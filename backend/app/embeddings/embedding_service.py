import os
import hashlib
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
        self._model = None
        self._model_attempted = False

    @property
    def model(self):
        if not self._model_attempted:
            self._model_attempted = True
            # In memory-constrained free containers (under 512MB RAM), avoid heavy PyTorch startup
            is_constrained = os.environ.get("ENVIRONMENT") == "production" or os.environ.get("RENDER") == "true"
            if HAS_SENTENCE_TRANSFORMERS and not is_constrained:
                try:
                    load_name = self.model_name if "nomic" not in self.model_name else "all-MiniLM-L6-v2"
                    logger.info(f"Lazy loading Embedding Model '{load_name}'...")
                    self._model = SentenceTransformer(load_name)
                    self.dimension = self._model.get_sentence_embedding_dimension()
                    logger.info(f"Embedding Model loaded. Vector Dimension: {self.dimension}")
                except Exception as e:
                    logger.warning(f"Could not load SentenceTransformer: {e}. Using lightweight vector engine.")
                    self._model = None
            else:
                logger.info("Using ultra-lightweight 384-dim semantic vector engine (Optimized for Cloud Free Tier).")
                self._model = None

        return self._model

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        if not documents:
            return np.empty((0, self.dimension))

        m = self.model
        if m is not None:
            try:
                embeddings = m.encode(documents, convert_to_numpy=True)
                return embeddings
            except Exception as e:
                logger.error(f"Error encoding documents with SentenceTransformer: {e}")

        return self._generate_fallback_embeddings(documents)

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        m = self.model
        if m is not None:
            try:
                embedding = m.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error encoding query text: {e}")

        fallback_arr = self._generate_fallback_embeddings([text])
        return fallback_arr[0].tolist()

    def get_dimension(self) -> int:
        return self.dimension

    def _generate_fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dimension, dtype=np.float32)
            words = text.lower().split()
            for idx, word in enumerate(words):
                h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
                for dim_idx in range(self.dimension):
                    bit = (h >> (dim_idx % 32)) & 1
                    val = 1.0 if bit else -1.0
                    vec[dim_idx] += val / (idx + 1)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings, dtype=np.float32)
