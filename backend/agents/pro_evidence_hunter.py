"""
Pro-Evidence Hunter Agent
Searches for supporting evidence for each sub-claim using Tavily + Semantic Scholar.
"""
import json
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_factory import get_llm
from db.schemas import EvidenceItem, StreamEvent
from tools_client.tool_loader import get_tavily_tools, get_semantic_scholar_tools


RELEVANCE_PROMPT = """You are a research assistant evaluating search results.
Given a claim and search results, extract the most relevant pieces of evidence 
that SUPPORT the claim. Return ONLY valid JSON.

Output format:
{
  "evidence": [
    {
      "title": "Article title",
      "url": "https://...",
      "snippet": "Relevant quote or summary (2-3 sentences)",
      "relevance_score": 0.85
    }
  ]
}

Rules:
- Include only evidence that genuinely supports the claim
- relevance_score is 0.0-1.0
- Maximum 5 evidence items
- If no supporting evidence found, return {"evidence": []}"""


async def hunt_pro_evidence(
    sub_claims: List[str],
    stream_callback=None,
) -> List[EvidenceItem]:
    """
    Search for evidence that supports the given sub-claims.
    
    Args:
        sub_claims: List of sub-claims to find evidence for
        stream_callback: Optional async callable for streaming progress
        
    Returns:
        List of EvidenceItem objects with pro evidence
    """
    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="pro_evidence_hunter",
            message="Searching for supporting evidence...",
        ))

    all_evidence: List[EvidenceItem] = []
    tavily_tools = await get_tavily_tools()
    scholar_tools = await get_semantic_scholar_tools()
    llm = get_llm(temperature=0.0)

    for i, sub_claim in enumerate(sub_claims):
        if stream_callback:
            await stream_callback(StreamEvent(
                event="agent_start",
                agent="pro_evidence_hunter",
                message=f"Searching for support: '{sub_claim[:80]}...'",
            ))

        # Search with Tavily
        tavily_results = []
        if tavily_tools:
            try:
                tool = tavily_tools[0]
                raw = await tool.ainvoke({"query": f"evidence supporting: {sub_claim}"})
                tavily_results = _parse_search_results(raw, source="tavily")
            except Exception as e:
                print(f"[ProHunter] Tavily error: {e}")

        # Search with Semantic Scholar for academic backing
        scholar_results = []
        if scholar_tools:
            try:
                tool = scholar_tools[0]
                raw = await tool.ainvoke({"query": sub_claim})
                scholar_results = _parse_search_results(raw, source="semantic-scholar")
            except Exception as e:
                print(f"[ProHunter] Scholar error: {e}")

        combined_results = tavily_results + scholar_results
        if not combined_results:
            continue

        # Use LLM to filter and score relevance
        evidence = await _filter_evidence(
            claim=sub_claim,
            raw_results=combined_results,
            evidence_type="pro",
            llm=llm,
        )
        all_evidence.extend(evidence)

        if stream_callback and evidence:
            await stream_callback(StreamEvent(
                event="evidence_found",
                agent="pro_evidence_hunter",
                message=f"Found {len(evidence)} supporting sources for sub-claim {i+1}",
                data={"evidence": [e.model_dump() for e in evidence]},
            ))

    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_done",
            agent="pro_evidence_hunter",
            message=f"Pro-evidence search complete: {len(all_evidence)} sources found",
            data={"total": len(all_evidence)},
        ))

    return all_evidence


def _parse_search_results(raw, source: str) -> List[dict]:
    """Parse raw search tool output into list of dicts."""
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
                        "title": item.get("title", ""),
                        "url": item.get("url", item.get("href", "")),
                        "snippet": item.get("content", item.get("snippet", item.get("abstract", ""))),
                        "source": source,
                    })
    except Exception:
        pass
    return results


async def _filter_evidence(
    claim: str,
    raw_results: List[dict],
    evidence_type: str,
    llm,
) -> List[EvidenceItem]:
    """Use LLM to score and filter evidence relevance."""
    if not raw_results:
        return []

    results_text = json.dumps(raw_results, indent=2)
    messages = [
        SystemMessage(content=RELEVANCE_PROMPT),
        HumanMessage(content=f"Claim: {claim}\n\nSearch results:\n{results_text}")
    ]
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
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
                source=e.get("source", raw_results[0].get("source", "tavily")),
                relevance_score=float(e.get("relevance_score", 0.5)),
                evidence_type=evidence_type,
            ))
        return items
    except Exception as ex:
        print(f"[ProHunter] LLM filtering error: {ex}")
        # Return raw results as evidence items without filtering
        return [
            EvidenceItem(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
                source=r.get("source", "tavily"),
                relevance_score=0.5,
                evidence_type=evidence_type,
            )
            for r in raw_results[:3]
        ]
