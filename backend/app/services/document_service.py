import os
import uuid
from typing import List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk
from backend.app.rag.pipeline import RAGPipeline
from backend.app.config.settings import settings
from backend.app.utils.exceptions import EntityNotFoundError

rag_pipeline = RAGPipeline()

class DocumentService:
    @staticmethod
    async def process_and_save_upload(db: AsyncSession, user_id: str, file_name: str, file_bytes: bytes, file_type: str) -> Document:
        doc_id = str(uuid.uuid4())
        user_upload_dir = settings.UPLOAD_DIR / user_id
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        saved_file_path = user_upload_dir / f"{doc_id}_{file_name}"
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)

        # Create Document record
        doc = Document(
            id=doc_id,
            user_id=user_id,
            filename=file_name,
            file_path=str(saved_file_path),
            file_type=file_type or Path(file_name).suffix,
            file_size=len(file_bytes),
            status="processing"
        )
        db.add(doc)
        await db.commit()

        # Run RAG indexing pipeline with ChromaDB
        rag_res = rag_pipeline.process_and_index_document(doc_id, str(saved_file_path), user_id)

        # Save chunks in database
        chunks_data = rag_res.get("chunks", [])
        vector_ids = rag_res.get("vector_ids", [])

        for idx, chunk_text in enumerate(chunks_data):
            chunk_rec = Chunk(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                chunk_index=idx,
                content=chunk_text,
                vector_id=vector_ids[idx] if idx < len(vector_ids) else None
            )
            db.add(chunk_rec)

        doc.status = "indexed"
        doc.chunk_count = len(chunks_data)
        await db.commit()
        await db.refresh(doc)

        return doc

    @staticmethod
    async def get_user_documents(db: AsyncSession, user_id: str) -> List[Document]:
        res = await db.execute(select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_document_details(db: AsyncSession, doc_id: str, user_id: str) -> Document:
        res = await db.execute(
            select(Document).options(selectinload(Document.chunks)).where(Document.id == doc_id, Document.user_id == user_id)
        )
        doc = res.scalar_one_or_none()
        if not doc:
            raise EntityNotFoundError("Document")
        return doc

    @staticmethod
    async def delete_document(db: AsyncSession, doc_id: str, user_id: str) -> bool:
        doc = await DocumentService.get_document_details(db, doc_id, user_id)

        # Delete ChromaDB vectors
        try:
            rag_pipeline.chroma_manager.delete_document(doc_id)
        except Exception:
            pass

        # Remove file on disk if exists
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        await db.delete(doc)
        await db.commit()
        return True

    @staticmethod
    async def search_chunks(query: str, limit: int = 5) -> List[dict]:
        results = rag_pipeline.chroma_manager.similarity_search(query, k=limit)
        return results
