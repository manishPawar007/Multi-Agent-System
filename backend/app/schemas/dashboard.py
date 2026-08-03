from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DashboardMetricsResponse(BaseModel):
    total_documents: int = 0
    total_chunks: int = 0
    total_vector_chunks: int = 0
    total_conversations: int = 0
    total_chats: int = 0
    total_messages: int = 0
    total_agents: int = 8
    active_llm_provider: str = "ollama"
    current_model: str = "llama3.2:latest"
    embedding_model: str = "nomic-embed-text"
    ollama_status: str = "online"
    chroma_status: str = "online"
    backend_status: str = "Healthy (FastAPI)"
    api_status: str = "Online"
    recent_activity: List[Dict[str, Any]] = []
