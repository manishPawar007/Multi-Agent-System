from typing import Optional
from pydantic import BaseModel

class UserSettingUpdate(BaseModel):
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    embedding_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    gemini_key: Optional[str] = None
    ollama_url: Optional[str] = None

class UserSettingResponse(BaseModel):
    id: str
    user_id: str
    default_provider: str
    default_model: str
    embedding_model: str
    temperature: float
    max_tokens: int
    top_p: float
    gemini_key: Optional[str] = None
    ollama_url: Optional[str] = None

    class Config:
        from_attributes = True
