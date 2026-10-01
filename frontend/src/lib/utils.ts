import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Verdict } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function verdictColor(verdict: Verdict): string {
  switch (verdict) {
    case 'STRONGLY SUPPORTED': return 'text-pro-400';
    case 'SUPPORTED':          return 'text-emerald-400';
    case 'CONTESTED':          return 'text-yellow-400';
    case 'REFUTED':            return 'text-orange-400';
    case 'STRONGLY REFUTED':   return 'text-counter-400';
    default:                   return 'text-white/60';
  }
}

export function verdictBgClass(verdict: Verdict): string {
  switch (verdict) {
    case 'STRONGLY SUPPORTED': return 'bg-pro-500/20 border-pro-500/40';
    case 'SUPPORTED':          return 'bg-emerald-500/20 border-emerald-500/40';
    case 'CONTESTED':          return 'bg-yellow-500/20 border-yellow-500/40';
    case 'REFUTED':            return 'bg-orange-500/20 border-orange-500/40';
    case 'STRONGLY REFUTED':   return 'bg-counter-500/20 border-counter-500/40';
    default:                   return 'bg-white/5 border-white/10';
  }
}

export function scoreToVerdict(score: number): Verdict {
  if (score >= 80) return 'STRONGLY SUPPORTED';
  if (score >= 60) return 'SUPPORTED';
  if (score >= 40) return 'CONTESTED';
  if (score >= 20) return 'REFUTED';
  return 'STRONGLY REFUTED';
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function agentDisplayName(agent: string): string {
  const names: Record<string, string> = {
    orchestrator:            'Orchestrator',
    claim_decomposer:        'Claim Decomposer',
    pro_evidence_hunter:     'Pro-Evidence Hunter',
    counter_evidence_hunter: 'Counter-Evidence Hunter',
    confidence_scorer:       'Confidence Scorer',
    report_generator:        'Report Generator',
  };
  return names[agent] || agent;
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + '...';
}
