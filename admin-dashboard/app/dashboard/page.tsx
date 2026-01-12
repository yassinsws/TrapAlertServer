"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@/contexts/auth-context";
import { FileText, Users, CheckCircle, TrendingUp } from "lucide-react";

interface Stats {
    total_reports: number;
    active_tenants: number;
    resolved_this_week: number;
    avg_struggle_score: number;
}

export default function DashboardPage() {
    const { token } = useAuth();
    const [stats, setStats] = useState<Stats | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get("/api/reports/stats", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setStats(response.data);
            } catch (error: any) {
                console.error("Error fetching stats:", error);
                if (error.response?.status === 401) {
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
            } finally {
                setIsLoading(false);
            }
        };

        if (token) {
            fetchStats();
        }
    }, [token]);

    if (isLoading) {
        return <div className="text-white">Loading statistics...</div>;
    }

    const statCards = [
        {
            name: "Total Reports",
            value: stats?.total_reports || 0,
            icon: FileText,
            color: "from-blue-500 to-cyan-500",
        },
        {
            name: "Active Tenants",
            value: stats?.active_tenants || 0,
            icon: Users,
            color: "from-purple-500 to-pink-500",
        },
        {
            name: "Resolved This Week",
            value: stats?.resolved_this_week || 0,
            icon: CheckCircle,
            color: "from-green-500 to-emerald-500",
        },
        {
            name: "Avg Struggle Score",
            value: stats?.avg_struggle_score?.toFixed(1) || "0.0",
            icon: TrendingUp,
            color: "from-orange-500 to-red-500",
        },
    ];

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
                <p className="text-gray-400">Welcome to TrapAlert Admin Dashboard</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {statCards.map((stat) => {
                    const Icon = stat.icon;
                    return (
                        <div
                            key={stat.name}
                            className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all hover:shadow-xl"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.color}`}>
                                    <Icon className="w-6 h-6 text-white" />
                                </div>
                            </div>
                            <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                            <div className="text-sm text-gray-400">{stat.name}</div>
                        </div>
                    );
                })}
            </div>

            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a
                        href="/dashboard/reports"
                        className="p-4 bg-gradient-to-br from-purple-600/20 to-violet-600/20 border border-purple-500/30 rounded-lg hover:from-purple-600/30 hover:to-violet-600/30 transition-all"
                    >
                        <h3 className="font-semibold text-white mb-1">View All Reports</h3>
                        <p className="text-sm text-gray-400">Browse and manage bug reports</p>
                    </a>
                    <a
                        href="/dashboard/tenants"
                        className="p-4 bg-gradient-to-br from-blue-600/20 to-cyan-600/20 border border-blue-500/30 rounded-lg hover:from-blue-600/30 hover:to-cyan-600/30 transition-all"
                    >
                        <h3 className="font-semibold text-white mb-1">Manage Tenants</h3>
                        <p className="text-sm text-gray-400">Add and configure client tenants</p>
                    </a>
                    <a
                        href="/dashboard/integrations"
                        className="p-4 bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-lg hover:from-green-600/30 hover:to-emerald-600/30 transition-all"
                    >
                        <h3 className="font-semibold text-white mb-1">Setup Integrations</h3>
                        <p className="text-sm text-gray-400">Connect Jira, ClickUp, and more</p>
                    </a>
                </div>
            </div>
        </div>
    );
}
