"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  ReactFlow,
  Background,
  Controls,
  MarkerType,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  type Node as FlowNode,
  type Edge as FlowEdge,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { getClaim, processClaim, type Claim } from "@/lib/api";
import { getStatusColor, getAgentLabel, formatDate, formatCurrency } from "@/lib/utils";
import {
  ArrowLeft, Play, RefreshCw, CheckCircle, XCircle, AlertTriangle,
  FileText, Search, DollarSign, Shield, FileCheck, Brain,
  Camera, UserCheck, BarChart3, GitPullRequest, ScrollText,
  Clock, Target, Fingerprint, Zap,
} from "lucide-react";

const pipelineOrder = ["intake", "validation", "assessment", "review_gate", "resolution"];

const agentDescriptions: Record<string, string> = {
  intake: "Extracts structured data from raw claim submission",
  validation: "Validates policy coverage and claimant identity",
  assessment: "Evaluates damage severity and estimates payout",
  review_gate: "Decides auto-approval vs human review",
  resolution: "Generates final resolution letter",
};

const agentIcons: Record<string, typeof Camera> = {
  intake: Camera,
  validation: UserCheck,
  assessment: BarChart3,
  review_gate: GitPullRequest,
  resolution: ScrollText,
};

const agentGradients: Record<string, string> = {
  intake: "from-blue-500 to-blue-600",
  validation: "from-emerald-500 to-emerald-600",
  assessment: "from-violet-500 to-violet-600",
  review_gate: "from-amber-500 to-amber-600",
  resolution: "from-rose-500 to-rose-600",
};

const agentGradientsLight: Record<string, string> = {
  intake: "from-blue-50 to-blue-100/50",
  validation: "from-emerald-50 to-emerald-100/50",
  assessment: "from-violet-50 to-violet-100/50",
  review_gate: "from-amber-50 to-amber-100/50",
  resolution: "from-rose-50 to-rose-100/50",
};

const agentBorderColors: Record<string, string> = {
  intake: "border-blue-200",
  validation: "border-emerald-200",
  assessment: "border-violet-200",
  review_gate: "border-amber-200",
  resolution: "border-rose-200",
};

function getMetricSummary(agent: string, claim: Claim): { label: string; value: string; icon: typeof Brain } | null {
  switch (agent) {
    case "intake": {
      const d = claim.intake_data as Record<string, unknown> | null;
      if (d?.claim_type) return { label: "Claim Type", value: String(d.claim_type).toUpperCase(), icon: FileText };
      return null;
    }
    case "validation": {
      const d = claim.validation_data as Record<string, unknown> | null;
      if (d?.policy_valid) return { label: "Policy", value: String(d.policy_valid) === "true" ? "Valid" : "Invalid", icon: Shield };
      return null;
    }
    case "assessment": {
      const d = claim.assessment_data as Record<string, unknown> | null;
      if (d?.estimated_payout) return { label: "Est. Payout", value: formatCurrency(Number(d.estimated_payout)), icon: DollarSign };
      return null;
    }
    case "review_gate": {
      const d = claim.review_gate_data as Record<string, unknown> | null;
      if (d?.needs_review !== undefined) return { label: "Review", value: String(d.needs_review) === "true" ? "Required" : "Auto", icon: Shield };
      return null;
    }
    case "resolution": {
      const d = claim.resolution_data as Record<string, unknown> | null;
      if (d?.outcome) return { label: "Outcome", value: String(d.outcome).charAt(0).toUpperCase() + String(d.outcome).slice(1), icon: FileCheck };
      return null;
    }
    default:
      return null;
  }
}

