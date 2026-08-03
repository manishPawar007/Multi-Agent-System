from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    vector_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    chunks: List[ChunkResponse] = []
