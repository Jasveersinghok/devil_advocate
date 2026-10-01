# 🔍 Devil's Advocate Research Agent

> **Stress-test any claim with AI.** A multi-agent system that researches both sides of any claim — finding supporting evidence and adversarial counter-arguments — then scores it with a 0–100 confidence rating.

**🌐 Live Demo:** [devil-advocate-sigma.vercel.app](https://devil-advocate-sigma.vercel.app)

---

## ✨ Features

- **Multi-agent pipeline** — Specialized AI agents work in parallel to research your claim
- **Real-time streaming** — Watch agents work live via WebSocket connection
- **Adversarial search** — Two different counter-evidence framings hunt for weaknesses in any claim
- **Confidence scoring** — Weighted pro vs. counter evidence produces a 0–100 credibility score
- **Full research report** — Markdown summary with verdict (Strongly Supported → Strongly Refuted)
- **Research history** — All past queries saved and browsable

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────────┐
                        │         User submits a claim         │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │      Claim Decomposer Agent          │
                        │  Breaks claim into 2-3 sub-claims   │
                        └────────────┬────────────────────────┘
                                     │
               ┌─────────────────────┴──────────────────────┐
               │                                            │
               ▼                                            ▼
  ┌────────────────────────┐                 ┌────────────────────────┐
  │  Pro-Evidence Hunter   │                 │ Counter-Evidence Hunter │
  │  Tavily search with    │                 │ Tavily search with 2x  │
  │  supporting framing    │                 │ adversarial framing    │
  └────────────┬───────────┘                 └───────────┬────────────┘
               │                                         │
               └─────────────────┬───────────────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────┐
                  │   Confidence Scorer       │
                  │  Weighted relevance score │
                  │  → 0–100 final rating     │
                  └──────────────┬───────────┘
                                 │
                                 ▼
                  ┌──────────────────────────┐
                  │    Report Generator       │
                  │  Full markdown analysis  │
                  │  with verdict + sources  │
                  └──────────────────────────┘
```

### Score Interpretation

| Score | Verdict |
|-------|---------|
| 80–100 | 🟢 Strongly Supported |
| 60–79 | 🟡 Supported |
| 40–59 | 🟠 Contested |
| 20–39 | 🔴 Refuted |
| 0–19 | ⛔ Strongly Refuted |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11 |
| **AI Orchestration** | LangGraph (multi-agent state machine) |
| **LLM** | Groq (`openai/gpt-oss-20b`) |
| **Search** | Tavily API |
| **Database** | SQLite + SQLAlchemy (async) |
| **Streaming** | WebSocket (real-time agent events) |
| **Deployment** | Vercel (frontend) + Render (backend) |

---

## 📁 Project Structure

```
research_agent/
├── backend/
│   ├── agents/
│   │   ├── claim_decomposer.py       # Breaks claim into sub-claims
│   │   ├── pro_evidence_hunter.py    # Finds supporting evidence
│   │   ├── counter_evidence_hunter.py# Adversarial counter-search
│   │   ├── confidence_scorer.py      # Computes 0-100 score
│   │   ├── report_generator.py       # Generates markdown report
│   │   ├── orchestrator.py           # LangGraph pipeline coordinator
│   │   └── llm_factory.py            # LLM provider abstraction
│   ├── api/
│   │   ├── jobs.py                   # REST endpoints (CRUD)
│   │   └── websocket.py              # WebSocket streaming
│   ├── db/
│   │   ├── models.py                 # SQLAlchemy models
│   │   └── schemas.py                # Pydantic schemas
│   ├── tools_client/
│   │   └── tool_loader.py            # Tavily search tool loader
│   ├── config.py                     # Settings from env
│   ├── main.py                       # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx              # Home / claim input
│       │   ├── research/[jobId]/     # Live research page
│       │   └── history/              # Past research jobs
│       ├── lib/
│       │   ├── api.ts                # Backend API client
│       │   └── utils.ts              # Helpers
│       └── types/                    # TypeScript types
└── .gitignore
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Groq API Key](https://console.groq.com) (free)
- [Tavily API Key](https://tavily.com) (free tier)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# → Fill in your GROQ_API_KEY and TAVILY_API_KEY

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
# → Values are already set for local dev

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
DATABASE_URL=sqlite+aiosqlite:///./devils_advocate.db
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## ☁️ Deployment

| Service | Platform | Notes |
|---------|----------|-------|
| Backend | [Render](https://render.com) | Free tier, set `PYTHON_VERSION=3.11.9` |
| Frontend | [Vercel](https://vercel.com) | Free tier, auto-detects Next.js |

Set `CORS_ORIGINS=https://your-app.vercel.app` on Render after deploying the frontend.
For production WebSocket, use `wss://` instead of `ws://`.

---

## 📄 License

feel free to fork and build on it.
