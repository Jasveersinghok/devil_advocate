import { JobResponse, FullJob } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Create a new research job.
 */
export async function createJob(claim: string): Promise<JobResponse> {
  const res = await fetch(`${API_BASE}/api/jobs/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ claim }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || `Failed to create job: ${res.status}`);
  }
  return res.json();
}

/**
 * Get all research jobs.
 */
export async function listJobs(): Promise<JobResponse[]> {
  const res = await fetch(`${API_BASE}/api/jobs/`);
  if (!res.ok) throw new Error(`Failed to list jobs: ${res.status}`);
  return res.json();
}

/**
 * Get a specific job with full details.
 */
export async function getJob(jobId: string): Promise<FullJob> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error(`Failed to get job: ${res.status}`);
  return res.json();
}

/**
 * Delete a job.
 */
export async function deleteJob(jobId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Failed to delete job: ${res.status}`);
}

/**
 * Build WebSocket URL for streaming research.
 */
export function buildWsUrl(jobId: string): string {
  const wsBase = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  return `${wsBase}/ws/research/${jobId}`;
}
