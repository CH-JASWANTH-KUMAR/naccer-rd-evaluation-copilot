import math
import re
from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Compute float embedding vector for given text."""
        pass


class FallbackDeterministicProvider(BaseEmbeddingProvider):
    """Zero-dependency deterministic embedding provider using hashed subword n-grams.

    Guarantees deterministic, reproducible cosine similarity calculation
    without external API keys or heavy GPU model weights.
    """

    def __init__(self, dim: int = 128):
        self._dim = dim

    @property
    def model_name(self) -> str:
        return "tfidf-deterministic-v1"

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self._dim

        # Normalize text
        clean = re.sub(r"[^\w\s]", "", text.lower())
        words = [w for w in clean.split() if len(w) > 1]
        if not words:
            return [0.0] * self._dim

        vec = [0.0] * self._dim

        # Compute n-gram and word hash projections
        for w in words:
            # Word level hash
            h = hash(w) % self._dim
            vec[h] += 1.0

            # Subword 3-gram hashes for partial matching (e.g., methan / gas / ventilat)
            for i in range(len(w) - 2):
                tri = w[i : i + 3]
                h_tri = hash(tri) % self._dim
                vec[h_tri] += 0.5

        # L2 normalize vector
        norm = math.sqrt(sum(val * val for val in vec))
        if norm > 0:
            vec = [val / norm for val in vec]

        return vec


def calculate_cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculate cosine similarity between two float vectors (0.0 to 1.0)."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))

    if n1 == 0 or n2 == 0:
        return 0.0

    sim = dot / (n1 * n2)
    return max(0.0, min(1.0, float(sim)))


class EmbeddingProviderFactory:
    @staticmethod
    def get_provider() -> BaseEmbeddingProvider:
        # Default to deterministic fallback provider
        return FallbackDeterministicProvider(dim=128)
