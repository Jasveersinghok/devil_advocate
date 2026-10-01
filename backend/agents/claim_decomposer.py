"""
Claim Decomposer Agent
Breaks a research claim into max 3 focused sub-claims using an LLM.
"""
import json
from typing import List, AsyncGenerator
from langchain_core.messages import HumanMessage, SystemMessage
from agents.llm_factory import get_llm
from db.schemas import StreamEvent, SubClaim


SYSTEM_PROMPT = """You are a research analyst specializing in claim decomposition.
Your job is to break down a complex claim into 2-3 precise, testable sub-claims.

Rules:
- Output ONLY valid JSON — no markdown, no extra text
- Each sub-claim must be independently verifiable
- Sub-claims should cover different aspects of the main claim
- Keep sub-claims concise (max 2 sentences each)
- Maximum 3 sub-claims

Output format:
{
  "sub_claims": [
    "Sub-claim 1 text",
    "Sub-claim 2 text",
    "Sub-claim 3 text"
  ]
}"""


async def decompose_claim(
    claim: str,
    stream_callback=None
) -> List[str]:
    """
    Decompose a claim into sub-claims.
    
    Args:
        claim: The main claim to decompose
        stream_callback: Optional async callable to stream progress events
        
    Returns:
        List of sub-claim strings (max 3)
    """
    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_start",
            agent="claim_decomposer",
            message=f"Decomposing claim into sub-claims...",
        ))

    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Decompose this claim into 2-3 testable sub-claims:\n\n{claim}")
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        data = json.loads(content)
        sub_claims = data.get("sub_claims", [])[:3]

        # Ensure we always have at least the original claim
        if not sub_claims:
            sub_claims = [claim]

    except Exception as e:
        print(f"[ClaimDecomposer] Error parsing LLM response: {e}")
        # Fallback: use the original claim as a single sub-claim
        sub_claims = [claim]

    if stream_callback:
        await stream_callback(StreamEvent(
            event="agent_done",
            agent="claim_decomposer",
            message=f"Found {len(sub_claims)} sub-claims",
            data={"sub_claims": sub_claims},
        ))

    return sub_claims
