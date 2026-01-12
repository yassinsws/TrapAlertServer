"use client";

import { useEffect, useState, use } from "react";
import axios from "axios";
import { useAuth } from "@/contexts/auth-context";
import { format } from "date-fns";
import {
    ArrowLeft,
    Clock,
    FileText,
    AlertCircle,
    CheckCircle2,
    XCircle,
    Download,
    Maximize2,
    Calendar,
    Tag,
    User as UserIcon,
    Code,
    Activity,
    Trash2,
    Edit2,
    Save,
    X,
    Loader2
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface BugReport {
    id: number;
    tenant_id: number;
    description: string | null;
    label: string[];
    struggle_score: number | null;
    status: string;
    synced_to_integration: boolean;
    external_ticket_id: string | null;
    created_at: string;
    metadata_json: string;
    dom_snapshot: string;
}

export default function ReportDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const { token } = useAuth();
    const router = useRouter();
    const [report, setReport] = useState<BugReport | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isUpdating, setIsUpdating] = useState(false);
    const [videoUrl, setVideoUrl] = useState<string | null>(null);

    // Edit Mode State
    const [isEditing, setIsEditing] = useState(false);
    const [editForm, setEditForm] = useState({ description: "", label: "" });
    const [isSaving, setIsSaving] = useState(false);

    // Delete State
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        const fetchReport = async () => {
            try {
                const response = await axios.get<BugReport>(`/api/reports/${id}`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setReport(response.data);
                setEditForm({
                    description: response.data.description || "",
                    label: response.data.label.join(", ")
                });

                // Fetch video as blob
                try {
                    const videoResponse = await axios.get(`/api/reports/${id}/video`, {
                        headers: { Authorization: `Bearer ${token}` },
                        responseType: 'blob'
                    });
                    const url = URL.createObjectURL(videoResponse.data);
                    setVideoUrl(url);
                } catch (vError) {
                    console.error("No video or access error:", vError);
                }
            } catch (error: any) {
                console.error("Error fetching report:", error);
                if (error.response?.status === 401) {
                    window.location.href = '/login';
                }
            } finally {
                setIsLoading(false);
            }
        };

        if (token) {
            fetchReport();
        }

        return () => {
            if (videoUrl) {
                URL.revokeObjectURL(videoUrl);
            }
        };
    }, [token, id]);

    const updateStatus = async (newStatus: string) => {
        setIsUpdating(true);
        try {
            await axios.put(`/api/reports/${id}/status`, { status: newStatus }, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setReport(prev => prev ? { ...prev, status: newStatus } : null);
        } catch (error) {
            console.error("Error updating status:", error);
        } finally {
            setIsUpdating(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const labels = editForm.label.split(",").map(s => s.trim()).filter(Boolean);
            const response = await axios.put(`/api/reports/${id}`, {
                description: editForm.description,
                label: labels
            }, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setReport(response.data);
            setIsEditing(false);
        } catch (error) {
            console.error("Failed to save report:", error);
            alert("Failed to save changes.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async () => {
        setIsDeleting(true);
        try {
            await axios.delete(`/api/reports/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            router.push("/dashboard/reports");
        } catch (error) {
            console.error("Failed to delete report:", error);
            alert("Failed to delete report.");
            setIsDeleting(false);
        }
    };

    if (isLoading) {
        return <div className="text-white">Loading report details...</div>;
    }

    if (!report) {
        return (
            <div className="text-white text-center py-12">
                <h2 className="text-2xl font-bold mb-4">Report not found</h2>
                <Link href="/dashboard/reports" className="text-purple-400 hover:underline">
                    Back to reports
                </Link>
            </div>
        );
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "NEW": return <FileText className="w-5 h-5" />;
            case "IN_PROGRESS": return <Clock className="w-5 h-5" />;
            case "RESOLVED": return <CheckCircle2 className="w-5 h-5" />;
            case "CLOSED": return <XCircle className="w-5 h-5" />;
            default: return <AlertCircle className="w-5 h-5" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "NEW": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
            case "IN_PROGRESS": return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
            case "RESOLVED": return "bg-green-500/20 text-green-400 border-green-500/30";
            case "CLOSED": return "bg-gray-500/20 text-gray-400 border-gray-500/30";
            default: return "bg-purple-500/20 text-purple-400 border-purple-500/30";
        }
    };

    const parsedMetadata = JSON.parse(report.metadata_json || '{}');

    return (
        <div className="max-w-6xl mx-auto pb-12">
            <div className="mb-6 flex items-center justify-between">
                <Link
                    href="/dashboard/reports"
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Reports
                </Link>

                <div className="flex gap-2">
                    {["NEW", "IN_PROGRESS", "RESOLVED", "CLOSED"].map((s) => (
                        <button
                            key={s}
                            onClick={() => updateStatus(s)}
                            disabled={isUpdating || report.status === s}
                            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${report.status === s
                                ? getStatusColor(s)
                                : "bg-gray-800 text-gray-400 border-gray-700 hover:border-gray-600"
                                } disabled:opacity-50`}
                        >
                            {s.replace('_', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Report Summary & Video */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden shadow-xl">
                        <div className="p-6 border-b border-gray-700 bg-gray-700/30 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className={`p-3 rounded-xl bg-gradient-to-br ${report.struggle_score && report.struggle_score > 70
                                    ? "from-red-500 to-orange-600"
                                    : "from-purple-500 to-violet-600"
                                    }`}>
                                    {getStatusIcon(report.status)}
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-white">Report #{report.id}</h1>
                                    <p className="text-gray-400 text-sm">
                                        Submitted on {format(new Date(report.created_at), "MMMM d, yyyy 'at' h:mm a")}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right flex items-center gap-2">
                                <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold ring-1 ring-inset ${getStatusColor(report.status)}`}>
                                    {report.status.replace('_', ' ')}
                                </span>

                                {isEditing ? (
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setIsEditing(false)}
                                            className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
                                            title="Cancel Editing"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={handleSave}
                                            disabled={isSaving}
                                            className="p-2 rounded-lg bg-green-600 hover:bg-green-700 text-white transition-colors"
                                            title="Save Changes"
                                        >
                                            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                        </button>
                                    </div>
                                ) : (
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setIsEditing(true)}
                                            className="p-2 rounded-lg hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
                                            title="Edit Report"
                                        >
                                            <Edit2 className="w-4 h-4" />
                                        </button>
                                        <button
                                            onClick={() => setShowDeleteConfirm(true)}
                                            className="p-2 rounded-lg hover:bg-red-900/30 text-gray-400 hover:text-red-400 transition-colors"
                                            title="Delete Report"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="p-8">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-purple-400" />
                                Description / Transcript
                            </h2>
                            <div className="bg-gray-900/50 rounded-xl p-6 text-gray-300 leading-relaxed border border-gray-700/50 italic">
                                {isEditing ? (
                                    <textarea
                                        value={editForm.description}
                                        onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                                        className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none min-h-[100px]"
                                        placeholder="Enter description..."
                                    />
                                ) : (
                                    `"${report.description || "No description provided."}"`
                                )}
                            </div>
                        </div>

                        {/* Video Player Section */}
                        <div className="p-8 border-t border-gray-700">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2 text-blue-400">
                                📹 Session Recording
                            </h2>
                            <div className="aspect-video bg-black rounded-xl overflow-hidden relative group border border-gray-700">
                                {videoUrl ? (
                                    <video
                                        className="w-full h-full object-contain"
                                        controls
                                        src={videoUrl}
                                    >
                                        Your browser does not support the video tag.
                                    </video>
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                                        <div className="p-4 rounded-full bg-gray-800">
                                            <AlertCircle className="w-12 h-12" />
                                        </div>
                                        <p>No video session recorded or still processing.</p>
                                    </div>
                                )}
                                <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    {videoUrl && (
                                        <a
                                            href={videoUrl}
                                            download={`report_${id}.mp4`}
                                            className="p-2 bg-gray-900/80 rounded-lg text-white hover:bg-gray-800 border border-gray-700"
                                            title="Download Video"
                                        >
                                            <Download className="w-5 h-5" />
                                        </a>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Metadata Grid */}
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 p-8 shadow-xl">
                        <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2 border-b border-gray-700 pb-4">
                            <Code className="w-5 h-5 text-green-400" />
                            Technical Metadata
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {Object.entries(parsedMetadata).map(([key, value]) => (
                                <div key={key} className="bg-gray-900/30 p-4 rounded-xl border border-gray-700/30">
                                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">{key.replace(/([A-Z])/g, ' $1')}</p>
                                    <p className="text-sm text-gray-200 font-mono break-all">{String(value)}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Sidebar Stats */}
                <div className="space-y-8">
                    {/* Struggle Score Card */}
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6 text-center shadow-xl">
                        <p className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-widest">Struggle Score</p>
                        <div className={`text-6xl font-black mb-2 ${(report.struggle_score || 0) > 75 ? "text-red-500" : (report.struggle_score || 0) > 40 ? "text-yellow-500" : "text-green-500"
                            }`}>
                            {report.struggle_score?.toFixed(0) || "0"}
                        </div>
                        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden mb-4">
                            <div
                                className={`h-full ring-2 ring-inset ${(report.struggle_score || 0) > 75 ? "bg-red-500" : (report.struggle_score || 0) > 40 ? "bg-yellow-500" : "bg-green-500"
                                    }`}
                                style={{ width: `${report.struggle_score}%` }}
                            />
                        </div>
                        <p className="text-xs text-gray-400">
                            {(report.struggle_score || 0) > 75
                                ? "Critical frustration detected!"
                                : (report.struggle_score || 0) > 40
                                    ? "Moderate struggle observed."
                                    : "Smooth user experience."
                            }
                        </p>
                    </div>

                    {/* Labels Card */}
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6 shadow-xl">
                        <h3 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-widest flex items-center gap-2">
                            <Tag className="w-4 h-4" />
                            AI Labels
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {isEditing ? (
                                <input
                                    type="text"
                                    value={editForm.label}
                                    onChange={(e) => setEditForm(prev => ({ ...prev, label: e.target.value }))}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg p-2 text-sm text-white focus:ring-2 focus:ring-purple-500 outline-none"
                                    placeholder="Enter labels separated by commas..."
                                />
                            ) : (
                                report.label.map((l, i) => (
                                    <span key={i} className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold">
                                        {l}
                                    </span>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Actions Card */}
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6 shadow-xl">
                        <h3 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-widest">Quick Actions</h3>
                        <div className="space-y-3">
                            <button
                                onClick={() => {
                                    const blob = new Blob([report.dom_snapshot], { type: 'text/html' });
                                    const url = URL.createObjectURL(blob);
                                    window.open(url, '_blank');
                                }}
                                className="w-full flex items-center justify-between px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-xl text-sm font-medium transition-all group"
                            >
                                <span className="flex items-center gap-2">
                                    <Code className="w-4 h-4 text-orange-400" />
                                    View DOM Snapshot
                                </span>
                                <Maximize2 className="w-4 h-4 text-gray-500 group-hover:text-white" />
                            </button>

                            <button
                                className="w-full flex items-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl text-sm font-bold text-white transition-all shadow-lg shadow-blue-900/20"
                                onClick={() => alert("External Ticket Sync implementation coming soon!")}
                            >
                                {report.synced_to_integration ? "Already Synced" : "Sync to Jira/ClickUp"}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
                    <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6 max-w-sm w-full shadow-2xl animate-in fade-in zoom-in duration-200">
                        <div className="flex items-center gap-4 mb-4 text-red-400">
                            <div className="p-3 bg-red-500/10 rounded-full">
                                <Trash2 className="w-8 h-8" />
                            </div>
                            <h3 className="text-xl font-bold text-white">Delete Report?</h3>
                        </div>
                        <p className="text-gray-400 mb-6">
                            Are you sure you want to delete Report #{report.id}? This action cannot be undone and the video data will be lost forever.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                disabled={isDeleting}
                                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-xl text-white font-medium transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDelete}
                                disabled={isDeleting}
                                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-xl text-white font-bold transition-colors flex items-center justify-center gap-2"
                            >
                                {isDeleting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Delete"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
