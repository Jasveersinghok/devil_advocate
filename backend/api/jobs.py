"""
Research Jobs API Router
REST endpoints for creating and retrieving research jobs.
"""
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import ResearchJob, get_db
from db.schemas import CreateJobRequest, JobResponse, JobStatus, ResearchReport

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    body: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new research job. Returns job_id immediately."""
    job_id = str(uuid.uuid4())
    job = ResearchJob(
        id=job_id,
        claim=body.claim,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return JobResponse(
        job_id=job.id,
        status=JobStatus(job.status),
        claim=job.claim,
        created_at=job.created_at,
    )


@router.get("/", response_model=List[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    """List all research jobs."""
    result = await db.execute(
        select(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(50)
    )
    jobs = result.scalars().all()
    return [
        JobResponse(
            job_id=j.id,
            status=JobStatus(j.status),
            claim=j.claim,
            created_at=j.created_at,
        )
        for j in jobs
    ]


@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get full details of a research job including report."""
    result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "claim": job.claim,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "sub_claims": job.sub_claims,
        "pro_evidence": job.pro_evidence,
        "counter_evidence": job.counter_evidence,
        "confidence_score": job.confidence_score,
        "report_markdown": job.report_markdown,
        "report_json": job.report_json,
        "error_message": job.error_message,
    }


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a research job."""
    result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()
