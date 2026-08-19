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
- **Security & Rate Limiting**: Built-in JWT authentication, Bcrypt password hashing, CORS protection, and 120 req/min rate limiter.

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

## 🔍 Sub-Agent Capabilities & Prompt Engineering

### 1. Supervisor Agent (Planner & Router)
Analyses incoming user queries to decide whether a single agent or a sequence of sub-agents is required.
- **Multi-Agent Mode**: If a prompt asks for news and code (e.g. *"Find latest Python 3.13 features and write code"*), it generates plan `['web_search_agent', 'code_agent']`.
- **Synthesis Engine**: Merges distinct sub-agent responses into a cohesive, structured Markdown answer without raw text duplication.

### 2. Document RAG Agent
Manages vector document retrieval using ChromaDB.
- **Chunking Strategy**: Recursive character text splitting with 1000 character chunk size and 200 character overlap.
- **Semantic Retrieval**: Top-k similarity vector retrieval with source chunk metadata attribution.

### 3. Code Agent & Python REPL Sandbox
Handles code generation, explanation, and live code testing.
- **Supported Languages**: Python, JavaScript, TypeScript, C++, Java, SQL, HTML/CSS, Rust.
- **Execution Sandbox**: Runs Python snippets inside a safe runtime environment to verify code logic before producing outputs.

### 4. Web Search & Academic Research Agents
Combines real-time web indexers with scientific database registries.
- **Tavily AI Engine**: Fetches structured web search summaries.
- **ArXiv API Integration**: Fetches research paper abstracts, author credits, and published dates.

---

## 💡 Example Interactive Use Cases

### Scenario A: Multi-Agent Search & Code Generation
- **User Query**: *"Search for the latest features introduced in Python 3.13 and write a python script to benchmark them."*
- **Execution Plan**: `['web_search_agent', 'code_agent']`
- **Output**: Detailed release summary of Python 3.13 (JIT compiler, free-threaded GIL) followed by an executable benchmark code block.

### Scenario B: PDF Document RAG Query
- **User Query**: *"Summarize key financial projections from page 3 of the uploaded Q4 report."*
- **Execution Plan**: `['rag_agent']`
- **Output**: Extracted semantic vector chunks with page citations and structured bullet point summaries.

### Scenario C: Academic Literature Synthesis
- **User Query**: *"Find recent ArXiv research papers on Transformer Attention Mechanisms and summarize their findings."*
- **Execution Plan**: `['research_agent']`
- **Output**: Literature review summarizing recent ArXiv papers with arXiv paper IDs and publication years.

---

## 🔄 Multi-Agent Workflow Execution Flow

```text
1. User Prompt Submission
   │
   ▼
2. Supervisor Agent Intent Analysis & Planning
   │
   ├── [Plan Generated]: ['web_search_agent', 'code_agent']
   │
3. Parallel / Sequential Sub-Agent Execution
   ├── web_search_agent ──> (Queries Tavily AI & DuckDuckGo APIs)
   └── code_agent       ──> (Generates & validates code via REPL Sandbox)
   │
4. Response Synthesis
   └── Supervisor Agent merges findings into unified Markdown output
   │
5. Persistence & Delivery
   └── Saves message to SQLite & streams rendered response to Web UI
```

---

## 🏗 System Architecture & Component Breakdown

