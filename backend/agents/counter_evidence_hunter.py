"""
Counter-Evidence Hunter Agent
Adversarially searches for evidence that contradicts or challenges the claim.

Search strategy (Tavily only, no extra API keys needed):
  - Query 1: "evidence against / criticism of {claim}"
  - Query 2: "problems / limitations / why wrong: {claim}"
  Two different adversarial framings of the same Tavily search surface
  genuinely opposing perspectives.
"""
import json
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_factory import get_llm
from db.schemas import EvidenceItem, StreamEvent
from tools_client.tool_loader import get_tavily_tools


COUNTER_RELEVANCE_PROMPT = """You are a devil's advocate research assistant.
Given a claim and search results, extract evidence that CHALLENGES, CONTRADICTS,
or COMPLICATES the claim. Return ONLY valid JSON.

Output format:
{
  "evidence": [
    {
      "title": "Article title",
      "url": "https://...",
      "snippet": "Relevant quote or summary showing contradiction (2-3 sentences)",
      "relevance_score": 0.85
    }
  ]
}

Rules:
- Include only evidence that genuinely challenges the claim
- Look for: contradictions, limitations, alternative explanations, criticism
- relevance_score is 0.0-1.0
- Maximum 5 evidence items
- If no counter evidence found, return {"evidence": []}"""


# Two adversarial framings — sent as separate Tavily queries for diversity
ADVERSARIAL_TEMPLATES = [
    "criticism and evidence against: {claim}",
    "problems limitations and reasons why wrong: {claim}",
]


async def hunt_counter_evidence(
    sub_claims: List[str],
    stream_callback=None,
) -> List[EvidenceItem]:
    """
    Search for counter-evidence using Tavily with two adversarial query framings.

    Args:
        sub_claims: List of sub-claims to challenge
        stream_callback: Optional async callable for streaming progress

    Returns:
        List of EvidenceItem objects with counter evidence
    """
    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="counter_evidence_hunter",
            message="Searching for counter-evidence (devil's advocate mode)...",
        ))

    all_evidence: List[EvidenceItem] = []
    tavily_tools = await get_tavily_tools()
    llm = get_llm(temperature=0.0)

    if not tavily_tools:
        if stream_callback:
            await stream_callback(StreamEvent(
                event="agent_done",
                agent="counter_evidence_hunter",
                message="No search tools available for counter-evidence.",
            ))
        return []

    tool = tavily_tools[0]

    for i, sub_claim in enumerate(sub_claims):
        if stream_callback:
            await stream_callback(StreamEvent(
                event="agent_start",
                agent="counter_evidence_hunter",
                message=f"Finding counter-evidence for sub-claim {i+1}: '{sub_claim[:70]}...'",
            ))

        all_raw_results = []

        # Run two adversarially-framed Tavily queries
        for template in ADVERSARIAL_TEMPLATES:
            query = template.format(claim=sub_claim)
            try:
                raw = await tool.ainvoke({"query": query})
                results = _parse_tavily_results(raw)
                all_raw_results.extend(results)
            except Exception as e:
                print(f"[CounterHunter] Tavily query failed: {e}")

        if not all_raw_results:
            continue

        # Deduplicate by URL
        seen_urls: set = set()
        unique_results = []
        for r in all_raw_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        # LLM filters for genuine counter-evidence
        evidence = await _filter_counter_evidence(
            claim=sub_claim,
            raw_results=unique_results[:12],
            llm=llm,
        )
        all_evidence.extend(evidence)

        if stream_callback and evidence:
            await stream_callback(StreamEvent(
                event="evidence_found",
                agent="counter_evidence_hunter",
                message=f"Found {len(evidence)} counter-sources for sub-claim {i+1}",
                data={"evidence": [e.model_dump() for e in evidence]},
            ))

    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_done",
            agent="counter_evidence_hunter",
            message=f"Counter-evidence search complete: {len(all_evidence)} sources found",
            data={"total": len(all_evidence)},
        ))

    return all_evidence


def _parse_tavily_results(raw) -> List[dict]:
    """Parse raw Tavily tool output into a list of dicts."""
    results = []
    try:
        if isinstance(raw, str):
            data = json.loads(raw)
        elif isinstance(raw, list):
            data = raw
        elif isinstance(raw, dict):
            data = raw.get("results", [raw])
        else:
            return []

        if isinstance(data, list):
            for item in data[:8]:
                if isinstance(item, dict):
                    results.append({
                        "title":   item.get("title", ""),
                        "url":     item.get("url", item.get("href", "")),
                        "snippet": item.get("content", item.get("snippet", item.get("description", ""))),
                        "source":  "tavily",
                    })
    except Exception:
        pass
    return results


async def _filter_counter_evidence(
    claim: str,
    raw_results: List[dict],
    llm,
) -> List[EvidenceItem]:
    """Use LLM to score and filter for genuine counter-evidence."""
    if not raw_results:
        return []

    results_text = json.dumps(raw_results, indent=2)
    messages = [
        SystemMessage(content=COUNTER_RELEVANCE_PROMPT),
        HumanMessage(content=f"Claim: {claim}\n\nSearch results:\n{results_text}")
    ]
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        data = json.loads(content)
        items = []
        for e in data.get("evidence", []):
            items.append(EvidenceItem(
                title=e.get("title", ""),
                url=e.get("url", ""),
                snippet=e.get("snippet", ""),
                source="tavily",
                relevance_score=float(e.get("relevance_score", 0.5)),
                evidence_type="counter",
            ))
        return items
    except Exception as ex:
        print(f"[CounterHunter] LLM filtering error: {ex}")
        # Fallback: return top raw results without LLM filtering
        return [
            EvidenceItem(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
                source="tavily",
                relevance_score=0.5,
                evidence_type="counter",
            )
            for r in raw_results[:3]
        ]
