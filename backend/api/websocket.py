"""
WebSocket Streaming Router
Handles real-time streaming of agent progress to the frontend.
"""
import json
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import ResearchJob, AsyncSessionLocal
from db.schemas import StreamEvent, JobStatus
from agents.orchestrator import run_research_pipeline

router = APIRouter(tags=["websocket"])


def serialize_event(event: StreamEvent) -> str:
    """Serialize a StreamEvent to JSON string."""
    return json.dumps(event.model_dump(mode="json"), default=str)


@router.websocket("/ws/research/{job_id}")
async def research_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for streaming research progress.
    
    Client connects → backend runs pipeline → streams events in real-time.
    
    Events:
        agent_start    — An agent began working
        agent_done     — An agent completed
        evidence_found — New evidence pieces discovered
        score_update   — Confidence score computed
        complete       — Full report ready
        error          — Pipeline encountered an error
    """
    await websocket.accept()

    async with AsyncSessionLocal() as db:
        # Fetch job
        result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            await websocket.send_text(serialize_event(StreamEvent(
                event="error",
                message=f"Job {job_id} not found",
            )))
            await websocket.close()
            return

        if job.status == JobStatus.DONE:
            # Already completed — send cached report
            await websocket.send_text(serialize_event(StreamEvent(
                event="complete",
                agent="cache",
                message="Research already complete (from cache)",
                data={"report_json": job.report_json},
            )))
            await websocket.close()
            return

        if job.status == JobStatus.RUNNING:
            await websocket.send_text(serialize_event(StreamEvent(
                event="error",
                message="Job is already running",
            )))
            await websocket.close()
            return

        # Mark as running
        job.status = JobStatus.RUNNING
        await db.commit()

    # ── Stream callback ───────────────────────────────────────────────────────
    async def stream_callback(event: StreamEvent):
        """Forward agent events to the WebSocket client."""
        try:
            await websocket.send_text(serialize_event(event))
        except Exception:
            pass  # Client disconnected

    # ── Run pipeline ──────────────────────────────────────────────────────────
    try:
        # Send start event
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="orchestrator",
            message="Research pipeline starting...",
        ))

        report = await run_research_pipeline(
            job_id=job_id,
            claim=job.claim,
            stream_callback=stream_callback,
        )

        # Persist results
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = JobStatus.DONE
                job.sub_claims = report.sub_claims
                job.pro_evidence = [e.model_dump() for e in report.pro_evidence]
                job.counter_evidence = [e.model_dump() for e in report.counter_evidence]
                job.confidence_score = report.confidence.final_score
                job.report_markdown = report.report_markdown
                job.report_json = report.model_dump(mode="json")
                await db.commit()

    except WebSocketDisconnect:
        # Client disconnected mid-stream — still mark job as error
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = JobStatus.ERROR
                job.error_message = "Client disconnected"
                await db.commit()

    except Exception as e:
        error_msg = str(e)
        await stream_callback(StreamEvent(
            event="error",
            agent="orchestrator",
            message=f"Pipeline failed: {error_msg}",
            data={"error": error_msg},
        ))

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = JobStatus.ERROR
                job.error_message = error_msg
                await db.commit()

    finally:
        try:
            await websocket.close()
        except Exception:
            pass
