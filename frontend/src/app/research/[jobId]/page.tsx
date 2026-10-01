'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Brain, Shield, Scale, Zap, FileText,
  CheckCircle, Loader2, AlertCircle, ArrowLeft,
  ExternalLink, TrendingUp, TrendingDown, Minus
} from 'lucide-react';
import { buildWsUrl, getJob } from '@/lib/api';
import {
  StreamEvent, AgentStatus, AgentName, EvidenceItem, ResearchReport, FullJob
} from '@/types';
import { agentDisplayName, verdictColor, verdictBgClass, formatDate, cn } from '@/lib/utils';

// ─── Agent pipeline config ────────────────────────────────────────────────────

const PIPELINE_AGENTS: { name: AgentName; icon: React.ElementType; color: string }[] = [
  { name: 'claim_decomposer',        icon: Brain,    color: 'text-purple-400' },
  { name: 'pro_evidence_hunter',     icon: TrendingUp, color: 'text-pro-400' },
  { name: 'counter_evidence_hunter', icon: TrendingDown, color: 'text-counter-400' },
  { name: 'confidence_scorer',       icon: Scale,    color: 'text-brand-400' },
  { name: 'report_generator',        icon: FileText, color: 'text-yellow-400' },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function AgentCard({
  agent,
  icon: Icon,
  color,
  status,
  message,
}: {
  agent: AgentName;
  icon: React.ElementType;
  color: string;
  status: 'pending' | 'active' | 'done' | 'error';
  message?: string;
}) {
  return (
    <div className={cn(
      'glass-card p-4 flex items-start gap-4 transition-all duration-500',
      status === 'active' && 'border-brand-400/40 bg-brand-600/10',
      status === 'done'   && 'border-pro-500/30 bg-pro-500/5',
      status === 'error'  && 'border-counter-500/30 bg-counter-500/5',
    )}>
      <div className={cn(
        'w-10 h-10 rounded-xl flex items-center justify-center shrink-0',
        status === 'active' ? 'bg-brand-600/30 animate-pulse' : 'bg-white/5'
      )}>
        <Icon className={cn('w-5 h-5', status === 'done' ? 'text-pro-400' : status === 'active' ? 'text-white' : 'text-white/30')} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className={cn(
            'text-sm font-semibold',
            status === 'done'   ? 'text-white' : 
            status === 'active' ? 'text-white' : 
            'text-white/40'
          )}>
            {agentDisplayName(agent)}
          </span>
          <div>
            {status === 'active' && <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />}
            {status === 'done'   && <CheckCircle className="w-4 h-4 text-pro-400" />}
            {status === 'error'  && <AlertCircle className="w-4 h-4 text-counter-400" />}
            {status === 'pending'&& <div className="w-4 h-4 rounded-full border border-white/20" />}
          </div>
        </div>
        {message && (
          <p className={cn(
            'text-xs mt-1 leading-relaxed',
            status === 'active' ? 'text-brand-300' : 'text-white/40'
          )}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

function EvidenceCard({ item }: { item: EvidenceItem }) {
  const isPro = item.evidence_type === 'pro';
  return (
    <div className={cn(
      'glass-card p-4 space-y-2 animate-slide-up',
      isPro ? 'border-pro-500/20' : 'border-counter-500/20'
    )}>
      <div className="flex items-start gap-3">
        <div className={cn(
          'w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5',
          isPro ? 'bg-pro-500/20' : 'bg-counter-500/20'
        )}>
          {isPro
            ? <TrendingUp className="w-3.5 h-3.5 text-pro-400" />
            : <TrendingDown className="w-3.5 h-3.5 text-counter-400" />
          }
        </div>
        <div className="flex-1 min-w-0">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-semibold text-white hover:text-brand-300 transition-colors flex items-center gap-1 group"
          >
            <span className="truncate">{item.title || item.url}</span>
            <ExternalLink className="w-3 h-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
          <p className="text-xs text-white/50 mt-1 leading-relaxed line-clamp-3">{item.snippet}</p>
        </div>
      </div>
      <div className="flex items-center justify-between pt-1">
        <span className={cn('badge', isPro ? 'badge-pro' : 'badge-counter')}>
          {isPro ? '✓ Supporting' : '✗ Counter'}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/30">{item.source}</span>
          <div className="flex items-center gap-1">
            <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className={cn('h-full rounded-full', isPro ? 'bg-pro-400' : 'bg-counter-400')}
                style={{ width: `${item.relevance_score * 100}%` }}
              />
            </div>
            <span className="text-xs text-white/30">{Math.round(item.relevance_score * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConfidenceGauge({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, score));
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (pct / 100) * circumference;

  const color =
    pct >= 80 ? '#22c55e' :
    pct >= 60 ? '#4ade80' :
    pct >= 40 ? '#facc15' :
    pct >= 20 ? '#fb923c' :
    '#f43f5e';

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease-out, stroke 0.5s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold text-white">{pct.toFixed(0)}</span>
          <span className="text-xs text-white/40">/ 100</span>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ResearchPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const router = useRouter();

  const [log, setLog] = useState<StreamEvent[]>([]);
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>(() => {
    const init: Record<string, AgentStatus> = {};
    PIPELINE_AGENTS.forEach(({ name }) => {
      init[name] = { name, displayName: agentDisplayName(name), status: 'pending' };
    });
    return init;
  });
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [liveScore, setLiveScore] = useState<number | null>(null);
  const [liveVerdict, setLiveVerdict] = useState<string | null>(null);
  const [liveEvidence, setLiveEvidence] = useState<EvidenceItem[]>([]);
  const [subClaims, setSubClaims] = useState<string[]>([]);
  const [claim, setClaim] = useState<string>('');
  const [isConnecting, setIsConnecting] = useState(true);
  const [isDone, setIsDone] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'pro' | 'counter' | 'all'>('all');

  const wsRef = useRef<WebSocket | null>(null);

  // Load job info first (for claim text)
  useEffect(() => {
    if (!jobId) return;
    getJob(jobId).then(job => {
      setClaim(job.claim);
      // If already done, show report immediately
      if (job.status === 'done' && job.report_json) {
        setReport(job.report_json);
        setLiveScore(job.confidence_score ?? null);
        setLiveEvidence([
          ...(job.pro_evidence ?? []),
          ...(job.counter_evidence ?? []),
        ]);
        setSubClaims(job.sub_claims ?? []);
        setIsDone(true);
        setIsConnecting(false);
      }
    }).catch(console.error);
  }, [jobId]);

  // WebSocket connection
  useEffect(() => {
    if (!jobId || isDone) return;

    const ws = new WebSocket(buildWsUrl(jobId));
    wsRef.current = ws;

    ws.onopen = () => setIsConnecting(false);

    ws.onmessage = (e) => {
      try {
        const event: StreamEvent = JSON.parse(e.data);
        setLog(prev => [...prev, event]);

        const agent = event.agent as AgentName | undefined;

        // Update agent statuses
        if (agent && agent !== 'orchestrator' && agent !== 'cache') {
          setAgentStatuses(prev => {
            const updated = { ...prev };
            if (event.event === 'agent_start') {
              updated[agent] = { ...prev[agent], status: 'active', message: event.message };
            } else if (event.event === 'agent_done') {
              updated[agent] = { ...prev[agent], status: 'done', message: event.message };
            } else if (event.event === 'error') {
              if (updated[agent]) updated[agent] = { ...prev[agent], status: 'error', message: event.message };
            }
            return updated;
          });
        }

        // Collect sub-claims
        if (event.event === 'agent_done' && agent === 'claim_decomposer' && event.data?.sub_claims) {
          setSubClaims(event.data.sub_claims);
        }

        // Accumulate evidence
        if (event.event === 'evidence_found' && event.data?.evidence) {
          setLiveEvidence(prev => [...prev, ...event.data!.evidence!]);
        }

        // Score update
        if (event.event === 'score_update' && event.data?.score !== undefined) {
          setLiveScore(event.data.score);
          setLiveVerdict(event.data.verdict ?? null);
          setAgentStatuses(prev => ({
            ...prev,
            confidence_scorer: { ...prev.confidence_scorer, status: 'done', message: event.message },
          }));
        }

        // Complete
        if (event.event === 'complete') {
          const reportData = event.data?.report || event.data?.report_json;
          if (reportData) setReport(reportData as ResearchReport);
          setIsDone(true);
          PIPELINE_AGENTS.forEach(({ name }) => {
            setAgentStatuses(prev => ({
              ...prev,
              [name]: { ...prev[name], status: prev[name].status === 'error' ? 'error' : 'done' },
            }));
          });
        }

        // Error
        if (event.event === 'error') {
          setGlobalError(event.message);
        }

      } catch (err) {
        console.error('WS parse error', err);
      }
    };

    ws.onerror = () => {
      setGlobalError('WebSocket connection failed. Is the backend running on port 8000?');
      setIsConnecting(false);
    };

    ws.onclose = () => {
      setIsConnecting(false);
    };

    return () => {
      ws.close();
    };
  }, [jobId, isDone]);

  // Derived
  const proEvidence = (report?.pro_evidence ?? liveEvidence.filter(e => e.evidence_type === 'pro'));
  const counterEvidence = (report?.counter_evidence ?? liveEvidence.filter(e => e.evidence_type === 'counter'));
  const displayedScore = report?.confidence.final_score ?? liveScore;
  const displayedVerdict = report?.verdict ?? liveVerdict;
  const displayedSubClaims = report?.sub_claims ?? subClaims;

  const filteredEvidence =
    activeTab === 'pro'     ? proEvidence :
    activeTab === 'counter' ? counterEvidence :
    [...proEvidence, ...counterEvidence];

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-900/30 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-32 w-80 h-80 bg-purple-900/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Top bar */}
        <div className="flex items-center gap-4">
          <button
            id="back-btn"
            onClick={() => router.push('/')}
            className="btn-secondary text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-white/30 uppercase tracking-widest mb-1">Researching claim</p>
            <h1 className="text-lg font-semibold text-white truncate">{claim || 'Loading...'}</h1>
          </div>
          {isDone && (
            <span className="badge badge-pro text-sm px-3 py-1.5 shrink-0">
              <CheckCircle className="w-3.5 h-3.5" />
              Complete
            </span>
          )}
          {isConnecting && (
            <span className="badge badge-neutral shrink-0">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Connecting...
            </span>
          )}
        </div>

        {/* Global error — only show if research didn't complete successfully */}
        {globalError && !isDone && (
          <div className="glass-card p-4 border-counter-500/40 bg-counter-500/10 text-counter-300 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Research Error</p>
              <p className="text-sm mt-1 text-white/60">{globalError}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ── Left column: Agent pipeline ─────────────────────────── */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-sm font-semibold text-white/40 uppercase tracking-widest">Agent Pipeline</h2>
            <div className="space-y-3">
              {PIPELINE_AGENTS.map(({ name, icon }) => (
                <AgentCard
                  key={name}
                  agent={name}
                  icon={icon}
                  color=""
                  status={agentStatuses[name]?.status ?? 'pending'}
                  message={agentStatuses[name]?.message}
                />
              ))}
            </div>

            {/* Sub-claims */}
            {displayedSubClaims.length > 0 && (
              <div className="glass-card p-4 space-y-3 mt-4">
                <h3 className="text-xs font-semibold text-white/40 uppercase tracking-wider">Sub-Claims</h3>
                {displayedSubClaims.map((sc, i) => (
                  <div key={i} className="flex gap-3">
                    <span className="w-5 h-5 bg-brand-600/30 rounded-full text-brand-300 text-xs flex items-center justify-center shrink-0 mt-0.5 font-bold">
                      {i + 1}
                    </span>
                    <p className="text-sm text-white/70 leading-relaxed">{sc}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Right column: Score + Evidence ──────────────────────── */}
          <div className="lg:col-span-2 space-y-6">
            {/* Confidence score card */}
            {displayedScore !== null && (
              <div className={cn('glass-card p-6 animate-slide-up', displayedVerdict ? verdictBgClass(displayedVerdict as any) : '')}>
                <div className="flex items-center gap-8">
                  <ConfidenceGauge score={displayedScore} />
                  <div className="flex-1">
                    <p className="text-xs text-white/30 uppercase tracking-wider mb-2">Confidence Score</p>
                    {displayedVerdict && (
                      <p className={cn('text-2xl font-extrabold mb-3', verdictColor(displayedVerdict as any))}>
                        {displayedVerdict}
                      </p>
                    )}
                    {report?.confidence && (
                      <div className="grid grid-cols-2 gap-4">
                        <div className="glass-card p-3 text-center">
                          <p className="text-2xl font-bold text-pro-400">{report.confidence.pro_count}</p>
                          <p className="text-xs text-white/40 mt-1">Supporting Sources</p>
                        </div>
                        <div className="glass-card p-3 text-center">
                          <p className="text-2xl font-bold text-counter-400">{report.confidence.counter_count}</p>
                          <p className="text-xs text-white/40 mt-1">Counter Sources</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Score bar */}
                <div className="mt-5">
                  <div className="flex justify-between text-xs text-white/30 mb-1.5">
                    <span>Strongly Refuted</span>
                    <span>Contested</span>
                    <span>Strongly Supported</span>
                  </div>
                  <div className="h-3 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className="h-full score-gradient rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${displayedScore}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Loading placeholder */}
            {displayedScore === null && !isDone && (
              <div className="glass-card p-8 text-center">
                <Loader2 className="w-10 h-10 text-brand-400 animate-spin mx-auto mb-4" />
                <p className="text-white/60">Agents are working...</p>
                <p className="text-xs text-white/30 mt-1">Score will appear when analysis is complete</p>
              </div>
            )}

            {/* Evidence section */}
            {filteredEvidence.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-white/40 uppercase tracking-widest">Evidence</h2>
                  <div className="flex gap-2">
                    {(['all', 'pro', 'counter'] as const).map(tab => (
                      <button
                        key={tab}
                        id={`tab-${tab}`}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all',
                          activeTab === tab
                            ? tab === 'pro'     ? 'bg-pro-500/20 text-pro-400 border border-pro-500/40'
                            : tab === 'counter' ? 'bg-counter-500/20 text-counter-400 border border-counter-500/40'
                            : 'bg-brand-600/20 text-brand-300 border border-brand-400/40'
                            : 'text-white/30 hover:text-white/60'
                        )}
                      >
                        {tab === 'all'     ? `All (${proEvidence.length + counterEvidence.length})` :
                         tab === 'pro'     ? `Support (${proEvidence.length})` :
                         `Counter (${counterEvidence.length})`}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {filteredEvidence.map((item, i) => (
                    <EvidenceCard key={`${item.url}-${i}`} item={item} />
                  ))}
                </div>
              </div>
            )}

            {/* Markdown report */}
            {report?.report_markdown && (
              <div className="glass-card p-6 animate-slide-up">
                <h2 className="text-sm font-semibold text-white/40 uppercase tracking-widest mb-4">Full Report</h2>
                <div className="prose prose-invert prose-sm max-w-none text-white/70 leading-relaxed">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-white/70 leading-7">
                    {report.report_markdown}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>


      </div>
    </div>
  );
}