function PipelineNode({ data }: NodeProps) {
  const status = data.status as string;
  const isActive = data.isActive as boolean;
  const isCompleted = data.isCompleted as boolean;
  const agent = data.agent as string;
  const metric = data.metric as { label: string; value: string; icon: typeof Brain } | null;
  const confidence = data.confidence as number | null;
  const Icon = agentIcons[agent] || Brain;

  let containerClass = "relative rounded-2xl border-2 p-0 overflow-hidden shadow-sm min-w-[220px] transition-all duration-500";
  if (isCompleted) {
    containerClass += " border-emerald-300 bg-white shadow-md shadow-emerald-100/50";
  } else if (isActive) {
    containerClass += " border-blue-400 bg-white shadow-lg shadow-blue-100/50";
  } else {
    containerClass += " border-slate-200 bg-white";
  }

  return (
    <div className={containerClass}>
      <Handle type="target" position={Position.Left} className="!w-3 !h-3 !border-2 !border-white !bg-slate-300" />

      {/* Gradient header bar */}
      <div className={`h-2 w-full bg-gradient-to-r ${isCompleted ? agentGradients[agent] || "from-slate-400 to-slate-500" : isActive ? "from-blue-400 to-blue-500" : "from-slate-200 to-slate-300"}`} />

      <div className="p-4 pt-3">
        {/* Header row */}
        <div className="flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${
            isCompleted ? agentGradients[agent] || "from-slate-500 to-slate-600" : isActive ? "from-blue-500 to-blue-600" : "from-slate-300 to-slate-400"
          } text-white shadow-sm`}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className={`text-sm font-bold leading-tight ${isCompleted ? "text-emerald-800" : isActive ? "text-blue-800" : "text-slate-700"}`}>
              {getAgentLabel(agent)}
            </p>
            <p className="text-[11px] text-slate-400 leading-tight mt-0.5">{agentDescriptions[agent]}</p>
          </div>
          {isCompleted && (
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100">
              <CheckCircle className="h-3.5 w-3.5 text-emerald-600" />
            </div>
          )}
          {isActive && (
            <div className="flex h-6 w-6 items-center justify-center">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-blue-500" />
              </span>
            </div>
          )}
        </div>

        {/* Status badge */}
        {status && (
          <div className="mt-3">
            <span className={`inline-block rounded-md px-2.5 py-1 text-[11px] font-semibold leading-none ${
              isCompleted ? "bg-emerald-50 text-emerald-700" : isActive ? "bg-blue-50 text-blue-700" : "bg-slate-100 text-slate-500"
            }`}>
              {status === "completed" ? "Complete" : status === "pending" ? "Waiting" : status.replace(/_/g, " ")}
            </span>
          </div>
        )}

        {/* Metric summary */}
        {metric && (
          <div className="mt-3 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 border border-slate-100">
            <metric.icon className="h-4 w-4 text-slate-400" />
            <div className="min-w-0 flex-1">
              <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">{metric.label}</p>
              <p className="text-sm font-bold text-slate-900">{metric.value}</p>
            </div>
          </div>
        )}

        {/* Confidence bar */}
        {confidence !== null && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-[10px] text-slate-400">
              <span>Confidence</span>
              <span className="font-semibold">{Math.round(confidence * 100)}%</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-700"
                style={{ width: `${Math.round(confidence * 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Right} className="!w-3 !h-3 !border-2 !border-white !bg-slate-300" />
    </div>
  );
}

const nodeTypes = { pipelineNode: PipelineNode };

