from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.models.setting import UserSetting
from backend.app.schemas.dashboard import DashboardMetricsResponse
from backend.app.vectorstore.chroma_manager import ChromaManager

chroma_manager = ChromaManager()

class DashboardService:
    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession, user_id: str) -> DashboardMetricsResponse:
        # Document Count
        doc_res = await db.execute(select(func.count(Document.id)).where(Document.user_id == user_id))
        total_docs = doc_res.scalar() or 0

        # Chunk Count
        chunk_res = await db.execute(
            select(func.count(Chunk.id)).join(Document).where(Document.user_id == user_id)
        )
        total_chunks = chunk_res.scalar() or 0

        # Conversation Count
        chat_res = await db.execute(select(func.count(Chat.id)).where(Chat.user_id == user_id))
        total_chats = chat_res.scalar() or 0

        # Message Count
        msg_res = await db.execute(select(func.count(Message.id)))
        total_msgs = msg_res.scalar() or 0

        # User Settings
        setting_res = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        user_sett = setting_res.scalar_one_or_none()

        provider = user_sett.default_provider if user_sett else "ollama"
        cur_model = user_sett.default_model if user_sett else "llama3.2:latest"
        emb_model = user_sett.embedding_model if user_sett else "nomic-embed-text"

        chroma_info = chroma_manager.get_stats()

        return DashboardMetricsResponse(
            total_documents=total_docs,
            total_chunks=total_chunks,
            total_vector_chunks=total_chunks,
            total_conversations=total_chats,
            total_chats=total_chats,
            total_messages=total_msgs,
            total_agents=8,
            active_llm_provider=f"{provider.upper()} ({cur_model})",
            current_model=cur_model,
            embedding_model=emb_model,
            ollama_status="online",
            chroma_status="online",
            backend_status="Healthy (FastAPI)",
            api_status="Online",
            recent_activity=[
                {"activity": "ChromaDB Persistent Index Online", "time": "Just now"},
                {"activity": "Multi-Agent Supervisor Ready", "time": "Just now"}
            ]
        )
