"""
LangGraph Orchestrator
Coordinates all agents in the research pipeline using a StateGraph.
Supports streaming via an async callback queue.
"""
import asyncio
from typing import List, Optional, AsyncGenerator, TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END

from agents.claim_decomposer import decompose_claim
from agents.pro_evidence_hunter import hunt_pro_evidence
from agents.counter_evidence_hunter import hunt_counter_evidence
from agents.confidence_scorer import score_confidence, get_verdict
from agents.report_generator import generate_report
from db.schemas import EvidenceItem, ConfidenceBreakdown, ResearchReport, StreamEvent


# ─── LangGraph State ─────────────────────────────────────────────────────────

class ResearchState(TypedDict):
    job_id: str
    claim: str
    sub_claims: List[str]
    pro_evidence: List[EvidenceItem]
    counter_evidence: List[EvidenceItem]
    confidence: Optional[ConfidenceBreakdown]
    report: Optional[ResearchReport]
    error: Optional[str]
    stream_callback: Optional[object]  # callable


# ─── Graph Nodes ──────────────────────────────────────────────────────────────

async def node_decompose(state: ResearchState) -> ResearchState:
    sub_claims = await decompose_claim(
        claim=state["claim"],
        stream_callback=state.get("stream_callback"),
    )
    return {**state, "sub_claims": sub_claims}


async def node_hunt_pro(state: ResearchState) -> ResearchState:
    pro_evidence = await hunt_pro_evidence(
        sub_claims=state["sub_claims"],
        stream_callback=state.get("stream_callback"),
    )
    return {**state, "pro_evidence": pro_evidence}


async def node_hunt_counter(state: ResearchState) -> ResearchState:
    counter_evidence = await hunt_counter_evidence(
        sub_claims=state["sub_claims"],
        stream_callback=state.get("stream_callback"),
    )
    return {**state, "counter_evidence": counter_evidence}


async def node_score(state: ResearchState) -> ResearchState:
    confidence = await score_confidence(
        pro_evidence=state["pro_evidence"],
        counter_evidence=state["counter_evidence"],
        stream_callback=state.get("stream_callback"),
    )
    return {**state, "confidence": confidence}


async def node_report(state: ResearchState) -> ResearchState:
    report = await generate_report(
        job_id=state["job_id"],
        claim=state["claim"],
        sub_claims=state["sub_claims"],
        pro_evidence=state["pro_evidence"],
        counter_evidence=state["counter_evidence"],
        confidence=state["confidence"],
        stream_callback=state.get("stream_callback"),
    )
    return {**state, "report": report}


# ─── Build Graph ──────────────────────────────────────────────────────────────

def build_research_graph():
    """Construct and compile the LangGraph research pipeline."""
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("decompose", node_decompose)
    graph.add_node("hunt_pro", node_hunt_pro)
    graph.add_node("hunt_counter", node_hunt_counter)
    graph.add_node("score", node_score)
    graph.add_node("generate_report", node_report)

    # Sequential pipeline edges
    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "hunt_pro")
    graph.add_edge("hunt_pro", "hunt_counter")
    graph.add_edge("hunt_counter", "score")
    graph.add_edge("score", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_research_graph()
    return _compiled_graph


# ─── Main Entry Point ─────────────────────────────────────────────────────────

async def run_research_pipeline(
    job_id: str,
    claim: str,
    stream_callback=None,
) -> ResearchReport:
    """
    Run the full research pipeline for a claim.
    
    Args:
        job_id: Unique job identifier
        claim: The claim to research
        stream_callback: Async callable that receives StreamEvent objects
        
    Returns:
        ResearchReport with all evidence and confidence score
    """
    graph = get_graph()

    initial_state: ResearchState = {
        "job_id": job_id,
        "claim": claim,
        "sub_claims": [],
        "pro_evidence": [],
        "counter_evidence": [],
        "confidence": None,
        "report": None,
        "error": None,
        "stream_callback": stream_callback,
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        return final_state["report"]
    except Exception as e:
        if stream_callback:
            await stream_callback(StreamEvent(
                event="error",
                agent="orchestrator",
                message=f"Pipeline error: {str(e)}",
                data={"error": str(e)},
            ))
        raise
