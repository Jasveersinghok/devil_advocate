import asyncio
from agents.orchestrator import run_research_pipeline

async def main():
    report = await run_research_pipeline("test-123", "Coffee is good for you")
    print(f"Pro: {len(report.pro_evidence)}")
    print(f"Counter: {len(report.counter_evidence)}")

if __name__ == "__main__":
    asyncio.run(main())
