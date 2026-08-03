import uuid
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from backend.app.models.chat import Chat
from backend.app.models.message import Message
from backend.app.models.setting import UserSetting
from backend.app.schemas.chat import ChatCreate, MessageCreate
from backend.app.graph.multi_agent_graph import multi_agent_system
from backend.app.utils.exceptions import EntityNotFoundError

class ChatService:
    @staticmethod
    async def create_chat(db: AsyncSession, user_id: str, chat_data: ChatCreate) -> Chat:
        res = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        user_sett = res.scalar_one_or_none()

        provider = chat_data.provider or (user_sett.default_provider if user_sett else settings.DEFAULT_LLM_PROVIDER)
        model = chat_data.model or (user_sett.default_model if user_sett else settings.DEFAULT_LLM_MODEL)

        chat = Chat(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=chat_data.title or "New Conversation",
            provider=provider,
            model=model
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        chat.messages = []
        return chat

    @staticmethod
    async def get_user_chats(db: AsyncSession, user_id: str, search: Optional[str] = None) -> List[Chat]:
        query = select(Chat).options(selectinload(Chat.messages)).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
        if search:
            query = query.where(Chat.title.ilike(f"%{search}%"))
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_chat_by_id(db: AsyncSession, chat_id: str, user_id: str) -> Chat:
        result = await db.execute(
            select(Chat).options(selectinload(Chat.messages)).where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        chat = result.scalar_one_or_none()
        if not chat:
            raise EntityNotFoundError("Chat conversation")
        return chat

    @staticmethod
    async def delete_chat(db: AsyncSession, chat_id: str, user_id: str) -> bool:
        chat = await ChatService.get_chat_by_id(db, chat_id, user_id)
        await db.delete(chat)
        await db.commit()
        return True

    @staticmethod
    async def process_user_message(db: AsyncSession, user_id: str, message_data: MessageCreate) -> Message:
        chat = await ChatService.get_chat_by_id(db, message_data.chat_id, user_id)

        # 1. Save user message
        user_msg = Message(
            id=str(uuid.uuid4()),
            chat_id=chat.id,
            sender_role="user",
            content=message_data.content,
            agent_name="user"
        )
        db.add(user_msg)
        await db.flush()

        # Update chat title if default
        if chat.title == "New Conversation":
            chat.title = message_data.content[:30] + ("..." if len(message_data.content) > 30 else "")

        if message_data.provider:
            chat.provider = message_data.provider
        if message_data.model:
            chat.model = message_data.model

        setting_res = await db.execute(select(UserSetting).where(UserSetting.user_id == user_id))
        user_setting = setting_res.scalar_one_or_none()

        # 2. Invoke LangGraph Multi-Agent Engine
        graph_state = multi_agent_system.run(
            query=message_data.content,
            chat_id=chat.id,
            user_id=user_id,
            provider=chat.provider,
            model=chat.model,
            user_settings=user_setting
        )

        final_response_text = graph_state.get("final_response", "Agent response generated.")
        agent_outputs = graph_state.get("agent_outputs", {})

        meta_payload = {
            "execution_plan": graph_state.get("execution_plan", []),
            **agent_outputs
        }

        # 3. Save Assistant Message
        assistant_msg = Message(
            id=str(uuid.uuid4()),
            chat_id=chat.id,
            sender_role="assistant",
            content=final_response_text,
            agent_name="supervisor",
            metadata_json=json.dumps(meta_payload)
        )
        db.add(assistant_msg)

        await db.commit()
        await db.refresh(assistant_msg)
        return assistant_msg
