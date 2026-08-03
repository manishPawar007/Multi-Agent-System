from typing import List, Any
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.document import DocumentResponse, DocumentDetailResponse
from backend.app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    doc = await DocumentService.process_and_save_upload(
        db=db,
        user_id=current_user.id,
        file_name=file.filename,
        file_bytes=contents,
        file_type=file.content_type
    )
    return doc

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await DocumentService.get_user_documents(db, current_user.id)

@router.get("/search")
async def search_vector_chunks(
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
) -> Any:
    return await DocumentService.search_chunks(query=query, limit=limit)

@router.get("/{doc_id}", response_model=DocumentDetailResponse)
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await DocumentService.get_document_details(db, doc_id, current_user.id)

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await DocumentService.delete_document(db, doc_id, current_user.id)
    return {"message": "Document and associated ChromaDB embeddings successfully removed"}
