from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/agents", tags=["Multi-Agents"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_agents(current_user: User = Depends(get_current_user)):
    return [
        {"id": "supervisor", "name": "Supervisor Agent", "type": "Orchestrator", "description": "Controls graph flow, routes requests, monitors retries & aggregates responses.", "status": "active"},
        {"id": "research", "name": "Research Agent", "type": "Academic & Web", "description": "Searches Wikipedia, Arxiv, GitHub, DuckDuckGo.", "status": "active"},
        {"id": "rag", "name": "RAG Agent", "type": "Retrieval QA", "description": "Queries ChromaDB vector database and synthesizes document context.", "status": "active"},
        {"id": "document", "name": "Document Agent", "type": "Parser & OCR", "description": "Parses PDF, DOCX, XLSX, PPTX, Images via Tesseract/EasyOCR & extracts metadata.", "status": "active"},
        {"id": "code", "name": "Code Agent", "type": "Developer", "description": "Generates, debugs, explains, and refactors Python, Java, JS, SQL, HTML, CSS.", "status": "active"},
        {"id": "data_analysis", "name": "Data Analysis Agent", "type": "Analytics", "description": "Analyzes tabular data, calculates statistics, detects trends & builds reports.", "status": "active"},
        {"id": "web_search", "name": "Web Search Agent", "type": "Internet Engine", "description": "Executes real-time web queries, ranks snippets, and summarizes links.", "status": "active"},
        {"id": "memory", "name": "Memory Agent", "type": "Context Engine", "description": "Maintains short-term chat memory, long-term summaries, and SQLite history.", "status": "active"}
    ]
