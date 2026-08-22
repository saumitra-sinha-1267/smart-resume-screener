import math
from typing import List, Optional, Union
import numpy as np

_EMBEDDING_MODEL = None

def get_sentence_transformer_model():
    """Loads and caches the SentenceTransformer all-MiniLM-L6-v2 model singleton."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not initialize SentenceTransformer ('all-MiniLM-L6-v2'): {e}")
            _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL

class SentenceEmbedder:
    """Encodes texts into dense vector embeddings using all-MiniLM-L6-v2 and computes cosine similarity."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = get_sentence_transformer_model()

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encodes single string or list of strings into normalized dense numpy embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                return np.asarray(embeddings, dtype=np.float32)
            except Exception as e:
                print(f"SentenceTransformer encoding error: {e}")

        dim = 384
        vectors = []
        for t in texts:
            vec = np.zeros(dim, dtype=np.float32)
            words = t.lower().split()
            for w in words:
                h = abs(hash(w)) % dim
                vec[h] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    def get_vector(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Computes cosine similarity between two normalized 1D dense vectors."""
        if vec1 is None or vec2 is None or len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        v1 = vec1.flatten()
        v2 = vec2.flatten()
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        sim = float(np.dot(v1, v2) / (norm1 * norm2))
        return max(0.0, min(1.0, sim))

SemanticVectorizer = SentenceEmbedder
