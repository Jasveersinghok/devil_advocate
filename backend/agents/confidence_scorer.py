"""
Confidence Scorer
Computes a 0-100 confidence score from pro vs counter evidence.
Formula: weighted count of pro evidence vs counter evidence.
"""
from typing import List
from db.schemas import EvidenceItem, ConfidenceBreakdown, StreamEvent


# Weights for relevance-weighted scoring
PRO_WEIGHT = 1.0    # Pro evidence weight multiplier
COUNTER_WEIGHT = 1.2  # Counter evidence slightly penalizes (adversarial bias)


def compute_confidence(
    pro_evidence: List[EvidenceItem],
    counter_evidence: List[EvidenceItem],
) -> ConfidenceBreakdown:
    """
    Compute confidence score from evidence counts and relevance scores.
    
    Score interpretation:
        80-100: STRONGLY SUPPORTED
        60-79:  SUPPORTED
        40-59:  CONTESTED
        20-39:  REFUTED
        0-19:   STRONGLY REFUTED
    
    Formula:
        pro_weight  = sum(item.relevance_score for pro items) * PRO_WEIGHT
        counter_weight = sum(item.relevance_score for counter items) * COUNTER_WEIGHT
        score = (pro_weight / (pro_weight + counter_weight)) * 100
    """
    pro_w = sum(e.relevance_score for e in pro_evidence) * PRO_WEIGHT
    counter_w = sum(e.relevance_score for e in counter_evidence) * COUNTER_WEIGHT

    total = pro_w + counter_w
    if total == 0:
        # No evidence found — score is neutral
        final_score = 50.0
    else:
        final_score = round((pro_w / total) * 100, 1)

    return ConfidenceBreakdown(
        pro_count=len(pro_evidence),
        counter_count=len(counter_evidence),
        pro_weight=round(pro_w, 3),
        counter_weight=round(counter_w, 3),
        final_score=final_score,
    )


def get_verdict(score: float) -> str:
    """Map confidence score to human-readable verdict."""
    if score >= 80:
        return "STRONGLY SUPPORTED"
    elif score >= 60:
        return "SUPPORTED"
    elif score >= 40:
        return "CONTESTED"
    elif score >= 20:
        return "REFUTED"
    else:
        return "STRONGLY REFUTED"


async def score_confidence(
    pro_evidence: List[EvidenceItem],
    counter_evidence: List[EvidenceItem],
    stream_callback=None,
) -> ConfidenceBreakdown:
    """Score confidence and stream the result."""
    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="confidence_scorer",
            message="Computing confidence score...",
        ))

    breakdown = compute_confidence(pro_evidence, counter_evidence)
    verdict = get_verdict(breakdown.final_score)

    if stream_callback:
        await stream_callback(StreamEvent(
            event="score_update",
            agent="confidence_scorer",
            message=f"Confidence score: {breakdown.final_score:.1f}/100 — {verdict}",
            data={
                "score": breakdown.final_score,
                "verdict": verdict,
                "breakdown": breakdown.model_dump(),
            },
        ))

    return breakdown
