"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/auth-context";
import { LayoutDashboard, Users, Building2, Settings, LogOut, FileText } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const { user, logout, isLoading } = useAuth();

    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login");
        }
    }, [user, isLoading, router]);

    if (isLoading || !user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-900">
                <div className="text-white text-xl">Loading...</div>
            </div>
        );
    }

    const navigation = [
        { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { name: "Reports", href: "/dashboard/reports", icon: FileText },
        ...(user.role === "SUPER_ADMIN" ? [
            { name: "Tenants", href: "/dashboard/tenants", icon: Building2 },
        ] : []),
        ...(user.role !== "CLIENT_USER" ? [
            { name: "Users", href: "/dashboard/users", icon: Users },
            { name: "Integrations", href: "/dashboard/integrations", icon: Settings },
        ] : []),
    ];

    return (
        <div className="min-h-screen bg-gray-900">
            {/* Sidebar */}
            <div className="fixed inset-y-0 left-0 w-64 bg-gray-800 border-r border-gray-700">
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="flex items-center justify-center h-16 border-b border-gray-700 bg-gradient-to-r from-purple-600 to-violet-600">
                        <h1 className="text-xl font-bold text-white">TrapAlert</h1>
                    </div>

                    {/* User Info */}
                    <div className="px-4 py-4 border-b border-gray-700">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white font-semibold">
                                {user.email[0].toUpperCase()}
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white truncate">{user.email}</p>
                                <p className="text-xs text-gray-400">{user.role.replace('_', ' ')}</p>
                            </div>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className="flex items-center gap-3 px-3 py-2 text-gray-300 rounded-lg hover:bg-gray-700 hover:text-white transition-colors group"
                                >
                                    <Icon className="w-5 h-5" />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Logout */}
                    <div className="px-4 py-4 border-t border-gray-700">
                        <button
                            onClick={logout}
                            className="flex items-center gap-3 px-3 py-2 text-gray-300 rounded-lg hover:bg-red-600/20 hover:text-red-400 transition-colors w-full"
                        >
                            <LogOut className="w-5 h-5" />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="pl-64">
                <div className="container mx-auto px-6 py-8">
                    {children}
                </div>
            </div>
        </div>
    );
}
