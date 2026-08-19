# OmniAgent AI — Autonomous Multi-Agent AI System

OmniAgent AI is an enterprise-grade autonomous Multi-Agent AI platform built with Python, FastAPI, LangGraph, ChromaDB Vector RAG, Google Gemini, and Ollama. It automatically orchestrates complex user queries across a team of specialized AI agents—ranging from real-time web search and document RAG to python code execution and academic research.

---

## 🌟 Key Capabilities

- **Autonomous Supervisor Orchestrator**: Dynamically plans, routes, and synthesizes multi-agent execution graphs using LangGraph.
- **Multi-Agent Delegation**: Executes multi-agent workflows (e.g. Web Search + Code Generation + Data Analytics) in parallel or sequence.
- **Document Hub & Vector RAG**: Semantic vector retrieval powered by ChromaDB for querying uploaded PDF, DOCX, XLSX, and text documents.
- **Real-Time Web Search**: Integrated search using Tavily AI, DuckDuckGo, and Wikipedia for up-to-date factual info.
- **Academic Literature Research**: Direct ArXiv academic paper abstracts and Wikipedia encyclopedia search.
- **Code Execution Engine**: Python REPL sandbox for live script execution and polyglot code generation (Python, JS, C++, Java, SQL).
- **Chat Export (TXT & PDF)**: Export full conversation history with agent insights as plain text or printable PDF.
- **Dual LLM Provider System**: Supports Google Gemini (Gemini 3.6 Flash / Pro) and local Ollama models with automatic fallback.

---

## 🤖 Specialized AI Agent Team

| Agent Name | Role | Capabilities | Primary Tools |
| :--- | :--- | :--- | :--- |
| **Supervisor Agent** | Master Orchestrator | Graph planning, multi-agent routing, and insight synthesis | LangGraph, LLM Provider Factory |
| **Web Search Agent** | Real-time Web Engine | Live news, biographies, current events, and web summaries | Tavily AI, DuckDuckGo, Wikipedia |
| **Document RAG Agent** | Vector Knowledge QA | Document chunk retrieval, semantic QA, and PDF summaries | ChromaDB, Nomic Embeddings, PDF Parser |
| **Code Agent** | Software Engineer | Polyglot code generation, refactoring, and script execution | Python REPL, Syntax Formatter |
| **Research Agent** | Academic Researcher | Scientific papers, methodologies, and literature reviews | ArXiv Registry, Wikipedia API |
| **Data Analysis Agent** | Data Analyst | Statistical analysis, tabular metrics, and CSV processing | Calculator, Pandas |
| **Document Parser** | Structure Specialist | Layout parsing, OCR text extraction, and metadata parsing | OCR Engine, PyPDF, Office Parsers |
| **Memory Agent** | Context Engine | Conversation continuity, short-term memory, & session history | SQLite Database, Async SQLAlchemy |

---

## 🏗 System Architecture

```text
                                 [ User Query ]
                                       │
                                       ▼
                             [ Frontend Web Interface ]
                                       │
                                       ▼
                             [ FastAPI Backend API ]
                                       │
                                       ▼
                       [ LangGraph Supervisor Orchestrator ]
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
 [ Web Search Agent ]        [ Document RAG Agent ]         [ Code Agent ]
         │                             │                             │
   (Tavily / DDG)             (ChromaDB Vector DB)          (Python REPL Sandbox)
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       │
                                       ▼
                      [ Supervisor Response Synthesizer ]
                                       │
                                       ▼
                          [ Final Response to User ]
```

---

## 💻 Technical Stack

### Backend & AI Architecture
- **Language**: Python 3.10+
- **Framework**: FastAPI (Asynchronous REST API)
- **Orchestration**: LangGraph, LangChain Core
- **LLM Engine**: Google Gemini API (`gemini-3.6-flash`), Ollama (Local LLaMA 3.2 / Qwen 2.5)
- **Vector Database**: ChromaDB (Persistent Vector Store)
- **Database**: SQLite with Async SQLAlchemy & aiosqlite

### Frontend & UI
- **Structure**: Single Page Application (HTML5, Vanilla JavaScript ES6+)
- **Styling**: Glassmorphism dark-theme design system (Vanilla CSS3)
- **Interactions**: Real-time agent execution visualizer & reasoning log drawer

---

## 🚀 Quick Start Guide

### 1. Repository Setup
```bash
git clone https://github.com/manishPawar007/Multi-Agent-System.git
cd Multi-Agent-System
```

### 2. Environment Configuration
Create a `.env` file in the root folder with the following configuration:

```env
PROJECT_NAME="OmniAgent AI"
ENVIRONMENT="development"
DEBUG=True

# LLM Providers
DEFAULT_LLM_PROVIDER="gemini"
DEFAULT_LLM_MODEL="gemini-3.6-flash"
GEMINI_API_KEY="your_google_gemini_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"

# Database & Security
DATABASE_URL="sqlite+aiosqlite:///./omniagent.db"
SECRET_KEY="your_secret_key_here"
OLLAMA_BASE_URL="http://localhost:11434"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Server
Launch the backend server from the project root:
```bash
python -m uvicorn backend.app.main:app --reload --port 8001
```

Access the application at `http://localhost:8001` or open `frontend/index.html` in your web browser.

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account |
| `POST` | `/api/v1/auth/login` | User login and token authentication |
| `GET` | `/api/v1/auth/me` | Retrieve user profile information |
| `GET` | `/api/v1/chats` | List user conversation threads |
| `POST` | `/api/v1/chats` | Initialize new chat conversation |
| `POST` | `/api/v1/chats/messages` | Process query through Multi-Agent system |
| `POST` | `/api/v1/documents/upload` | Upload document & index into ChromaDB |
| `GET` | `/api/v1/documents` | List uploaded RAG documents |
| `GET` | `/api/v1/agents` | View status of active sub-agents |
| `GET` | `/api/v1/dashboard/stats` | View system analytics & model status |

---

## 📂 Project Directory Structure

```text
Multi-Agent-System/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph specialized sub-agents
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── auth/            # Authentication & JWT security
│   │   ├── config/          # Environment configuration
│   │   ├── database/        # Async SQLite session manager
│   │   ├── graph/           # Multi-agent graph pipeline
│   │   ├── llm/             # Gemini 3.6 Flash & Ollama providers
│   │   ├── models/          # Database ORM models
│   │   ├── rag/             # Vector database & document processing
│   │   ├── schemas/         # Request & response validation
│   │   ├── services/        # Service layer logic
│   │   ├── tools/           # Web search, Python REPL, & calculator tools
│   │   └── utils/           # Logging & text extraction helpers
│   ├── chroma_db/           # Persistent vector database storage
│   └── uploads/             # Uploaded PDF/Office documents
├── frontend/
│   ├── index.html           # Main user interface
│   ├── css/                 # Glassmorphic styles
│   └── js/                  # App controllers & API client
├── docker-compose.yml       # Docker deployment configuration
├── Dockerfile               # Production build manifest
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

---

## 👤 Author & License

- **Developer**: Manish Pawar (manishPawar007)
- **Repository**: Multi-Agent-System
- **License**: MIT License
