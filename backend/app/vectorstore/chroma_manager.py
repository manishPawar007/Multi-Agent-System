import os
import uuid
import chromadb
from typing import List, Dict, Any, Optional
from backend.app.config.settings import settings
from backend.app.embeddings.embedding_service import EmbeddingService
from backend.app.utils.logger import logger

class ChromaManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaManager, cls).__new__(cls)
            cls._instance.client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
            cls._instance.embedding_service = EmbeddingService()
            cls._instance.collection_name = "omniagent_documents"
            cls._instance.collection = cls._instance.client.get_or_create_collection(
                name=cls._instance.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB persistent client at {settings.CHROMA_DIR}")
        return cls._instance

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        if not documents:
            return []

        embeddings = self.embedding_service.embed_documents(documents).tolist()
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        if metadatas is None:
            metadatas = [{}] * len(documents)

        # Chroma metadata keys must be simple primitives
        clean_metadatas = []
        for meta in metadatas:
            clean_m = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_m[k] = v
                else:
                    clean_m[k] = str(v)
            clean_metadatas.append(clean_m)

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=clean_metadatas,
            ids=ids
        )
        logger.info(f"Added {len(documents)} document chunks to ChromaDB collection '{self.collection_name}'")
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        count = self.collection.count()
        if count == 0:
            return []

        query_embedding = self.embedding_service.embed_text(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, max(1, count)),
            where=filter_metadata if filter_metadata else None
        )

        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

            for doc, meta, dist, doc_id in zip(docs, metas, distances, ids):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "score": float(1.0 - dist) if dist is not None else 1.0,
                    "id": doc_id
                })

        return formatted_results

    def delete_document(self, doc_id: str):
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id} from ChromaDB: {e}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection_name,
            "vector_dimension": self.embedding_service.get_dimension()
        }
