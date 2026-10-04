<div align="center">

# 🔍 Devil's Advocate Research Agent

**An AI-powered multi-agent system that stress-tests any claim by researching both sides and scoring its credibility from 0 to 100.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-devil--advocate--sigma.vercel.app-6366f1?style=for-the-badge&logo=vercel)](https://devil-advocate-sigma.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://devil-advocate.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)

</div>

---

## 🎯 What It Does

You give it a claim. Any claim. The system fights itself.

Five specialized AI agents collaborate to research both sides — one hunts for supporting evidence, another plays devil's advocate and hunts for counter-arguments. The results are weighed against each other, scored, and synthesized into a full research report. **Everything streams live to your browser while the agents work.**

| Score Range | Verdict |
|-------------|---------|
| 80 – 100 | 🟢 **Strongly Supported** |
| 60 – 79 | 🟡 **Supported** |
| 40 – 59 | 🟠 **Contested** |
| 20 – 39 | 🔴 **Refuted** |
| 0 – 19 | ⛔ **Strongly Refuted** |

---

## ✨ Key Features

- **Multi-agent pipeline** — 5 specialized agents run in sequence via LangGraph
- **Adversarial search** — Counter-evidence agent uses negative query framing to find the strongest opposition
- **Real-time streaming** — Watch every agent work live via WebSocket connection
- **Weighted confidence scoring** — Deterministic math formula (no LLM subjectivity) with built-in skepticism bias
- **Full research report** — Markdown summary with all sources linked and scored by relevance
- **Research history** — All past queries saved and browsable
- **MCP-ready** — Tool loading via Model Context Protocol, with API fallbacks for reliability

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER SUBMITS CLAIM                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   1. Claim Decomposer   │
                    │  Breaks into 2-3 focused│
                    │      sub-claims         │
                    └───────────┬────────────┘
                                │
          ┌─────────────────────┴──────────────────────┐
          │                                             │
┌─────────▼────────────┐               ┌───────────────▼──────────┐
│  2. Pro-Evidence      │               │  3. Counter-Evidence      │
│     Hunter            │               │       Hunter              │
│  Tavily search with   │               │  Tavily with 2× adversarial│
│  supporting framing   │               │  query framing            │
└─────────┬────────────┘               └───────────────┬──────────┘
          │                                             │
          └─────────────────────┬───────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   4. Confidence Scorer  │
                    │  Weighted math formula  │
                    │  → 0 to 100 score       │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   5. Report Generator   │
                    │  Full markdown report   │
                    │  with verdict + sources │
                    └────────────────────────┘
```

### How Scoring Works

The score is a **deterministic formula** — no LLM involved, always reproducible:

```
pro_weight     = sum(relevance_score for each pro source)   × 1.0
counter_weight = sum(relevance_score for each counter source) × 1.2

score = (pro_weight / (pro_weight + counter_weight)) × 100
```

The **1.2 counter multiplier** is a deliberate skepticism bias — the system requires stronger evidence to be convinced than the average reader would.

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 + TypeScript | File-based routing, Vercel native |
| **Styling** | Tailwind CSS | Utility-first, rapid UI |
| **Backend** | FastAPI (Python 3.11) | Async-first, auto Swagger docs |
| **AI Orchestration** | LangGraph 0.2 | Stateful multi-agent graph execution |
| **LLM** | Groq (`openai/gpt-oss-20b`) | Fast inference, free tier |
| **Search** | Tavily API | AI-optimized web search |
| **Tool Protocol** | MCP (Model Context Protocol) | Extensible, plug-and-play tools |
| **Database** | SQLite + SQLAlchemy (async) | Zero-ops, persistent job history |
| **Streaming** | WebSocket | Real-time agent event streaming |
| **Deployment** | Vercel + Render | Free tier, zero config |

---

## 📁 Project Structure

```
research_agent/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py           # LangGraph pipeline — the brain
│   │   ├── llm_factory.py            # Provider-agnostic LLM (Groq/OpenAI/Anthropic)
│   │   ├── claim_decomposer.py       # Breaks claim → sub-claims
│   │   ├── pro_evidence_hunter.py    # Finds supporting evidence via Tavily
│   │   ├── counter_evidence_hunter.py# Adversarial counter-search via Tavily
│   │   ├── confidence_scorer.py      # Deterministic 0-100 scoring formula
│   │   └── report_generator.py       # Final markdown report
│   ├── api/
│   │   ├── jobs.py                   # REST API (create, list, get, delete jobs)
│   │   └── websocket.py              # WebSocket endpoint — streams agent events
│   ├── db/
│   │   ├── models.py                 # SQLAlchemy async models
│   │   └── schemas.py                # Pydantic schemas (EvidenceItem, StreamEvent, etc.)
│   ├── tools_client/
│   │   └── tool_loader.py            # MCP tool loader with API fallback
│   ├── config.py                     # Pydantic Settings — all env vars
│   ├── main.py                       # FastAPI app, CORS, lifespan
│   ├── runtime.txt                   # Python 3.11.9 (for Render)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx              # Homepage — claim input
│       │   ├── research/[jobId]/     # Live research page (WebSocket + agents)
│       │   └── history/              # Past research jobs
│       ├── lib/
│       │   ├── api.ts                # HTTP + WebSocket client helpers
│       │   └── utils.ts              # cn(), formatDate(), verdictColor()
│       └── types/index.ts            # TypeScript types matching backend schemas
├── mcp_config.json                   # MCP server definitions
├── .gitignore
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Groq API Key](https://console.groq.com) — free
- [Tavily API Key](https://tavily.com) — free tier (1000 searches/month)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/devils-advocate.git
cd devils-advocate/research_agent
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Open .env and fill in GROQ_API_KEY and TAVILY_API_KEY

# Start the server
uvicorn main:app --reload --port 8000
```

API is live at `http://localhost:8000` · Swagger docs at `http://localhost:8000/docs`

### 3. Frontend setup

```bash
# In a new terminal
cd frontend

npm install

cp .env.example .env.local
# .env.local values are pre-filled for local dev — no changes needed

npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
# LLM Provider
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b

# Search
TAVILY_API_KEY=your_tavily_api_key_here

# App
DATABASE_URL=sqlite+aiosqlite:///./devils_advocate.db
CORS_ORIGINS=http://localhost:3000
MCP_CONFIG_PATH=../mcp_config.json
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

> **Note:** For production use `wss://` (not `ws://`) for the WebSocket URL.

---

## ☁️ Deploy Your Own

### Backend → Render

1. Go to [render.com](https://render.com) → New Web Service → Connect GitHub repo
2. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Environment Variables (in Render dashboard):
   ```
   GROQ_API_KEY      = your_key
   TAVILY_API_KEY    = your_key
   LLM_PROVIDER      = groq
   LLM_MODEL         = openai/gpt-oss-20b
   CORS_ORIGINS      = https://your-app.vercel.app
   PYTHON_VERSION    = 3.11.9
   ```

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import repo
2. Set **Root Directory** to `frontend`
3. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.onrender.com
   NEXT_PUBLIC_WS_URL  = wss://your-backend.onrender.com
   ```
4. Deploy

> **Important:** After getting your Vercel URL, update `CORS_ORIGINS` on Render to that URL and redeploy the backend.

---

## 🧠 How the LLM is Used

The LLM plays a different role at each stage:

| Agent | LLM Task | Temperature |
|-------|----------|-------------|
| Claim Decomposer | JSON output — split claim into sub-claims | `0.0` (deterministic) |
| Pro Hunter | Filter search results for supporting evidence | `0.0` |
| Counter Hunter | Filter search results for counter-evidence | `0.0` |
| Confidence Scorer | **No LLM** — pure math formula | — |
| Report Generator | Write structured markdown report | `0.3` |

The LLM **never invents facts** — it only filters and evaluates real search results from Tavily.

---

## 🔒 Security

- API keys are stored only in `.env` files locally and platform dashboards — never in code
- `.gitignore` blocks all `.env*` files except `.env.example`
- All secrets are injected as OS environment variables at runtime on Render
- `.env.example` files contain only placeholder strings — safe to commit

---

## 📄 License

MIT — fork it, build on it, break it.
