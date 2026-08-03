import os
import numpy as np
from typing import List, Optional
from backend.app.config.settings import settings
from backend.app.utils.logger import logger

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    SentenceTransformer = None
    HAS_SENTENCE_TRANSFORMERS = False

class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL or "all-MiniLM-L6-v2"
        self.dimension = 384
        self.model = None

        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Use lightweight sentence transformer model
                load_name = self.model_name if "nomic" not in self.model_name else "all-MiniLM-L6-v2"
                logger.info(f"Loading Embedding Model '{load_name}'...")
                self.model = SentenceTransformer(load_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Embedding Model '{load_name}' loaded. Vector Dimension: {self.dimension}")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Using deterministic embedding fallback.")
                self.model = None

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        if not documents:
            return np.empty((0, self.dimension))

        if self.model is not None:
            try:
                embeddings = self.model.encode(documents, convert_to_numpy=True)
                return embeddings
            except Exception as e:
                logger.error(f"Error encoding documents with SentenceTransformer: {e}")

        # Deterministic fallback embedding generator
        return self._generate_fallback_embeddings(documents)

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        if self.model is not None:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error encoding query text: {e}")

        fallback_arr = self._generate_fallback_embeddings([text])
        return fallback_arr[0].tolist()

    def get_dimension(self) -> int:
        return self.dimension

    def _generate_fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generates normalized deterministic feature vectors when neural embedding models are offline."""
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dimension, dtype=np.float32)
            words = text.lower().split()
            for idx, word in enumerate(words):
                h = hash(word) % self.dimension
                vec[h] += 1.0 / (idx + 1.0)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings)
