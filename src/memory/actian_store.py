"""
Actian Vector DB — stores trial design fingerprints for similarity search.

When the agent evaluates a new design, it queries Actian for similar past designs.
Over time, the agent builds a rich memory of what works (and what doesn't)
across different diseases, endpoints, and sample sizes.
"""

from typing import Optional
import numpy as np

from src.simulation.models import TrialDesignRequest, DesignFingerprint


# Simplified embedding: treat design parameters as a feature vector.
# In production, you'd use a learned embedding model.
def _embed_design(request: TrialDesignRequest) -> list[float]:
    """Create a simple feature vector from design parameters."""
    # Normalize each parameter to ~0-1 range
    return [
        request.expected_effect / 100.0,           # treatment effect (cap at 100)
        request.variability / 50.0,                 # variability
        request.n_per_arm / 500.0,                  # sample size
        request.alpha * 20,                         # significance (0.05 → 1.0)
        request.dropout_rate,                       # already 0-1
        request.estimated_exclusion_rate,            # already 0-1
    ]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    norm = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / norm)


class ActianStore:
    """
    Vector store for trial design fingerprints.

    Wraps the Actian portable vector database.
    For hackathon: in-memory store. In production: Actian edge/cloud.
    """

    def __init__(self, connection_string: str | None = None):
        self._connection_string = connection_string or "memory://default"
        self._store: list[DesignFingerprint] = []
        self._embeddings: list[list[float]] = []

    def count(self) -> int:
        return len(self._store)

    async def store(self, fingerprint: DesignFingerprint) -> str:
        """Store a design fingerprint and return its ID."""
        embedding = _embed_design(
            TrialDesignRequest(
                disease_area=fingerprint.disease_area,
                endpoint=fingerprint.endpoint,
                expected_effect=fingerprint.treatment_effect,
                variability=fingerprint.variability,
                n_per_arm=fingerprint.n_per_arm,
                dropout_rate=fingerprint.dropout_rate,
                estimated_exclusion_rate=fingerprint.exclusion_rate,
            )
        )
        fingerprint.embedding = embedding
        fingerprint.id = f"design_{len(self._store):05d}"

        self._store.append(fingerprint)
        self._embeddings.append(embedding)
        return fingerprint.id

    def search_similar(
        self,
        request: TrialDesignRequest,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[DesignFingerprint]:
        """Find past trial designs similar to the given request."""
        if not self._store:
            return []

        query_embedding = _embed_design(request)

        # Compute similarities
        similarities = [
            _cosine_similarity(query_embedding, emb)
            for emb in self._embeddings
        ]

        # Get top-k above threshold
        indexed = sorted(
            enumerate(similarities),
            key=lambda x: x[1],
            reverse=True,
        )
        results = []
        for idx, sim in indexed:
            if sim >= threshold and len(results) < top_k:
                results.append(self._store[idx])

        return results

    def get_all(self) -> list[DesignFingerprint]:
        """Return all stored designs (for demo/visualization)."""
        return list(self._store)
