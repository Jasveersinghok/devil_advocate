# Devil's Advocate Research Agent

A multi-agent research system that analyzes claims by finding both supporting and counter evidence, then generating a confidence-scored report.

## Architecture

```
research_agent/
├── backend/          # FastAPI + LangGraph agents
│   ├── agents/       # Individual agent modules
│   ├── db/           # SQLite models & migrations
│   ├── mcp/          # MCP tool loading
│   └── api/          # FastAPI routes + WebSocket
├── frontend/         # Next.js + Tailwind + shadcn/ui
└── mcp_config.json   # MCP server configuration
```

## Quick Start

### 1. Configure MCP servers
Edit `mcp_config.json` and add your API keys.

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # add your API keys
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
See `backend/.env.example` for required keys:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `TAVILY_API_KEY`
- `BRAVE_API_KEY`

## MCP Servers Used
- **mcp-tavily** — primary web search
- **mcp-brave-search** — adversarial counter-evidence search  
- **mcp-semantic-scholar** — academic paper lookup
