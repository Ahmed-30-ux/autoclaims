"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { createClaimWithPhotos } from "@/lib/api";
import {
  FileText, Send, Upload, X, Camera, Image as ImageIcon,
} from "lucide-react";

const claimTypes = [
  { value: "auto", label: "Auto" },
  { value: "home", label: "Home" },
  { value: "health", label: "Health" },
  { value: "travel", label: "Travel" },
  { value: "property", label: "Property" },
  { value: "liability", label: "Liability" },
  { value: "other", label: "Other" },
];

export default function NewClaim() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [submitting, setSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [photos, setPhotos] = useState<File[]>([]);
  const [photoPreviews, setPhotoPreviews] = useState<string[]>([]);
  const [form, setForm] = useState({
    claimant_name: "",
    claimant_email: "",
    claimant_phone: "",
    policy_number: "",
    claim_type: "auto",
    description: "",
    incident_date: "",
    location: "",
    estimated_loss: "",
  });

  const addPhotos = (files: FileList | File[]) => {
    const newFiles = Array.from(files).filter(f => f.type.startsWith("image/"));
    setPhotos(prev => [...prev, ...newFiles]);
    for (const file of newFiles) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreviews(prev => [...prev, e.target?.result as string]);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = (idx: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== idx));
    setPhotoPreviews(prev => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("claimant_name", form.claimant_name);
      formData.append("claimant_email", form.claimant_email);
      formData.append("claimant_phone", form.claimant_phone);
      formData.append("policy_number", form.policy_number);
      formData.append("claim_type", form.claim_type);
      formData.append("description", form.description);
      formData.append("incident_date", form.incident_date);
      formData.append("location", form.location);
      if (form.estimated_loss) formData.append("estimated_loss", form.estimated_loss);
      photos.forEach((photo) => formData.append("photos", photo));

      const result = await createClaimWithPhotos(formData);
      router.push(`/claim/${result.claim_id}`);
    } catch (err) {
      console.error("Failed to create claim", err);
      alert("Failed to submit claim. Is the backend running?");
    } finally {
      setSubmitting(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8 page-enter">
      <div className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-md">
          <FileText className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Submit New Claim</h2>
          <p className="text-slate-500">Our AI pipeline will process this claim through 5 intelligent agents.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Claimant Information */}
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-blue-500 to-blue-600" />
          <div className="p-6">
            <h3 className="mb-4 flex items-center gap-2 text-base font-bold text-slate-900">
              <FileText className="h-4 w-4 text-blue-600" /> Claimant Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Full Name *</label>
                <input
                  type="text"
                  required
                  value={form.claimant_name}
                  onChange={(e) => updateField("claimant_name", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g., John Doe"
                />
              </div>
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Email *</label>
                <input
                  type="email"
                  required
                  value={form.claimant_email}
                  onChange={(e) => updateField("claimant_email", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="john@email.com"
                />
              </div>
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Phone</label>
                <input
                  type="tel"
                  value={form.claimant_phone}
                  onChange={(e) => updateField("claimant_phone", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Policy Number *</label>
                <input
                  type="text"
                  required
                  value={form.policy_number}
                  onChange={(e) => updateField("policy_number", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g., POL-2026-001"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Claim Details */}
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-violet-500 to-violet-600" />
          <div className="p-6">
            <h3 className="mb-4 flex items-center gap-2 text-base font-bold text-slate-900">
              <FileText className="h-4 w-4 text-violet-600" /> Claim Details
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Claim Type *</label>
                <select
                  required
                  value={form.claim_type}
                  onChange={(e) => updateField("claim_type", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                >
                  {claimTypes.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Incident Date *</label>
                <input
                  type="date"
                  required
                  value={form.incident_date}
                  onChange={(e) => updateField("incident_date", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                />
              </div>
              <div className="col-span-2">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Location</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => updateField("location", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g., New York, NY"
                />
              </div>
              <div className="col-span-2">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Description *</label>
                <textarea
                  required
                  rows={4}
                  value={form.description}
                  onChange={(e) => updateField("description", e.target.value)}
                  className="w-full resize-none rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="Describe the incident in detail..."
                />
              </div>
              <div className="col-span-2 sm:col-span-1">
                <label className="mb-1.5 block text-sm font-medium text-slate-700">Estimated Loss ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.estimated_loss}
                  onChange={(e) => updateField("estimated_loss", e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none transition-all focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                  placeholder="e.g., 5000"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Photo Upload Section */}
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="h-1.5 w-full bg-gradient-to-r from-amber-500 to-rose-500" />
          <div className="p-6">
            <h3 className="mb-4 flex items-center gap-2 text-base font-bold text-slate-900">
              <Camera className="h-4 w-4 text-amber-600" /> Damage Photos
            </h3>
            <p className="mb-4 text-sm text-slate-500">
              Upload photos of the damage — the AI will analyze them to assess severity (optional but recommended).
            </p>

            {/* Drop zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); addPhotos(e.dataTransfer.files); }}
              onClick={() => fileInputRef.current?.click()}
              className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
                dragOver ? "border-blue-400 bg-blue-50" : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                className="hidden"
                onChange={(e) => { if (e.target.files) addPhotos(e.target.files); }}
              />
              <div className="flex flex-col items-center gap-2">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                  <Upload className="h-6 w-6 text-slate-400" />
                </div>
                <p className="text-sm font-medium text-slate-600">
                  {dragOver ? "Drop photos here" : "Drag & drop photos or click to browse"}
                </p>
                <p className="text-xs text-slate-400">Supports JPG, PNG, WebP — up to 10MB each</p>
              </div>
            </div>

            {/* Photo previews */}
            {photoPreviews.length > 0 && (
              <div className="mt-4 grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5">
                {photoPreviews.map((preview, idx) => (
                  <div key={idx} className="group relative aspect-square overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
                    <img src={preview} alt={`Damage photo ${idx + 1}`} className="h-full w-full object-cover" />
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); removePhoto(idx); }}
                      className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-black/50 text-white opacity-0 transition-opacity group-hover:opacity-100 hover:bg-black/70"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-1.5">
                      <p className="text-[10px] font-medium text-white">{photos[idx].name}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => router.push("/")}
            className="rounded-xl border border-slate-200 bg-white px-6 py-2.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 transition-all"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:from-blue-700 hover:to-blue-800 hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Submit Claim
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
