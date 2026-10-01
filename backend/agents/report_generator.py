"""
Report Generator
Produces a structured JSON report + markdown narrative from research results.
"""
from datetime import datetime
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_factory import get_llm
from agents.confidence_scorer import get_verdict
from db.schemas import (
    EvidenceItem, ConfidenceBreakdown, ResearchReport, StreamEvent
)


REPORT_PROMPT = """You are an expert research analyst writing a balanced research report.
Write a concise analytical summary (3-4 paragraphs) based on the evidence provided.

Structure:
1. **Overview**: State the claim and what was found
2. **Supporting Evidence**: Summarize the key pro-evidence points
3. **Counter Evidence**: Summarize the key counter-evidence points  
4. **Conclusion**: Give a balanced assessment with the confidence score

Rules:
- Be objective and analytical
- Cite specific evidence when possible
- Acknowledge uncertainty
- Keep each paragraph to 3-5 sentences
- Write in professional research style"""


async def generate_report(
    job_id: str,
    claim: str,
    sub_claims: List[str],
    pro_evidence: List[EvidenceItem],
    counter_evidence: List[EvidenceItem],
    confidence: ConfidenceBreakdown,
    stream_callback=None,
) -> ResearchReport:
    """
    Generate the final research report (JSON + Markdown).
    """
    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="report_generator",
            message="Generating research report...",
        ))

    verdict = get_verdict(confidence.final_score)
    llm = get_llm(temperature=0.3)

    # Build context for LLM
    pro_text = "\n".join([
        f"- [{e.title}]({e.url}): {e.snippet}"
        for e in pro_evidence[:5]
    ]) or "No supporting evidence found."

    counter_text = "\n".join([
        f"- [{e.title}]({e.url}): {e.snippet}"
        for e in counter_evidence[:5]
    ]) or "No counter-evidence found."

    sub_claims_text = "\n".join([f"{i+1}. {sc}" for i, sc in enumerate(sub_claims)])

    messages = [
        SystemMessage(content=REPORT_PROMPT),
        HumanMessage(content=f"""
Claim: {claim}

Sub-claims analyzed:
{sub_claims_text}

Confidence Score: {confidence.final_score:.1f}/100 ({verdict})
Pro evidence count: {confidence.pro_count}
Counter evidence count: {confidence.counter_count}

Supporting Evidence:
{pro_text}

Counter Evidence:
{counter_text}

Write the research report now.
""")
    ]

    try:
        response = await llm.ainvoke(messages)
        narrative = response.content.strip()
    except Exception as e:
        print(f"[ReportGenerator] LLM error: {e}")
        narrative = _fallback_narrative(claim, confidence, verdict)

    # Build full markdown report
    markdown = _build_markdown(
        claim=claim,
        sub_claims=sub_claims,
        pro_evidence=pro_evidence,
        counter_evidence=counter_evidence,
        confidence=confidence,
        verdict=verdict,
        narrative=narrative,
    )

    report = ResearchReport(
        job_id=job_id,
        claim=claim,
        sub_claims=sub_claims,
        pro_evidence=pro_evidence,
        counter_evidence=counter_evidence,
        confidence=confidence,
        verdict=verdict,
        report_markdown=markdown,
        created_at=datetime.utcnow(),
    )

    if stream_callback:
        await stream_callback(StreamEvent(
            event="complete",
            agent="report_generator",
            message="Research complete! Report generated.",
            data={"report": report.model_dump(mode="json")},
        ))

    return report


def _build_markdown(
    claim: str,
    sub_claims: List[str],
    pro_evidence: List[EvidenceItem],
    counter_evidence: List[EvidenceItem],
    confidence: ConfidenceBreakdown,
    verdict: str,
    narrative: str,
) -> str:
    """Build the full markdown report."""
    score_bar = _score_bar(confidence.final_score)
    
    pro_sources = "\n".join([
        f"- **[{e.title}]({e.url})**  \n  {e.snippet}  \n  *Source: {e.source} | Relevance: {e.relevance_score:.0%}*"
        for e in pro_evidence
    ]) or "*No supporting evidence found.*"

    counter_sources = "\n".join([
        f"- **[{e.title}]({e.url})**  \n  {e.snippet}  \n  *Source: {e.source} | Relevance: {e.relevance_score:.0%}*"
        for e in counter_evidence
    ]) or "*No counter-evidence found.*"

    sub_claim_list = "\n".join([f"{i+1}. {sc}" for i, sc in enumerate(sub_claims)])

    return f"""# Devil's Advocate Research Report

## Claim
> {claim}

## Verdict: {verdict}

**Confidence Score: {confidence.final_score:.1f} / 100**

{score_bar}

| Metric | Value |
|--------|-------|
| Supporting Sources | {confidence.pro_count} |
| Counter Sources | {confidence.counter_count} |
| Pro Weight | {confidence.pro_weight:.2f} |
| Counter Weight | {confidence.counter_weight:.2f} |

---

## Sub-Claims Analyzed
{sub_claim_list}

---

## Analysis

{narrative}

---

## Supporting Evidence ({confidence.pro_count} sources)

{pro_sources}

---

## Counter Evidence ({confidence.counter_count} sources)

{counter_sources}

---

*Generated by Devil's Advocate Research Agent · {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*
"""


def _score_bar(score: float) -> str:
    """Generate an ASCII confidence bar."""
    filled = int(score / 5)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    return f"`[{bar}]` {score:.1f}%"


def _fallback_narrative(claim: str, confidence: ConfidenceBreakdown, verdict: str) -> str:
    return (
        f"This research analyzed the claim: '{claim}'. "
        f"Based on the evidence gathered, the claim is rated as **{verdict}** "
        f"with a confidence score of {confidence.final_score:.1f}/100. "
        f"The analysis found {confidence.pro_count} supporting sources and "
        f"{confidence.counter_count} counter-evidence sources."
    )