### 📊 End-to-End System Pipeline Diagram

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT LAYER (SPA WEB UI)                                     │
│  - Vanilla JS Single Page Application (Glassmorphic Dark Theme)                                  │
│  - Dynamic Provider Status Badges & Dual-Port Auto Resolution (8000 ↔ 8001)                      │
│  - Interactive LangGraph Node Visualizer & Real-time Reasoning Logs Drawer                       │
│  - Chat Export Modules (Export to TXT & Print/PDF Renderer)                                     │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ HTTP / REST API (JSON)
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FASTAPI BACKEND ROUTER LAYER                                   │
│  - Middleware: CORS Security, Rate Limiter (120 req/min), Logging Middleware                     │
│  - Authentication: JWT Access Tokens, Passlib Bcrypt Hashing                                     │
│  - REST Controllers: /api/v1/auth, /api/v1/chats, /api/v1/documents, /api/v1/agents              │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ State Graph Invocation
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             LANGGRAPH MULTI-AGENT SUPERVISOR ENGINE                              │
│                                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 1. SUPERVISOR PLANNER: Analyzes query & creates plan: ['web_search', 'code', 'rag']      │   │
│   └────────────────────────────────────────────┬─────────────────────────────────────────────┘   │
│                                                │                                                 │
│        ┌───────────────────────────────────────┼───────────────────────────────────────┐         │
│        ▼                                       ▼                                       ▼         │
│  ┌───────────┐                           ┌───────────┐                           ┌───────────┐   │
│  │Web Search │                           │ Document  │                           │   Code    │   │
│  │   Agent   │                           │ RAG Agent │                           │   Agent   │   │
│  └─────┬─────┘                           └─────┬─────┘                           └─────┬─────┘   │
│        │                                       │                                       │         │
│        ▼                                       ▼                                       ▼         │
│  (Tavily / DDG / Wiki)                   (ChromaDB Vector Store)                (Python REPL Sandbox)│
│        │                                       │                                       │         │
│        └───────────────────────────────────────┼───────────────────────────────────────┘         │
│                                                │ Sub-Agent Output Collection                     │
│                                                ▼                                                 │
│   ┌──────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 2. SUPERVISOR SYNTHESIZER: Merges agent outputs into unified Markdown answer             │   │
│   └──────────────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PERSISTENCE & LLM PROVIDER LAYER                                 │
│  - Database: Async SQLite (aiosqlite) with SQLAlchemy ORM (Chats, Messages, Docs, Users)        │
│  - LLM Factory: Google Gemini API (gemini-3.6-flash) & Ollama Local LLMs (LLaMA 3.2, Qwen 2.5)   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 🧱 Architectural Layer Breakdown

1. **User Interface (Presentation Layer)**:
   - Built as a zero-dependency, ultra-fast Single Page Application (SPA) using HTML5, Vanilla JavaScript (ES6+), and CSS3.
   - Features modern glassmorphism aesthetics, real-time node execution visualizer, and dynamic status badges that auto-detect model providers and server ports.

2. **API & Security Layer (FastAPI Router)**:
   - Asynchronous ASGI server endpoints providing JWT authentication, passlib bcrypt password hashing, CORS security, and 120 req/min rate limiting.
   - Handles static file mounting, multi-part file uploads, and session management.

3. **Orchestration Layer (LangGraph StateGraph)**:
   - State Graph Engine that controls execution state passing between agents using standard Python dictionaries (`AgentState`).
   - The Supervisor Agent plans execution pathways dynamically, ensuring optimal resource usage and high response quality.

4. **Execution Nodes (Specialized Sub-Agent Team)**:
   - **Supervisor Agent**: Plans agent routing and synthesizes output.
   - **Web Search Agent**: Queries Tavily AI, DuckDuckGo, and Wikipedia.
   - **Document RAG Agent**: Performs semantic vector searches in ChromaDB.
   - **Code Agent**: Generates, refactors, and evaluates code via Python REPL.
   - **Research Agent**: Fetches arXiv papers and literature summaries.
   - **Data Analysis Agent**: Performs math and tabular analytics.
   - **Document Parser**: OCR layout parser for multi-format files.
   - **Memory Agent**: Session context continuity engine.

5. **Storage & Provider Layer**:
   - **Vector Store**: ChromaDB persistent vector database storing document chunk embeddings.
   - **Relational DB**: SQLite database using async SQLAlchemy ORM.
   - **LLM Provider Factory**: Universal wrapper supporting Google Gemini API (`gemini-3.6-flash`) and local Ollama server (`http://localhost:11434`).

---

## 💻 Technical Stack

### Backend Architecture
- **Language**: Python 3.10+
- **Framework**: FastAPI (Asynchronous REST API)
- **Orchestration Engine**: LangGraph, LangChain Core
- **LLM Provider Factory**: Google Gemini API (`gemini-3.6-flash`), Ollama (Local LLaMA 3.2 / Qwen 2.5)
- **Vector Database**: ChromaDB (Persistent Embeddings Store)
- **Database ORM**: SQLite with Async SQLAlchemy & aiosqlite
- **Security**: PyJWT, Passlib (Bcrypt hashing), Rate Limiting Middleware

### Frontend Architecture
- **Structure**: Single Page Application (HTML5, Vanilla JavaScript ES6+)
- **Design System**: Glassmorphism dark-theme layout (Vanilla CSS3)
- **Real-Time Visualizer**: Interactive LangGraph execution node inspector & sub-agent drawer

---

## ⚙️ Environment Configuration Matrix

