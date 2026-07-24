"""
Tests for the agent and memory layers.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

from src.simulation.models import TrialDesignRequest
from src.memory.actian_store import ActianStore
from src.communication.band import BandRoom
from src.inference.pioneer import PioneerClient
from src.agent.trial_architect import TrialArchitect


def test_actian_store_store_and_count():
    """Actian store should store fingerprints and report count."""
    store = ActianStore()
    assert store.count() == 0

    request = TrialDesignRequest(
        disease_area="Hypertension",
        endpoint="SBP",
        expected_effect=10,
        variability=15,
        n_per_arm=100,
    )

    # Store a design via the agent (uses ActianStore under the hood)
    async def _run():
        band = BandRoom()
        pioneer = PioneerClient()
        agent = TrialArchitect(memory=store, band=band, pioneer=pioneer)
        result = await agent.evaluate_design(request)
        return result

    asyncio.run(_run())
    assert store.count() == 1, f"Expected 1 design stored, got {store.count()}"


def test_actian_store_search_similar_empty():
    """Search on an empty store should return empty list."""
    store = ActianStore()
    request = TrialDesignRequest(
        disease_area="Diabetes",
        endpoint="HbA1c",
        expected_effect=5,
        variability=10,
        n_per_arm=200,
    )
    results = store.search_similar(request)
    assert results == []


def test_actian_store_search_similar_returns_results():
    """After storing designs, similar ones should be found."""
    store = ActianStore()
    band = BandRoom()
    pioneer = PioneerClient()
    agent = TrialArchitect(memory=store, band=band, pioneer=pioneer)

    async def _run():
        # Store a hypertension design
        req1 = TrialDesignRequest(
            disease_area="Hypertension",
            endpoint="SBP", expected_effect=10, variability=15, n_per_arm=100,
        )
        await agent.evaluate_design(req1)

        # Store a diabetes design
        req2 = TrialDesignRequest(
            disease_area="Diabetes",
            endpoint="HbA1c", expected_effect=5, variability=10, n_per_arm=200,
        )
        await agent.evaluate_design(req2)

        # Search for something similar to hypertension
        query = TrialDesignRequest(
            disease_area="Hypertension",
            endpoint="SBP", expected_effect=8, variability=15, n_per_arm=120,
        )
        similar = store.search_similar(query, top_k=3, threshold=0.5)
        assert len(similar) >= 1, f"Expected at least 1 similar, got {len(similar)}"
        assert similar[0].disease_area == "Hypertension"

    asyncio.run(_run())


def test_band_tracks_escalations():
    """Band room should track how many escalations happened."""
    band = BandRoom()
    assert band.total_rooms_opened == 0

    async def _run():
        await band.escalate(
            title="Test escalation",
            message="Something needs human review",
            suggested_action="Review the design",
        )
        assert band.total_rooms_opened == 1

        await band.escalate(
            title="Another one",
            message="More issues found",
        )
        assert band.total_rooms_opened == 2

        log = band.get_log()
        assert len(log) == 4  # 2 escalations + 2 responses

    asyncio.run(_run())