function ResultCard({ title, icon: Icon, color, data }: { title: string; icon: typeof Brain; color: string; data: Record<string, unknown> | null | undefined }) {
  if (!data) return null;
  const keys = Object.keys(data);

  return (
    <div className="group rounded-xl border border-slate-200 bg-white shadow-sm transition-all hover:shadow-md hover:border-slate-300 overflow-hidden">
      <div className={`h-1.5 w-full bg-gradient-to-r ${color}`} />
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br ${color} text-white shadow-sm`}>
            <Icon className="h-4 w-4" />
          </div>
          <h4 className="text-sm font-bold text-slate-800">{title}</h4>
        </div>
        <dl className="space-y-2">
          {keys.map((key) => {
            const val = data[key];
            const display = typeof val === "object" && val !== null ? JSON.stringify(val) : String(val ?? "—");
            return (
              <div key={key} className="flex items-start justify-between gap-2 text-xs">
                <dt className="text-slate-400 font-medium capitalize shrink-0 min-w-[100px]">{key.replace(/_/g, " ")}</dt>
                <dd className="text-slate-800 font-semibold text-right break-all">{display}</dd>
              </div>
            );
          })}
        </dl>
      </div>
    </div>
  );
}

export default function ClaimDetail() {
  const params = useParams();
  const claimId = Number(params.id);
  const [claim, setClaim] = useState<Claim | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);

  const loadClaim = useCallback(async () => {
    try {
      const data = await getClaim(claimId);
      setClaim(data);
      updatePipeline(data);
    } catch (e) {
      console.error("Failed to load claim", e);
    } finally {
      setLoading(false);
    }
  }, [claimId]);

  const updatePipeline = (claim: Claim) => {
    const currentIdx = pipelineOrder.indexOf(claim.current_agent);
    const isResolved = claim.status === "resolved";

    const newNodes: FlowNode[] = pipelineOrder.map((agent, idx) => {
      const isCompleted = isResolved || idx < currentIdx;
      const isActive = !isResolved && idx === currentIdx;

      let confidence: number | null = null;
      switch (agent) {
        case "intake":
          confidence = (claim.intake_data?.confidence as number) ?? null;
          break;
        case "validation":
          confidence = (claim.validation_data?.confidence as number) ?? null;
          break;
        case "assessment":
          confidence = (claim.assessment_data?.confidence as number) ?? null;
          break;
        case "review_gate":
          confidence = (claim.review_gate_data?.confidence as number) ?? null;
          break;
        case "resolution":
          confidence = (claim.resolution_data?.confidence as number) ?? null;
          break;
      }

      return {
        id: agent,
        type: "pipelineNode",
        position: { x: idx * 230, y: 0 },
        data: {
          agent,
          label: agent,
          status: idx === currentIdx ? claim.status : isCompleted ? "completed" : "pending",
          isActive,
          isCompleted,
          description: agentDescriptions[agent],
          metric: getMetricSummary(agent, claim),
          confidence,
        },
      };
    });

    const newEdges: FlowEdge[] = pipelineOrder.slice(0, -1).map((agent, idx) => {
      const nextAgent = pipelineOrder[idx + 1];
      const passed = isResolved || idx < currentIdx;
      const isCurrentEdge = idx === currentIdx - 1;

      return {
        id: `e-${agent}-${nextAgent}`,
        source: agent,
        target: nextAgent,
        type: "smoothstep",
        animated: isCurrentEdge && !isResolved,
        style: {
          stroke: passed ? "#10b981" : "#cbd5e1",
          strokeWidth: 3,
          strokeDasharray: passed ? "none" : "6 4",
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: passed ? "#10b981" : "#cbd5e1",
          width: 18,
          height: 18,
        },
      };
    });

    setNodes(newNodes);
    setEdges(newEdges);
  };

  useEffect(() => {
    loadClaim();
  }, [loadClaim]);

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const result = await processClaim(claimId);
      await loadClaim();
    } catch (e) {
      console.error("Processing failed", e);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-slate-400 animate-pulse">Loading claim data...</p>
        </div>
      </div>
    );
  }

  if (!claim) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-center">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-red-50">
          <XCircle className="h-8 w-8 text-red-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-700">Claim not found</h2>
        <p className="mt-1 text-sm text-slate-400">The claim you're looking for doesn't exist.</p>
        <a href="/" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Dashboard
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <a
            href="/"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-slate-700 transition-all shadow-sm"
          >
            <ArrowLeft className="h-4 w-4" />
          </a>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold tracking-tight text-slate-900">Claim #{claim.id}</h2>
              <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${getStatusColor(claim.status)}`}>
                <span className={`h-1.5 w-1.5 rounded-full ${claim.status === "resolved" ? "bg-emerald-500" : claim.status === "pending_review" ? "bg-orange-500" : "bg-blue-500"}`} />
                {claim.status.replace(/_/g, " ")}
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-0.5">
              {claim.claimant_name} &middot; {claim.claim_type.toUpperCase()} &middot; {formatDate(claim.created_at)}
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={loadClaim}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md"
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
          {(claim.status === "submitted" || claim.status === "intake_complete") && (
            <button
              onClick={handleProcess}
              disabled={processing}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:from-blue-700 hover:to-blue-800 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className={`h-4 w-4 ${processing ? "animate-pulse" : ""}`} />
              {processing ? "Processing..." : "Run Pipeline"}
            </button>
          )}
        </div>
      </div>

      {/* Pipeline Flow */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 text-white">
              <Zap className="h-4 w-4" />
            </div>
            <h3 className="text-base font-bold text-slate-900">AI Processing Pipeline</h3>
          </div>
          {claim.status === "resolved" && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 border border-emerald-200">
              <CheckCircle className="h-3.5 w-3.5" /> Pipeline Complete
            </span>
          )}
          {(claim.status === "submitted" || claim.status === "intake_complete") && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 border border-blue-200">
              <Clock className="h-3.5 w-3.5" /> Ready to Process
            </span>
          )}
        </div>
        <div className="h-[380px] lg:h-[420px] bg-gradient-to-b from-slate-50/50 to-white">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.4 }}
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable={false}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#e2e8f0" gap={24} size={1} />
            <Controls showInteractive={false} className="!rounded-xl !border !border-slate-200 !shadow-sm" />
          </ReactFlow>
        </div>
      </div>

      {/* Damage Photos Section */}
      {claim.image_paths && claim.image_paths.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-amber-500 to-rose-500" />
          <div className="p-6">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-amber-500 to-rose-500 text-white">
                <Camera className="h-4 w-4" />
              </div>
              <h3 className="text-base font-bold text-slate-900">Damage Photos</h3>
              {Number(claim.intake_data?.photos_analyzed) > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 text-xs font-semibold text-green-700 border border-green-200">
                  <CheckCircle className="h-3 w-3" /> {String(claim.intake_data?.photos_analyzed)} analyzed by AI
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {claim.image_paths.map((path, idx) => {
                const imgUrl = `http://localhost:8000${path}`;
                return (
                  <a
                    key={idx}
                    href={imgUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group relative aspect-square overflow-hidden rounded-xl border border-slate-200 bg-slate-100"
                  >
                    <img src={imgUrl} alt={`Damage photo ${idx + 1}`} className="h-full w-full object-cover transition-transform group-hover:scale-105" />
                    <div className="absolute inset-0 bg-black/0 transition-colors group-hover:bg-black/10" />
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                      <p className="text-xs font-medium text-white">Photo {idx + 1}</p>
                    </div>
                  </a>
                );
              })}
            </div>

            {/* Photo analysis results */}
            {!!claim.intake_data?.photo_analysis && Array.isArray(claim.intake_data.photo_analysis) && (
              <div className="mt-5 space-y-3">
                <h4 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Brain className="h-4 w-4 text-slate-400" /> AI Visual Analysis
                </h4>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {(claim.intake_data.photo_analysis as Record<string, unknown>[]).map((analysis, idx) => {
                      const a = analysis as Record<string, string | number | boolean | null>;
                      return (
                        <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                          <p className="text-xs font-medium text-slate-500 mb-2">Photo {idx + 1}: {String(a.filename ?? "")}</p>
                          <dl className="space-y-1.5 text-xs">
                            {!!a.damage_type && (
                              <div className="flex justify-between">
                                <dt className="text-slate-400">Damage</dt>
                                <dd className="font-semibold text-slate-800">{String(a.damage_type)}</dd>
                              </div>
                            )}
                            {!!a.damage_severity && (
                              <div className="flex justify-between">
                                <dt className="text-slate-400">Severity</dt>
                                <dd className="font-semibold text-slate-800">{String(a.damage_severity)}</dd>
                              </div>
                            )}
                            {!!a.estimated_repair_cost && (
                              <div className="flex justify-between">
                                <dt className="text-slate-400">Est. Repair</dt>
                                <dd className="font-semibold text-slate-800">${String(a.estimated_repair_cost)}</dd>
                              </div>
                            )}
                            {!!a.confidence && (
                              <div className="flex justify-between">
                                <dt className="text-slate-400">Confidence</dt>
                                <dd className="font-semibold text-slate-800">{Math.round(Number(a.confidence) * 100)}%</dd>
                              </div>
                            )}
                            {!!a.fraud_indicators && (
                              <div className="flex justify-between">
                                <dt className="text-slate-400">Fraud Flags</dt>
                                <dd className="font-semibold text-amber-600">{String(a.fraud_indicators)}</dd>
                              </div>
                            )}
                          </dl>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Details grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Claim Details */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-blue-500 to-purple-500" />
          <div className="p-6">
            <h3 className="mb-5 text-base font-bold text-slate-900">Claim Details</h3>
            <dl className="grid grid-cols-2 gap-x-8 gap-y-4 text-sm">
              <div>
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Claimant</dt>
                <dd className="mt-1 font-semibold text-slate-900">{claim.claimant_name}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Policy Number</dt>
                <dd className="mt-1 font-semibold text-slate-900 font-mono">{claim.policy_number}</dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Claim Type</dt>
                <dd className="mt-1">
                  <span className="inline-flex items-center rounded-lg bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 border border-blue-200 uppercase">
                    {claim.claim_type}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Incident Date</dt>
                <dd className="mt-1 font-semibold text-slate-900">{String(claim.intake_data?.incident_date ?? "—")}</dd>
              </div>
              {String(claim.intake_data?.location ?? "") && (
                <div className="col-span-2">
                  <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Location</dt>
                  <dd className="mt-1 font-semibold text-slate-900">{String(claim.intake_data?.location ?? "")}</dd>
                </div>
              )}
              <div className="col-span-2">
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">Description</dt>
                <dd className="mt-1 text-slate-700 leading-relaxed">{claim.description}</dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Status Panel */}
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-amber-400 to-rose-400" />
          <div className="p-6">
            <h3 className="mb-5 text-base font-bold text-slate-900">Processing Status</h3>
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Active Agent</span>
                <span className="inline-flex items-center gap-2 rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-semibold text-slate-800">
                  {(() => {
                    const Icon = agentIcons[claim.current_agent] || Brain;
                    return <Icon className="h-4 w-4 text-slate-500" />;
                  })()}
                  {getAgentLabel(claim.current_agent)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500">Pipeline Progress</span>
                <span className="text-sm font-bold text-slate-900">{Math.round(claim.pipeline_progress)}%</span>
              </div>
              <div className="relative h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500 transition-all duration-1000 ease-out"
                  style={{ width: `${claim.pipeline_progress}%` }}
                />
                <div
                  className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  style={{ width: `${claim.pipeline_progress}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Pipeline: 5 agents</span>
                <span>{Math.round(claim.pipeline_progress / 20)}/5</span>
              </div>

              <div className="pt-2 space-y-3">
                {claim.status === "pending_review" && (
                  <div className="rounded-xl bg-orange-50 border border-orange-200 p-4">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-100">
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-orange-800">Pending Human Review</p>
                        <p className="text-xs text-orange-600 mt-0.5">This claim has been flagged for manual review by a human operator.</p>
                      </div>
                    </div>
                    <a
                      href="/reviews"
                      className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-orange-600 px-3 py-2 text-xs font-semibold text-white hover:bg-orange-700 transition-colors"
                    >
                      Go to Review Dashboard
                    </a>
                  </div>
                )}
                {claim.status === "resolved" && (
                  <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100">
                        <CheckCircle className="h-4 w-4 text-emerald-600" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-emerald-800">Resolved</p>
                        <p className="text-xs text-emerald-600 mt-0.5">
                          {claim.resolution_data?.outcome === "approved"
                            ? `Approved — payout: ${formatCurrency(Number(claim.assessment_data?.estimated_payout ?? 0))}`
                            : "This claim has been fully processed."}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Results */}
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="h-1.5 w-full bg-gradient-to-r from-blue-500 via-purple-500 to-rose-500" />
        <div className="p-6">
          <div className="flex items-center gap-2.5 mb-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-slate-600 to-slate-700 text-white">
              <Brain className="h-4 w-4" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Agent Results</h3>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <ResultCard title="Intake" icon={Camera} color="from-blue-500 to-blue-600" data={claim.intake_data as Record<string, unknown> | null} />
            <ResultCard title="Validation" icon={UserCheck} color="from-emerald-500 to-emerald-600" data={claim.validation_data as Record<string, unknown> | null} />
            <ResultCard title="Assessment" icon={BarChart3} color="from-violet-500 to-violet-600" data={claim.assessment_data as Record<string, unknown> | null} />
            <ResultCard title="Review Gate" icon={GitPullRequest} color="from-amber-500 to-amber-600" data={claim.review_gate_data as Record<string, unknown> | null} />
            <ResultCard title="Resolution" icon={ScrollText} color="from-rose-500 to-rose-600" data={claim.resolution_data as Record<string, unknown> | null} />
          </div>
        </div>
      </div>
    </div>
  );
}
