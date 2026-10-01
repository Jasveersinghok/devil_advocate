// ─── API Types ────────────────────────────────────────────────────────────────

export type JobStatus = 'pending' | 'running' | 'done' | 'error';

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  claim: string;
  created_at: string;
}

export interface EvidenceItem {
  title: string;
  url: string;
  snippet: string;
  source: string;
  relevance_score: number;
  evidence_type: 'pro' | 'counter';
}

export interface ConfidenceBreakdown {
  pro_count: number;
  counter_count: number;
  pro_weight: number;
  counter_weight: number;
  final_score: number;
}

export type Verdict =
  | 'STRONGLY SUPPORTED'
  | 'SUPPORTED'
  | 'CONTESTED'
  | 'REFUTED'
  | 'STRONGLY REFUTED';

export interface ResearchReport {
  job_id: string;
  claim: string;
  sub_claims: string[];
  pro_evidence: EvidenceItem[];
  counter_evidence: EvidenceItem[];
  confidence: ConfidenceBreakdown;
  verdict: Verdict;
  report_markdown: string;
  created_at: string;
}

export interface FullJob {
  job_id: string;
  status: JobStatus;
  claim: string;
  created_at: string;
  updated_at: string;
  sub_claims: string[] | null;
  pro_evidence: EvidenceItem[] | null;
  counter_evidence: EvidenceItem[] | null;
  confidence_score: number | null;
  report_markdown: string | null;
  report_json: ResearchReport | null;
  error_message: string | null;
}

// ─── WebSocket Event Types ────────────────────────────────────────────────────

export type StreamEventType =
  | 'agent_start'
  | 'agent_done'
  | 'evidence_found'
  | 'score_update'
  | 'complete'
  | 'error';

export type AgentName =
  | 'orchestrator'
  | 'claim_decomposer'
  | 'pro_evidence_hunter'
  | 'counter_evidence_hunter'
  | 'confidence_scorer'
  | 'report_generator'
  | 'cache';

export interface StreamEvent {
  event: StreamEventType;
  agent?: AgentName;
  message: string;
  data?: {
    sub_claims?: string[];
    evidence?: EvidenceItem[];
    total?: number;
    score?: number;
    verdict?: string;
    breakdown?: ConfidenceBreakdown;
    report?: ResearchReport;
    report_json?: ResearchReport;
    error?: string;
  };
  timestamp: string;
}

// ─── UI State Types ───────────────────────────────────────────────────────────

export interface AgentStatus {
  name: AgentName;
  displayName: string;
  status: 'pending' | 'active' | 'done' | 'error';
  message?: string;
  startedAt?: number;
  finishedAt?: number;
}
