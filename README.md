# ⚡ OmniAgent AI — Autonomous Multi-Agent AI Platform

![OmniAgent Banner](https://img.shields.io/badge/OmniAgent_AI-Multi--Agent_System-7c3aed?style=for-the-badge&logo=openai&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestrator-blue?style=for-the-badge&logo=python&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_RAG-orange?style=for-the-badge)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.6_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)

OmniAgent AI is an advanced, autonomous **Multi-Agent Orchestration System** powered by **LangGraph**, **FastAPI**, **ChromaDB Vector Store**, **Google Gemini**, and **Local Ollama**. It routes user queries to specialized AI sub-agents, executes multi-agent workflows concurrently or sequentially, and synthesizes expert-level responses.

---

## 🚀 Key Features & Sub-Agent Team

### 🧠 1. Supervisor Agent (Orchestrator & Synthesizer)
- **Intelligent Routing**: Analyzes query intent and delegates tasks to one or more specialized sub-agents.
- **Multi-Agent Collaboration**: Runs multi-agent pipelines (e.g. `Web Search + Code Generation` or `RAG + Data Analytics`).
- **Response Synthesis**: Synthesizes insights from all sub-agents into clean, comprehensive Markdown outputs.

### 🌐 2. Web Search Agent (Internet Engine)
- Queries Tavily AI Search (primary) and DuckDuckGo + Wikipedia (fallback).
- Fetches real-time news, current events, biographies, and factual web data.

### 📄 3. Document RAG Agent (Vector Retrieval)
- Queries ChromaDB vector database using semantic embeddings.
- Summarizes uploaded PDFs, DOCX, XLSX, PPTX, and text documents with chunk citations.

### 💻 4. Code Agent (Polyglot Software Engineer)
- Generates, debugs, explains, and refactors Python, JavaScript, C++, Java, SQL, HTML/CSS.
- Integrates Python REPL execution tool for real-time code evaluation.

### 🔬 5. Academic Research Agent (Literature Review)
- Searches ArXiv research paper registry, Wikipedia encyclopedia, and scientific sources.
- Synthesizes academic literature reviews, methodologies, and paper abstracts.

### 📊 6. Data Analysis Agent (Analytics & Computation)
- Evaluates mathematical expressions, statistical metrics, CSV/Excel datasets, and tabular trends.

### 📄 7. Document Parser Agent (OCR & Layout Engine)
- Extracts text, tables, and document structures from PDF, DOCX, and image formats.

### 💾 8. Memory Agent (Conversational Context)
- Maintains session memory continuity, conversation history, and SQLite persistence.

---

## 🛠️ Additional Platform Capabilities

- 📤 **Chat Export (TXT & PDF)**: Export complete multi-agent conversations directly as `.txt` or printable `.pdf` files.
- 🎨 **Modern Glassmorphism UI**: Real-time LangGraph execution visualizer, sub-agent reasoning drawers, dark mode aesthetics, and responsive layout.
- 🔄 **Dual Provider Support**: Seamless switching between **Google Gemini (Cloud)** and **Ollama (Local LLM)**.
- 🔌 **Dual-Port Auto Failover**: Automatic frontend connection switching between port `8000` and `8001`.

---

## 🏗️ Project Architecture

```text
Multi-Agent Platform
├── backend/
│   └── app/
│       ├── agents/           # Specialized Agent Implementations (Supervisor, Code, RAG, Web, etc.)
│       ├── api/              # FastAPI v1 REST Endpoints (Auth, Chats, Docs, Agents)
│       ├── auth/             # JWT Authentication & Passlib Hashing
│       ├── config/           # Pydantic Settings & Environment Variables
│       ├── database/         # Async SQLAlchemy & SQLite Database Session
│       ├── graph/            # LangGraph Multi-Agent StateGraph Architecture
│       ├── llm/              # LLM Provider Factory (Gemini 3.6 Flash & Ollama)
│       ├── models/           # SQLAlchemy DB Schemas (User, Chat, Message, Document, Chunk)
│       ├── rag/              # ChromaDB Vectorstore, Chunking & Document Parser
│       ├── tools/            # Web Search (Tavily/DDG/Wiki/Arxiv), Python REPL, Calculator
│       └── utils/            # Logging & Robust LLM Content Extractor
├── frontend/
│   ├── index.html            # Main SPA Interface
│   ├── css/                  # Custom Modern Glassmorphic Styles
│   └── js/                   # SPA Controllers, App State, & API Client
├── docker-compose.yml        # Docker Container Deployment
├── Dockerfile                # Production Container Build
└── requirements.txt          # Python Dependencies
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- *(Optional)* **Ollama** installed locally for offline execution

### 2. Clone Repository & Install Dependencies
```bash
git clone https://github.com/manishPawar007/Multi-Agent-System.git
cd Multi-Agent-System

# Install Python requirements
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
PROJECT_NAME="OmniAgent AI"
ENVIRONMENT="development"
DEFAULT_LLM_PROVIDER="gemini"
DEFAULT_LLM_MODEL="gemini-3.6-flash"
GEMINI_API_KEY="your_google_gemini_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
DATABASE_URL="sqlite+aiosqlite:///./omniagent.db"
SECRET_KEY="your_jwt_secret_key"
OLLAMA_BASE_URL="http://localhost:11434"
```

### 4. Run Backend API Server
Run the FastAPI backend server from the project root directory:
```bash
python -m uvicorn backend.app.main:app --reload --port 8001
```

### 5. Access the Web Application
Open your browser and navigate to:
- **Web App**: `http://localhost:8001` or double click `frontend/index.html`
- **Swagger API Docs**: `http://localhost:8001/docs`

---

## 🧪 Testing Multi-Agent Execution

You can test multi-agent routing directly from Python:
```python
from backend.app.graph.multi_agent_graph import multi_agent_system

state = multi_agent_system.run(
    query="Search latest news on Python 3.13 and write a python script to test features",
    chat_id="session_1",
    user_id="user_1",
    provider="gemini",
    model="gemini-3.6-flash"
)

print("Execution Plan:", state["execution_plan"])
print("Final Synthesized Answer:\n", state["final_response"])
```

---

## 📄 License
This project is licensed under the **MIT License**.
