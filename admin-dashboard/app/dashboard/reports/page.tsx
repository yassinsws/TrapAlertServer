"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@/contexts/auth-context";
import { format } from "date-fns";
import { FileText, Clock, AlertCircle, CheckCircle2, XCircle } from "lucide-react";

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
}

interface ReportsResponse {
    total: number;
    page: number;
    page_size: number;
    reports: BugReport[];
}

export default function ReportsPage() {
    const { token, user } = useAuth();
    const [reports, setReports] = useState<BugReport[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const response = await axios.get<ReportsResponse>("/api/reports", {
                    headers: { Authorization: `Bearer ${token}` },
                    params: { page, page_size: 10 },
                });
                setReports(response.data.reports);
                setTotal(response.data.total);
            } catch (error: any) {
                console.error("Error fetching reports:", error);
                if (error.response?.status === 401) {
                    // Token is invalid or expired
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
            } finally {
                setIsLoading(false);
            }
        };

        if (token) {
            fetchReports();
        }
    }, [token, page]);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "NEW":
                return <FileText className="w-4 h-4" />;
            case "IN_PROGRESS":
                return <Clock className="w-4 h-4" />;
            case "RESOLVED":
                return <CheckCircle2 className="w-4 h-4" />;
            case "CLOSED":
                return <XCircle className="w-4 h-4" />;
            default:
                return <AlertCircle className="w-4 h-4" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "NEW":
                return "bg-blue-500/20 text-blue-400 border-blue-500/30";
            case "IN_PROGRESS":
                return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
            case "RESOLVED":
                return "bg-green-500/20 text-green-400 border-green-500/30";
            case "CLOSED":
                return "bg-gray-500/20 text-gray-400 border-gray-500/30";
            default:
                return "bg-purple-500/20 text-purple-400 border-purple-500/30";
        }
    };

    if (isLoading) {
        return <div className="text-white">Loading reports...</div>;
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Bug Reports</h1>
                <p className="text-gray-400">View and manage all bug reports from your tenants</p>
            </div>

            <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-700/50 border-b border-gray-700">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    Description
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    Labels
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    Struggle Score
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                                    Created
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                            {reports.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-8 text-center text-gray-400">
                                        No reports found
                                    </td>
                                </tr>
                            ) : (
                                reports.map((report) => (
                                    <tr
                                        key={report.id}
                                        className="hover:bg-gray-700/30 transition-colors cursor-pointer"
                                        onClick={() => window.open(`/dashboard/reports/${report.id}`, '_blank')}
                                    >
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-white font-medium">
                                            #{report.id}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">
                                            {report.description || "No description"}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex gap-1 flex-wrap">
                                                {report.label?.slice(0, 3).map((label, idx) => (
                                                    <span
                                                        key={idx}
                                                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-500/20 text-purple-300"
                                                    >
                                                        {label}
                                                    </span>
                                                ))}
                                                {report.label?.length > 3 && (
                                                    <span className="text-xs text-gray-400">
                                                        +{report.label.length - 3} more
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {report.struggle_score !== null ? (
                                                <span className={`font-semibold ${report.struggle_score >= 75
                                                    ? "text-red-400"
                                                    : report.struggle_score >= 50
                                                        ? "text-yellow-400"
                                                        : "text-green-400"
                                                    }`}>
                                                    {report.struggle_score.toFixed(0)}
                                                </span>
                                            ) : (
                                                <span className="text-gray-500">-</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border ${getStatusColor(report.status)}`}>
                                                {getStatusIcon(report.status)}
                                                {report.status.replace("_", " ")}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                            {format(new Date(report.created_at), "MMM d, yyyy")}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {total > 10 && (
                    <div className="px-6 py-4 border-t border-gray-700 flex items-center justify-between">
                        <p className="text-sm text-gray-400">
                            Showing {Math.min((page - 1) * 10 + 1, total)} to {Math.min(page * 10, total)} of {total} reports
                        </p>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                            >
                                Previous
                            </button>
                            <button
                                onClick={() => setPage(p => p + 1)}
                                disabled={page * 10 >= total}
                                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
                            >
                                Next
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
