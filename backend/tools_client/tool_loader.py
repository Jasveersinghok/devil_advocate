"""
MCP Tool Loader
Loads tools from MCP servers defined in mcp_config.json using langchain-mcp-adapters.
Falls back to direct Tavily API if MCP servers are unavailable.
"""
import json
import os
import asyncio
from pathlib import Path
from typing import List, Optional
from langchain_core.tools import BaseTool
from config import get_settings

settings = get_settings()


def load_mcp_config() -> dict:
    """Load MCP server configuration from mcp_config.json."""
    config_path = Path(settings.mcp_config_path)
    if not config_path.exists():
        # Try relative to this file
        config_path = Path(__file__).parent.parent.parent / "mcp_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"mcpServers": {}}


async def get_tavily_tools() -> List[BaseTool]:
    """Load Tavily MCP tools or fall back to direct TavilySearchResults."""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        config = load_mcp_config()
        tavily_cfg = config.get("mcpServers", {}).get("mcp-tavily")
        if tavily_cfg:
            client = MultiServerMCPClient({"mcp-tavily": tavily_cfg})
            tools = await client.get_tools()
            return tools
    except Exception as e:
        print(f"[MCP] Tavily MCP unavailable, falling back to direct API: {e}")

    # Fallback: direct Tavily tool via langchain_community
    # Must inject the key into os.environ because TavilySearchResults reads it from there
    try:
        import os
        from langchain_community.tools.tavily_search import TavilySearchResults
        os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
        return [TavilySearchResults(max_results=5)]
    except Exception as e:
        print(f"[MCP] Tavily fallback also failed: {e}")
        return []


async def get_brave_tools() -> List[BaseTool]:
    """Load Brave Search MCP tools."""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        config = load_mcp_config()
        brave_cfg = config.get("mcpServers", {}).get("mcp-brave-search")
        if brave_cfg:
            client = MultiServerMCPClient({"mcp-brave-search": brave_cfg})
            tools = await client.get_tools()
            return tools
    except Exception as e:
        print(f"[MCP] Brave MCP unavailable: {e}")
    return []


async def get_semantic_scholar_tools() -> List[BaseTool]:
    """Load Semantic Scholar MCP tools."""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        config = load_mcp_config()
        ss_cfg = config.get("mcpServers", {}).get("mcp-semantic-scholar")
        if ss_cfg:
            client = MultiServerMCPClient({"mcp-semantic-scholar": ss_cfg})
            tools = await client.get_tools()
            return tools
    except Exception as e:
        print(f"[MCP] Semantic Scholar MCP unavailable: {e}")
    return []


async def get_all_search_tools() -> dict:
    """Return dict of all available search tools."""
    tavily, brave, scholar = await asyncio.gather(
        get_tavily_tools(),
        get_brave_tools(),
        get_semantic_scholar_tools(),
    )
    return {
        "tavily": tavily,
        "brave": brave,
        "semantic_scholar": scholar,
    }
