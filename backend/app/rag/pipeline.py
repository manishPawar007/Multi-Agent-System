import uuid
from typing import List, Dict, Any, Optional
from backend.app.rag.parser import DocumentParser
from backend.app.rag.chunker import TextChunker
from backend.app.vectorstore.chroma_manager import ChromaManager
from backend.app.utils.logger import logger

class RAGPipeline:
    def __init__(self, chroma_manager: ChromaManager = None):
        self.chroma_manager = chroma_manager or ChromaManager()

    def process_and_index_document(self, document_id: str, file_path: str, user_id: str) -> Dict[str, Any]:
        logger.info(f"RAG Pipeline: Processing document {document_id} at {file_path}")

        # 1. Parse Document
        raw_text, meta = DocumentParser.parse_file(file_path)

        # 2. Chunk Text
        chunks = TextChunker.chunk_text(raw_text, chunk_size=400, chunk_overlap=50)
        if not chunks:
            chunks = [raw_text or "Empty document."]

        # 3. Create Metadatas for vector store
        chunk_metadatas = []
        for idx, chunk_str in enumerate(chunks):
            chunk_metadatas.append({
                "document_id": str(document_id),
                "user_id": str(user_id),
                "chunk_index": idx,
                "filename": meta.get("filename", "")
            })

        # 4. Embed & Store in ChromaDB
        vector_ids = self.chroma_manager.add_documents(chunks, chunk_metadatas)

        logger.info(f"RAG Pipeline: Successfully indexed {len(chunks)} chunks in ChromaDB for document {document_id}")

        return {
            "document_id": document_id,
            "raw_text": raw_text,
            "chunks": chunks,
            "vector_ids": vector_ids,
            "chunk_count": len(chunks),
            "metadata": meta
        }

    def retrieve_context(
        self,
        query: str,
        k: int = 6,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        filter_meta = {}
        if document_id:
            filter_meta["document_id"] = str(document_id)
        if user_id:
            filter_meta["user_id"] = str(user_id)

        # If query is a general summary request, retrieve main introduction/overview chunks
        search_query = query
        if any(w in query.lower() for w in ["summary", "summarize", "summerize", "summarise", "summery", "explain", "overview"]):
            search_query = "document main topic introduction overview key points executive summary content"

        results = self.chroma_manager.similarity_search(
            query=search_query,
            k=k,
            filter_metadata=filter_meta if filter_meta else None
        )

        if not results and filter_meta:
            # Fallback search without query embedding constraint to get any chunks for the target document
            results = self.chroma_manager.similarity_search(
                query="content introduction",
                k=k,
                filter_metadata=filter_meta
            )

        if not results:
            return "No relevant document context found in ChromaDB vector index."

        formatted_contexts = []
        for idx, res in enumerate(results, 1):
            source = res.get("metadata", {}).get("filename", "Uploaded Document")
            text = res.get("content", "")
            score = res.get("score", 0.0)
            formatted_contexts.append(f"[Document Chunk {idx} (Source: {source})]\n{text}")

        return "\n\n".join(formatted_contexts)
