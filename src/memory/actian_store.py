"""
Actian Vector DB — stores trial design fingerprints for similarity search.

Dual-mode:
  - real: Actian VectorAI (PostgreSQL + pgvector) when connection string is provided
  - memory: In-memory numpy-based store for hackathon / offline demo

When the agent evaluates a new design, it queries Actian for similar past designs.
Over time, the agent builds a rich memory of what works (and what doesn't)
across different diseases, endpoints, and sample sizes.
"""

from typing import Optional
import numpy as np
import os
import json

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
    Two modes:
      - memory://default  → in-memory numpy store (hackathon default)
      - postgresql://...  → Actian VectorAI via pgvector (production)

    The connection string is passed at init or read from ACTIAN_HOST env var.
    """

    def __init__(self, connection_string: str | None = None):
        self._connection_string = connection_string or os.getenv("ACTIAN_HOST", "memory://default")
        self._store: list[DesignFingerprint] = []
        self._embeddings: list[list[float]] = []
        self._pg_pool = None
        self._use_pg = self._connection_string.startswith("postgresql://")

        # Try connecting to VectorAI if configured
        if self._use_pg:
            self._init_pg()

    def _init_pg(self):
        """Attempt to connect to Actian VectorAI (PostgreSQL + pgvector)."""
        try:
            import asyncpg
            import asyncio
            # We'll lazily init the pool on first real call
            self._use_pg = True
        except ImportError:
            print("[Actian] asyncpg not installed — falling back to in-memory store. "
                  "Install with: pip install asyncpg")
            self._use_pg = False

    async def _get_pg(self):
        """Get a pgvector connection (lazy pool creation)."""
        if self._pg_pool is None and self._use_pg:
            try:
                import asyncpg
                self._pg_pool = await asyncpg.create_pool(
                    self._connection_string,
                    min_size=1,
                    max_size=3,
                )
                # Create extension + table if not exists
                async with self._pg_pool.acquire() as conn:
                    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS trial_designs (
                            id SERIAL PRIMARY KEY,
                            fingerprint_id TEXT UNIQUE,
                            disease_area TEXT,
                            endpoint TEXT,
                            treatment_effect REAL,
                            variability REAL,
                            n_per_arm INTEGER,
                            dropout_rate REAL,
                            exclusion_rate REAL,
                            power_achieved REAL,
                            is_viable BOOLEAN,
                            embedding vector(6),
                            created_at TIMESTAMP DEFAULT NOW()
                        )
                    """)
            except Exception as e:
                print(f"[Actian] VectorAI connection failed: {e}")
                print("[Actian] Falling back to in-memory store")
                self._use_pg = False
        return self._pg_pool

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

        if self._use_pg:
            try:
                pool = await self._get_pg()
                if pool:
                    async with pool.acquire() as conn:
                        fid = f"design_{len(self._store):05d}"
                        fingerprint.id = fid
                        await conn.execute("""
                            INSERT INTO trial_designs
                                (fingerprint_id, disease_area, endpoint, treatment_effect,
                                 variability, n_per_arm, dropout_rate, exclusion_rate,
                                 power_achieved, is_viable, embedding)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::vector)
                            ON CONFLICT (fingerprint_id) DO NOTHING
                        """,
                            fid,
                            fingerprint.disease_area,
                            fingerprint.endpoint,
                            fingerprint.treatment_effect,
                            fingerprint.variability,
                            fingerprint.n_per_arm,
                            fingerprint.dropout_rate,
                            fingerprint.exclusion_rate,
                            fingerprint.power_achieved,
                            fingerprint.is_viable,
                            str(embedding),
                        )
                        return fid
            except Exception:
                pass  # fall through to in-memory

        # In-memory fallback
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
