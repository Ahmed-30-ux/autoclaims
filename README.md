# AutoClaims - AI-Powered Insurance Claims Processing

**Track:** Track 4: Autopilot Agent

AutoClaims is a production-grade multi-agent system that automates the entire insurance claims lifecycle — from intake to resolution — using Qwen Cloud models. It demonstrates sophisticated agent orchestration, human-in-the-loop workflows, and real-time pipeline visualization.

## Architecture

![Architecture Diagram](docs/architecture.png)

```
┌────────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                          │
│  Dashboard │ New Claim │ Claim Detail (React Flow) │ Reviews       │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────▼─────────────────────────────────────┐
│                      API Gateway (FastAPI)                         │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                    Agent Orchestrator                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Intake  │ │Validation│ │Assessment│ │  Review  │ │Resolution│  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Gate    │ │  Agent   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│       ▼            ▼            ▼            ▼            ▼         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     Qwen Cloud API                            │   │
│  │  qwen3.7-max (reasoning) │ qwen3.7-plus (vision) │ flash     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────┐
│                    Data Layer (SQLite / PostgreSQL)                 │
│  Claims │ Policies │ Human Reviews                                   │
└────────────────────────────────────────────────────────────────────┘
```

### Agents & Models

| Agent | Model | Responsibility |
|-------|-------|---------------|
| **Intake Agent** | `qwen3.7-plus` (vision) | Extracts structured data from raw claim submissions |
| **Validation Agent** | `qwen3.7-max` (reasoning) | Validates policy, coverage, and claimant identity |
| **Assessment Agent** | `qwen3.7-max` (reasoning) | Evaluates damage, estimates payout, assesses fraud risk |
| **Review Gate** | `qwen3.7-max` (reasoning) | Decides if human review is needed |
| **Resolution Agent** | `qwen3.6-flash` (speed) | Generates final resolution letters |

## Features

- **Multi-Agent Pipeline**: 5 specialized agents orchestrated by a supervisor
- **Qwen Cloud Integration**: Uses Qwen3.7-Max, Qwen3.7-Plus, and Qwen3.6-Flash
- **Human-in-the-Loop**: Claims flagged for review appear in a review dashboard
- **Real-Time Pipeline Visualization**: React Flow shows the claim's journey through each agent
- **Mock Policy Database**: Pre-seeded with test policies for demonstration
- **Production-Ready**: Clean architecture, error handling, async processing

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Qwen Cloud API key ([get one free](https://docs.qwencloud.com/resources/free-quota))

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your QWEN_API_KEY
python run.py          # Starts on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local  # Set NEXT_PUBLIC_API_URL
npm run dev                  # Starts on http://localhost:3000
```

### Demo Flow

1. Open http://localhost:3000
2. Click "New Claim" and fill in the form (use policy `POL-2026-001` for a valid policy)
3. Submit the claim
4. Click "Process" to run the AI pipeline
5. Watch the pipeline visualization update in real-time
6. If the claim is flagged, check the Reviews page
7. Approve or reject from the review dashboard

### Test Policies

| Policy Number | Holder | Type | Coverage |
|--------------|--------|------|----------|
| POL-2026-001 | Alice Johnson | Auto | $50,000 |
| POL-2026-002 | Bob Smith | Home | $300,000 |
| POL-2026-003 | Carol Davis | Health | $100,000 |
| POL-2026-004 | Daniel Lee | Travel | $50,000 |
| POL-2026-005 | Eve Martinez | Property | $200,000 |

## Tech Stack

- **Backend**: Python FastAPI, SQLite/PostgreSQL, OpenAI SDK (Qwen-compatible)
- **Frontend**: Next.js 16, TypeScript, Tailwind CSS, React Flow
- **AI**: Qwen Cloud (Qwen3.7-Max, Qwen3.7-Plus, Qwen3.6-Flash)
- **Deployment**: Alibaba Cloud ECS, Docker

## Submission

- **Track**: Autopilot Agent — Global AI Hackathon with Qwen Cloud
- **Deployed At**: Alibaba Cloud ECS (local proof available)
- **Demo Video**: [YouTube Link — coming soon]
- **Screenshots**: See `docs/screenshots/`
- **Architecture**: See `docs/architecture.svg`
- **License**: MIT

## Project Structure

```
autoclaims/
├── backend/            # FastAPI + SQLite + 5 AI Agents
│   ├── app/
│   │   ├── agents/     # Intake, Validation, Assessment, Review Gate, Resolution
│   │   ├── api/        # REST endpoints
│   │   ├── db/         # Database init, CRUD, migrations
│   │   └── services/   # Qwen Cloud client wrapper
│   ├── seed_demo.py    # Seed 9 demo claims
│   └── Dockerfile
├── frontend/           # Next.js 15 + React 19 + Tailwind
│   ├── src/app/        # Pages (dashboard, claim detail, new, reviews)
│   └── Dockerfile
├── deploy/             # ECS deploy script + proof generator
├── docs/               # Architecture diagram, screenshots, video script
└── docker-compose.yml
```