| Variable | Default Value | Required | Description |
| :--- | :--- | :---: | :--- |
| `PROJECT_NAME` | `"OmniAgent AI"` | No | Application display title |
| `ENVIRONMENT` | `"development"` | No | Deployment mode (`development`/`production`) |
| `DEFAULT_LLM_PROVIDER` | `"gemini"` | Yes | Default provider (`gemini` or `ollama`) |
| `DEFAULT_LLM_MODEL` | `"gemini-3.6-flash"` | Yes | Selected LLM model string |
| `GEMINI_API_KEY` | `""` | Yes* | Google Gemini API key (*required for Gemini provider) |
| `TAVILY_API_KEY` | `""` | No | Tavily search API key (falls back to DDG & Wikipedia) |
| `DATABASE_URL` | `"sqlite+aiosqlite:///./omniagent.db"` | Yes | Async database connection URL |
| `SECRET_KEY` | `"supersecretkey"` | Yes | JWT token signing secret key |
| `OLLAMA_BASE_URL` | `"http://localhost:11434"` | No | Local Ollama server endpoint |

---

## 🚀 Quick Start Guide

### 1. Repository Setup
```bash
git clone https://github.com/manishPawar007/Multi-Agent-System.git
cd Multi-Agent-System
```

### 2. Environment Setup
Create a `.env` file in the root directory:

```env
PROJECT_NAME="OmniAgent AI"
ENVIRONMENT="development"
DEBUG=True

# LLM Configurations
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
Launch the backend server from the root directory:
```bash
python -m uvicorn backend.app.main:app --reload --port 8001
```

Access the application at `http://localhost:8001` or open `frontend/index.html` in your web browser.

---

## 🐳 Docker Container Deployment

To launch the system inside containerized Docker services:

```bash
# Build and run containers
docker-compose up --build -d

# Check running container status
docker-compose ps

# Stream application logs
docker-compose logs -f
```

---

## 📡 API Endpoints Specification

| Method | Endpoint | Description | Sample Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account | `{"email": "user@example.com", "password": "secretpassword"}` |
| `POST` | `/api/v1/auth/login` | Authenticate & get JWT token | `{"username": "user@example.com", "password": "secretpassword"}` |
| `GET` | `/api/v1/auth/me` | Fetch active user profile | Header: `Authorization: Bearer <token>` |
| `GET` | `/api/v1/chats` | List user chat conversations | Header: `Authorization: Bearer <token>` |
| `POST` | `/api/v1/chats` | Initialize new chat session | `{"title": "Python 3.13 Research"}` |
| `POST` | `/api/v1/chats/messages` | **Send prompt to Multi-Agent Engine** | `{"chat_id": "...", "content": "Search news and write code"}` |
| `POST` | `/api/v1/documents/upload` | Upload file & index in ChromaDB | `Multipart FormData (file: document.pdf)` |
| `GET` | `/api/v1/documents` | List uploaded documents | Returns document metadata & chunk counts |
| `GET` | `/api/v1/agents` | View status of sub-agents | Returns status array of 8 sub-agents |
| `GET` | `/api/v1/dashboard/stats` | System analytics & health stats | Returns doc counts, message stats, & provider status |

---

## 📄 Python Programmatic Usage Example

You can invoke the Multi-Agent engine directly in your Python code:

```python
from backend.app.graph.multi_agent_graph import multi_agent_system

# Run Multi-Agent Execution Graph
state = multi_agent_system.run(
    query="Search for recent news on quantum computing and write a python summary",
    chat_id="demo_session_1",
    user_id="user_demo",
    provider="gemini",
    model="gemini-3.6-flash"
)

# Inspect execution graph output
print("Execution Plan Created by Supervisor:", state["execution_plan"])
print("Sub-Agent Outputs Keys:", list(state["agent_outputs"].keys()))
print("\n--- Final Synthesized Response ---\n")
print(state["final_response"])
```

---

## 🛠 Troubleshooting Common Setup Issues

- **Backend Port Auto-Detection**: The backend defaults to port `8001`. The frontend contains automatic dual-port detection (`8000` & `8001`) to automatically resolve connection errors when opening `index.html`.
- **Gemini Model 404 Error**: Ensure your `.env` model string uses `gemini-3.6-flash` as deprecated model endpoints (`gemini-1.5-flash`) have been sunset by Google API.
- **Ollama Offline Fallback**: If using local Ollama models, ensure the Ollama service is running via `ollama serve` before selecting Ollama models in the frontend dropdown.

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
