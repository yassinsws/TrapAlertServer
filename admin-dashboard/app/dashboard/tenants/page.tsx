"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@/contexts/auth-context";
import { Building2, Key, Plus } from "lucide-react";
import { format } from "date-fns";

interface Tenant {
    id: number;
    name: string;
    company_name: string | null;
    api_key: string;
    is_active: boolean;
    created_at: string;
}

export default function TenantsPage() {
    const { token, user } = useAuth();
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newTenant, setNewTenant] = useState({ name: "", company_name: "" });

    useEffect(() => {
        fetchTenants();
    }, [token]);

    const fetchTenants = async () => {
        try {
            const response = await axios.get("/api/tenants", {
                headers: { Authorization: `Bearer ${token}` },
            });
            setTenants(response.data);
        } catch (error) {
            console.error("Error fetching tenants:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const createTenant = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await axios.post("/api/tenants", newTenant, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setShowCreateModal(false);
            setNewTenant({ name: "", company_name: "" });
            fetchTenants();
        } catch (error) {
            console.error("Error creating tenant:", error);
        }
    };

    if (user?.role !== "SUPER_ADMIN") {
        return (
            <div className="text-white">
                <p>Access denied. This page is only available to super admins.</p>
            </div>
        );
    }

    if (isLoading) {
        return <div className="text-white">Loading tenants...</div>;
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Tenants</h1>
                    <p className="text-gray-400">Manage client tenants and their API keys</p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 text-white font-semibold rounded-lg shadow-lg transition"
                >
                    <Plus className="w-5 h-5" />
                    Add Tenant
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tenants.map((tenant) => (
                    <div
                        key={tenant.id}
                        className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-purple-500/50 transition-all"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="p-3 rounded-lg bg-gradient-to-br from-purple-600 to-violet-600">
                                    <Building2 className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-white">{tenant.name}</h3>
                                    <p className="text-sm text-gray-400">{tenant.company_name || "No company name"}</p>
                                </div>
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${tenant.is_active ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"
                                }`}>
                                {tenant.is_active ? "Active" : "Inactive"}
                            </span>
                        </div>

                        <div className="space-y-3">
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <Key className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm font-medium text-gray-300">API Key</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <code className="text-xs bg-gray-700 px-2 py-1 rounded text-purple-300 font-mono flex-1 truncate">
                                        {tenant.api_key}
                                    </code>
                                    <button
                                        onClick={() => navigator.clipboard.writeText(tenant.api_key)}
                                        className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition"
                                    >
                                        Copy
                                    </button>
                                </div>
                            </div>

                            <div className="text-xs text-gray-400 pt-2 border-t border-gray-700">
                                Created {format(new Date(tenant.created_at), "MMM d, yyyy")}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Create Tenant Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md border border-gray-700">
                        <h2 className="text-xl font-bold text-white mb-4">Create New Tenant</h2>
                        <form onSubmit={createTenant} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Tenant Name
                                </label>
                                <input
                                    type="text"
                                    value={newTenant.name}
                                    onChange={(e) => setNewTenant({ ...newTenant, name: e.target.value })}
                                    required
                                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Company Name (Optional)
                                </label>
                                <input
                                    type="text"
                                    value={newTenant.company_name}
                                    onChange={(e) => setNewTenant({ ...newTenant, company_name: e.target.value })}
                                    className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <div className="flex gap-2 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 text-white rounded-lg transition"
                                >
                                    Create
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
