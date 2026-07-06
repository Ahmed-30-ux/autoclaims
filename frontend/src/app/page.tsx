"use client";

import { useEffect, useState, useCallback } from "react";
import { listClaims, processClaim, type Claim } from "@/lib/api";
import { getStatusColor, getAgentIcon, getAgentLabel, formatDate } from "@/lib/utils";
import {
  RefreshCw, Plus, Play, FileText, DollarSign, Shield, Users,
  TrendingUp, Clock, CheckCircle2, AlertCircle, Activity, Zap, Camera,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

const COLORS = ["#3b82f6", "#8b5cf6", "#f59e0b", "#22c55e", "#ef4444", "#ec4899"];
const PIPELINE_AGENTS = ["intake", "validation", "assessment", "review_gate", "resolution"];

export default function Dashboard() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState("all");

  const loadClaims = useCallback(async () => {
    try {
      const data = await listClaims();
      setClaims(data.claims);
    } catch (e) {
      console.error("Failed to load claims", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadClaims();
  }, [loadClaims]);

  const handleProcess = async (id: number) => {
    setProcessing(id);
    try {
      await processClaim(id);
      await loadClaims();
    } catch (e) {
      console.error("Processing failed", e);
    } finally {
      setProcessing(null);
    }
  };

  const filtered = statusFilter === "all" ? claims : claims.filter(c => c.status === statusFilter);
  const pendingReview = claims.filter(c => c.status === "pending_review").length;
  const resolved = claims.filter(c => c.status === "resolved").length;
  const avgPayout = claims
    .filter(c => c.assessment_data?.estimated_payout)
    .reduce((a, c) => a + Number(c.assessment_data?.estimated_payout), 0) / Math.max(claims.filter(c => c.assessment_data?.estimated_payout).length, 1);

  const typeData = Object.entries(
    claims.reduce((acc, c) => {
      acc[c.claim_type] = (acc[c.claim_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  ).map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }));

  const agentData = PIPELINE_AGENTS.map(agent => ({
    name: getAgentLabel(agent),
    count: claims.filter(c => c.current_agent === agent || (c.status === "resolved" && PIPELINE_AGENTS.indexOf(agent) < PIPELINE_AGENTS.length)).length,
  }));

  const stats = [
    { label: "Total Claims", value: claims.length, icon: FileText, color: "from-blue-500 to-blue-600", bg: "bg-blue-50", text: "text-blue-600" },
    { label: "Pending Review", value: pendingReview, icon: Shield, color: "from-orange-500 to-orange-600", bg: "bg-orange-50", text: "text-orange-600" },
    { label: "Resolved", value: resolved, icon: CheckCircle2, color: "from-green-500 to-green-600", bg: "bg-green-50", text: "text-green-600" },
    { label: "Avg Payout", value: `$${Math.round(avgPayout).toLocaleString()}`, icon: DollarSign, color: "from-purple-500 to-purple-600", bg: "bg-purple-50", text: "text-purple-600" },
  ];

  return (
    <div className="page-enter space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 p-8 shadow-xl">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-40" />
        <div className="relative z-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-500/20 px-3 py-1 text-xs font-semibold text-blue-300 border border-blue-400/20">
                <Zap className="h-3 w-3" /> AI-Powered
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-semibold text-emerald-300 border border-emerald-400/20">
                <Activity className="h-3 w-3" /> 5-Agent Pipeline
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              AutoClaims Intelligence
            </h1>
            <p className="mt-3 text-base text-blue-200 leading-relaxed max-w-xl">
              An autonomous AI claims processing system powered by <strong className="text-white">Qwen Cloud</strong>.
              Submit a claim and watch 5 specialized AI agents — <strong className="text-white">Intake</strong>, <strong className="text-white">Validation</strong>, <strong className="text-white">Assessment</strong>, <strong className="text-white">Review Gate</strong>, and <strong className="text-white">Resolution</strong> — process it end-to-end with human oversight.
            </p>
            <div className="mt-4 flex flex-wrap gap-4 text-sm text-blue-300">
              <span className="flex items-center gap-1.5"><Camera className="h-4 w-4" /> Photo damage analysis</span>
              <span className="flex items-center gap-1.5"><Shield className="h-4 w-4" /> Policy validation</span>
              <span className="flex items-center gap-1.5"><DollarSign className="h-4 w-4" /> Payout estimation</span>
              <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> Human-in-the-loop</span>
            </div>
          </div>
          <div className="hidden sm:flex flex-col items-center gap-3">
            <a
              href="/new"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-sm font-bold text-slate-900 shadow-lg transition-all hover:bg-blue-50 hover:shadow-xl"
            >
              <Plus className="h-5 w-5" /> New Claim
            </a>
            <button
              onClick={loadClaims}
              className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-xs font-medium text-blue-200 hover:bg-white/20 transition-all backdrop-blur-sm"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label} className="group relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">{s.label}</p>
                <p className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">{s.value}</p>
              </div>
              <div className={`rounded-xl p-3 ${s.bg} transition-transform group-hover:scale-110`}>
                <s.icon className={`h-5 w-5 ${s.text}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
            <h3 className="font-semibold text-slate-900">Claims Overview</h3>
            <div className="flex gap-1.5">
              {["all", "submitted", "pending_review", "resolved"].map((s) => (
                <button
                  key={s}
                  onClick={() => setStatusFilter(s)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                    statusFilter === s ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {s === "all" ? "All" : s.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-24">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 text-center">
              <FileText className="mb-3 h-10 w-10 text-slate-300" />
              <h3 className="font-semibold text-slate-700">No claims yet</h3>
              <p className="mt-1 text-sm text-slate-500">Submit your first claim to see it here.</p>
              <a href="/new" className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700">
                <Plus className="h-4 w-4" /> Submit Claim
              </a>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filtered.map((claim) => (
                <div key={claim.id} className="flex items-center gap-4 px-6 py-4 transition-colors hover:bg-slate-50">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${claim.status === "resolved" ? "bg-green-100" : claim.status === "pending_review" ? "bg-orange-100" : "bg-blue-100"}`}>
                    <span className="text-lg">{getAgentIcon(claim.current_agent)}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <a href={`/claim/${claim.id}`} className="font-medium text-slate-900 hover:text-blue-600 transition-colors">{claim.claimant_name}</a>
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500 uppercase">{claim.claim_type}</span>
                    </div>
                    <p className="mt-0.5 truncate text-sm text-slate-500">{claim.description}</p>
                  </div>
                  <div className="hidden items-center gap-3 md:flex">
                    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${getStatusColor(claim.status)}`}>
                      <span className={`h-1.5 w-1.5 rounded-full ${claim.status === "resolved" ? "bg-green-500" : claim.status === "pending_review" ? "bg-orange-500" : "bg-blue-500"}`} />
                      {claim.status.replace(/_/g, " ")}
                    </span>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400">
                      <Clock className="h-3.5 w-3.5" />
                      {formatDate(claim.created_at)}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <a href={`/claim/${claim.id}`} className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50">
                      View
                    </a>
                    {(claim.status === "submitted" || claim.status === "intake_complete") && (
                      <button
                        onClick={() => handleProcess(claim.id)}
                        disabled={processing === claim.id}
                        className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                      >
                        <Play className={`h-3 w-3 ${processing === claim.id ? "animate-pulse" : ""}`} />
                        {processing === claim.id ? "..." : "Process"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          {typeData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h4 className="mb-3 text-sm font-semibold text-slate-700">Claims by Type</h4>
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={typeData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                      {typeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 space-y-1.5">
                {typeData.map((d, i) => (
                  <div key={d.name} className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-slate-600">
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                      {d.name}
                    </span>
                    <span className="font-medium text-slate-900">{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h4 className="mb-3 text-sm font-semibold text-slate-700">Pipeline Activity</h4>
            <div className="space-y-2.5">
              {PIPELINE_AGENTS.map((agent, i) => {
                const count = claims.filter(c => c.current_agent === agent || (c.status === "resolved" && i < PIPELINE_AGENTS.length)).length;
                const max = Math.max(1, claims.length);
                return (
                  <div key={agent} className="flex items-center gap-3">
                    <span className="w-20 text-xs text-slate-500">{getAgentLabel(agent)}</span>
                    <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all" style={{ width: `${(count / max) * 100}%` }} />
                    </div>
                    <span className="w-6 text-right text-xs font-medium text-slate-600">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
