"use client";

import { useEffect, useState, useCallback } from "react";
import { getPendingReviews, resolveHumanReview } from "@/lib/api";
import { Shield, CheckCircle, XCircle, RefreshCw, ExternalLink } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface Review {
  id: number;
  claim_id: number;
  status: string;
  claimant_name: string;
  claim_type: string;
  claim_status: string;
  assessment_data: string | null;
  created_at: string;
}

export default function Reviews() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState<number | null>(null);
  const [reviewNotes, setReviewNotes] = useState<Record<number, string>>({});

  const loadReviews = useCallback(async () => {
    try {
      const data = await getPendingReviews();
      setReviews(data.reviews as Review[]);
    } catch (e) {
      console.error("Failed to load reviews", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  const handleResolve = async (reviewId: number, claimId: number, status: string) => {
    setResolving(reviewId);
    try {
      await resolveHumanReview(claimId, {
        review_id: reviewId,
        status,
        notes: reviewNotes[reviewId] || "",
        reviewer: "human_operator",
        reviewed_at: new Date().toISOString(),
      });
      await loadReviews();
    } catch (e) {
      console.error("Failed to resolve review", e);
    } finally {
      setResolving(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Human Reviews</h2>
          <p className="text-slate-500">Claims flagged for manual review and decision.</p>
        </div>
        <button
          onClick={loadReviews}
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </div>

      {reviews.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white py-20 text-center">
          <Shield className="mb-4 h-12 w-12 text-green-400" />
          <h3 className="text-lg font-semibold text-slate-700">No pending reviews</h3>
          <p className="mt-1 text-sm text-slate-500">All claims have been processed automatically.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => {
            let assessment = null;
            try {
              assessment = review.assessment_data ? JSON.parse(review.assessment_data) : null;
            } catch {}
            return (
              <div key={review.id} className="rounded-xl border border-slate-200 bg-white p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="rounded-lg bg-orange-100 p-3">
                      <Shield className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900">{review.claimant_name}</h3>
                      <p className="text-sm text-slate-500">
                        Claim #{review.claim_id} &middot; {review.claim_type.toUpperCase()} &middot; {formatDate(review.created_at)}
                      </p>
                    </div>
                  </div>
                  <a
                    href={`/claim/${review.claim_id}`}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                  >
                    <ExternalLink className="h-3.5 w-3.5" /> View
                  </a>
                </div>

                {assessment && (
                  <div className="mt-4 grid grid-cols-3 gap-4 rounded-lg bg-slate-50 p-4">
                    {assessment.estimated_payout && (
                      <div>
                        <span className="text-xs text-slate-500">Est. Payout</span>
                        <p className="font-semibold text-slate-900">${assessment.estimated_payout?.toLocaleString()}</p>
                      </div>
                    )}
                    {assessment.severity && (
                      <div>
                        <span className="text-xs text-slate-500">Severity</span>
                        <p className="font-semibold text-slate-900 capitalize">{assessment.severity}</p>
                      </div>
                    )}
                    {assessment.fraud_risk_score !== undefined && (
                      <div>
                        <span className="text-xs text-slate-500">Fraud Risk</span>
                        <p className={`font-semibold ${assessment.fraud_risk_score > 0.7 ? "text-red-600" : "text-green-600"}`}>
                          {(assessment.fraud_risk_score * 100).toFixed(0)}%
                        </p>
                      </div>
                    )}
                    {assessment.fraud_risk_factors && assessment.fraud_risk_factors.length > 0 && (
                      <div className="col-span-3">
                        <span className="text-xs text-slate-500">Flags</span>
                        <div className="mt-1 flex flex-wrap gap-2">
                          {(assessment.fraud_risk_factors as string[]).map((f: string, i: number) => (
                            <span key={i} className="rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-700">
                              {f}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="mt-4">
                  <textarea
                    placeholder="Review notes..."
                    rows={2}
                    value={reviewNotes[review.id] || ""}
                    onChange={(e) => setReviewNotes((prev) => ({ ...prev, [review.id]: e.target.value }))}
                    className="w-full resize-none rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-colors focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  />
                </div>

                <div className="mt-4 flex justify-end gap-3">
                  <button
                    onClick={() => handleResolve(review.id, review.claim_id, "rejected")}
                    disabled={resolving === review.id}
                    className="flex items-center gap-2 rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors"
                  >
                    <XCircle className="h-4 w-4" />
                    {resolving === review.id ? "Processing..." : "Reject"}
                  </button>
                  <button
                    onClick={() => handleResolve(review.id, review.claim_id, "approved")}
                    disabled={resolving === review.id}
                    className="flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    <CheckCircle className="h-4 w-4" />
                    {resolving === review.id ? "Processing..." : "Approve"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
