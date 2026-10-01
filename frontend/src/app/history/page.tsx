'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Scale, Trash2, Clock, CheckCircle, AlertCircle, Loader2, Plus, ChevronRight } from 'lucide-react';
import { listJobs, deleteJob } from '@/lib/api';
import { JobResponse, JobStatus } from '@/types';
import { formatDate, cn, scoreToVerdict, verdictColor } from '@/lib/utils';

export default function HistoryPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      const data = await listJobs();
      setJobs(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchJobs(); }, [fetchJobs]);

  const handleDelete = async (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteJob(jobId);
      setJobs(prev => prev.filter(j => j.job_id !== jobId));
    } catch (e: any) {
      alert(`Delete failed: ${e.message}`);
    }
  };

  const statusIcon = (status: JobStatus) => {
    switch (status) {
      case 'done':    return <CheckCircle className="w-4 h-4 text-pro-400" />;
      case 'running': return <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />;
      case 'error':   return <AlertCircle className="w-4 h-4 text-counter-400" />;
      default:        return <Clock className="w-4 h-4 text-white/30" />;
    }
  };

  return (
    <div className="min-h-screen relative">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-900/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Research History</h1>
            </div>
            <p className="text-white/40 text-sm">{jobs.length} research job{jobs.length !== 1 ? 's' : ''}</p>
          </div>
          <button
            id="new-research-btn"
            onClick={() => router.push('/')}
            className="btn-primary"
          >
            <Plus className="w-4 h-4" />
            New Research
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="glass-card p-12 text-center">
            <Loader2 className="w-8 h-8 text-brand-400 animate-spin mx-auto mb-3" />
            <p className="text-white/40">Loading history...</p>
          </div>
        ) : error ? (
          <div className="glass-card p-8 text-center border-counter-500/30">
            <AlertCircle className="w-8 h-8 text-counter-400 mx-auto mb-3" />
            <p className="text-white/60">{error}</p>
            <p className="text-white/30 text-sm mt-2">Is the backend running?</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="glass-card p-16 text-center">
            <Scale className="w-12 h-12 text-white/10 mx-auto mb-4" />
            <p className="text-white/40 text-lg">No research jobs yet</p>
            <p className="text-white/20 text-sm mt-2 mb-6">Start by researching a claim</p>
            <button onClick={() => router.push('/')} className="btn-primary">
              <Plus className="w-4 h-4" />
              Research a Claim
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map(job => (
              <button
                key={job.job_id}
                id={`job-${job.job_id}`}
                onClick={() => router.push(`/research/${job.job_id}`)}
                className="w-full glass-card-hover p-5 text-left flex items-center gap-4 group"
              >
                <div className="shrink-0">{statusIcon(job.status)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{job.claim}</p>
                  <p className="text-xs text-white/30 mt-1">{formatDate(job.created_at)}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={cn(
                    'text-xs font-semibold px-2 py-1 rounded-full',
                    job.status === 'done'    ? 'bg-pro-500/15 text-pro-400' :
                    job.status === 'running' ? 'bg-brand-500/15 text-brand-300' :
                    job.status === 'error'   ? 'bg-counter-500/15 text-counter-400' :
                    'bg-white/5 text-white/30'
                  )}>
                    {job.status}
                  </span>
                  <button
                    id={`delete-${job.job_id}`}
                    onClick={(e) => handleDelete(job.job_id, e)}
                    className="p-2 rounded-lg hover:bg-counter-500/20 text-white/20 hover:text-counter-400 transition-all opacity-0 group-hover:opacity-100"
                    title="Delete job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-white/60 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
