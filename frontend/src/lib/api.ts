const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Claim {
  id: number;
  status: string;
  claimant_name: string;
  claim_type: string;
  description: string;
  policy_number: string;
  created_at: string;
  updated_at: string;
  pipeline_progress: number;
  current_agent: string;
  image_paths: string[];
  intake_data: Record<string, unknown> | null;
  validation_data: Record<string, unknown> | null;
  assessment_data: Record<string, unknown> | null;
  review_gate_data: Record<string, unknown> | null;
  resolution_data: Record<string, unknown> | null;
}

export interface CreateClaimPayload {
  claimant_name: string;
  claimant_email: string;
  claimant_phone?: string;
  policy_number: string;
  claim_type: string;
  description: string;
  incident_date: string;
  location?: string;
  estimated_loss?: number;
}

export interface ReviewPayload {
  review_id?: number;
  status: string;
  notes: string;
  reviewer: string;
  reviewed_at: string;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API Error ${res.status}: ${err}`);
  }
  return res.json();
}

export async function createClaim(data: CreateClaimPayload): Promise<{ claim_id: number; status: string }> {
  return fetchJson('/api/claims', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createClaimWithPhotos(formData: FormData): Promise<{ claim_id: number; status: string; photos_saved: number }> {
  const res = await fetch(`${API_BASE}/api/claims/with-photos`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API Error ${res.status}: ${err}`);
  }
  return res.json();
}

export async function listClaims(): Promise<{ claims: Claim[]; total: number }> {
  return fetchJson('/api/claims');
}

export async function getClaim(id: number): Promise<Claim> {
  return fetchJson(`/api/claims/${id}`);
}

export async function processClaim(id: number): Promise<Record<string, unknown>> {
  return fetchJson(`/api/claims/${id}/process`, { method: 'POST' });
}

export async function getPendingReviews(): Promise<{ reviews: unknown[]; total: number }> {
  return fetchJson('/api/claims/reviews/pending');
}

export async function resolveHumanReview(claimId: number, decision: ReviewPayload): Promise<Record<string, unknown>> {
  return fetchJson(`/api/claims/${claimId}/review`, {
    method: 'POST',
    body: JSON.stringify(decision),
  });
}

export async function healthCheck(): Promise<{ status: string }> {
  return fetchJson('/api/health');
}
