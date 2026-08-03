import uuid
from typing import List, Dict, Any
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

    def retrieve_context(self, query: str, k: int = 4) -> str:
        results = self.chroma_manager.similarity_search(query, k=k)
        if not results:
            return "No relevant document context found."

        formatted_contexts = []
        for idx, res in enumerate(results, 1):
            source = res.get("metadata", {}).get("filename", "Unknown Document")
            text = res.get("content", "")
            score = res.get("score", 0.0)
            formatted_contexts.append(f"[Source {idx}: {source} (Relevance: {score:.2f})]\n{text}")

        return "\n\n".join(formatted_contexts)
