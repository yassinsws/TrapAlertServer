"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@/contexts/auth-context";
import { Settings, Plus, Check, X } from "lucide-react";

interface Integration {
    id: number;
    tenant_id: number;
    integration_type: string;
    config_json: any;
    enabled: boolean;
    created_at: string;
}

const AVAILABLE_INTEGRATIONS = [
    {
        type: "JIRA",
        name: "Jira",
        description: "Sync bug reports to Jira issues",
        icon: "🎯",
        color: "from-blue-600 to-blue-800",
    },
    {
        type: "CLICKUP",
        name: "ClickUp",
        description: "Create ClickUp tasks from reports",
        icon: "✅",
        color: "from-purple-600 to-pink-600",
    },
    {
        type: "LINEAR",
        name: "Linear",
        description: "Track issues in Linear",
        icon: "📊",
        color: "from-gray-600 to-gray-800",
    },
];

export default function IntegrationsPage() {
    const { token, user } = useAuth();
    const [integrations, setIntegrations] = useState<Integration[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchIntegrations();
    }, [token]);

    const fetchIntegrations = async () => {
        try {
            const response = await axios.get("/api/integrations", {
                headers: { Authorization: `Bearer ${token}` },
            });
            setIntegrations(response.data);
        } catch (error) {
            console.error("Error fetching integrations:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const hasIntegration = (type: string) => {
        return integrations.some((i) => i.integration_type === type);
    };

    if (user?.role === "CLIENT_USER") {
        return (
            <div className="text-white">
                <p>Access denied. This page is only available to admins.</p>
            </div>
        );
    }

    if (isLoading) {
        return <div className="text-white">Loading integrations...</div>;
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Integrations</h1>
                <p className="text-gray-400">Connect TrapAlert with your project management tools</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {AVAILABLE_INTEGRATIONS.map((integration) => {
                    const isConnected = hasIntegration(integration.type);
                    return (
                        <div
                            key={integration.type}
                            className={`bg-gray-800 rounded-xl p-6 border ${isConnected ? "border-green-500/50" : "border-gray-700"
                                } hover:border-purple-500/50 transition-all`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`text-4xl p-3 rounded-lg bg-gradient-to-br ${integration.color}`}>
                                    {integration.icon}
                                </div>
                                {isConnected && (
                                    <span className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
                                        <Check className="w-3 h-3" />
                                        Connected
                                    </span>
                                )}
                            </div>

                            <h3 className="text-xl font-bold text-white mb-2">{integration.name}</h3>
                            <p className="text-sm text-gray-400 mb-4">{integration.description}</p>

                            <button
                                className={`w-full px-4 py-2 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${isConnected
                                        ? "bg-gray-700 hover:bg-gray-600 text-gray-300"
                                        : "bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700 text-white"
                                    }`}
                                onClick={() => {
                                    if (!isConnected) {
                                        alert(`${integration.name} configuration coming soon! This will initiate OAuth flow.`);
                                    }
                                }}
                            >
                                {isConnected ? (
                                    <>
                                        <Settings className="w-4 h-4" />
                                        Configure
                                    </>
                                ) : (
                                    <>
                                        <Plus className="w-4 h-4" />
                                        Connect
                                    </>
                                )}
                            </button>
                        </div>
                    );
                })}
            </div>

            {integrations.length > 0 && (
                <div className="mt-8">
                    <h2 className="text-xl font-bold text-white mb-4">Active Integrations</h2>
                    <div className="bg-gray-800 rounded-xl border border-gray-700 divide-y divide-gray-700">
                        {integrations.map((integration) => (
                            <div key={integration.id} className="p-4 flex items-center justify-between">
                                <div>
                                    <h4 className="font-semibold text-white">{integration.integration_type}</h4>
                                    <p className="text-sm text-gray-400">Tenant ID: {integration.tenant_id}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition"
                                        onClick={async () => {
                                            try {
                                                await axios.post(`/api/integrations/${integration.id}/test`, {}, {
                                                    headers: { Authorization: `Bearer ${token}` },
                                                });
                                                alert("Integration test successful!");
                                            } catch (error) {
                                                alert("Integration test failed");
                                            }
                                        }}
                                    >
                                        Test
                                    </button>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${integration.enabled ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"
                                        }`}>
                                        {integration.enabled ? "Enabled" : "Disabled"}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
