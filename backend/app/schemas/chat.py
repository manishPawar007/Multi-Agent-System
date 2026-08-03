from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ChatCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    provider: Optional[str] = None
    model: Optional[str] = None

class ChatUpdate(BaseModel):
    title: Optional[str] = None

class MessageCreate(BaseModel):
    chat_id: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender_role: str
    content: str
    agent_name: Optional[str] = "supervisor"
    metadata_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    id: str
    user_id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True
