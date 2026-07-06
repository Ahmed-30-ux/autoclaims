export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    submitted: 'bg-blue-50 text-blue-700 border-blue-200',
    intake_complete: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    validating: 'bg-purple-50 text-purple-700 border-purple-200',
    validated: 'bg-teal-50 text-teal-700 border-teal-200',
    assessing: 'bg-violet-50 text-violet-700 border-violet-200',
    assessed: 'bg-violet-50 text-violet-700 border-violet-200',
    pending_review: 'bg-orange-50 text-orange-700 border-orange-200',
    approved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rejected: 'bg-red-50 text-red-700 border-red-200',
    resolved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    error: 'bg-red-50 text-red-700 border-red-200',
  };
  return colors[status] || 'bg-slate-50 text-slate-700 border-slate-200';
}

export function getAgentIcon(agent: string): string {
  const icons: Record<string, string> = {
    intake: '📋',
    validation: '✅',
    assessment: '📊',
    review_gate: '🔍',
    resolution: '📝',
    completed: '🎉',
  };
  return icons[agent] || '⚙️';
}

export function getAgentLabel(agent: string): string {
  const labels: Record<string, string> = {
    intake: 'Intake',
    validation: 'Validation',
    assessment: 'Assessment',
    review_gate: 'Review Gate',
    resolution: 'Resolution',
    completed: 'Completed',
  };
  return labels[agent] || agent;
}

export function getAgentColor(agent: string): string {
  const colors: Record<string, string> = {
    intake: '#3b82f6',
    validation: '#22c55e',
    assessment: '#8b5cf6',
    review_gate: '#f59e0b',
    resolution: '#ec4899',
    completed: '#22c55e',
  };
  return colors[agent] || '#94a3b8';
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}
