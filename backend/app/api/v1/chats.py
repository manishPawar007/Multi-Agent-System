from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from backend.app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChatService.create_chat(db, current_user.id, chat_data)

@router.get("", response_model=List[ChatResponse])
async def list_chats(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChatService.get_user_chats(db, current_user.id, search)

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChatService.get_chat_by_id(db, chat_id, current_user.id)

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await ChatService.delete_chat(db, chat_id, current_user.id)
    return {"message": "Chat conversation successfully deleted"}

@router.post("/messages", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ChatService.process_user_message(db, current_user.id, message_data)
