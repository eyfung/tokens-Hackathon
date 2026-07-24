"""
Seed Actian memory with realistic trial designs for the demo.

This gives the agent an immediate "self-evolving" narrative — it already
has learned patterns when the demo starts, so users can see it make
intelligent recommendations from the first interaction.
"""

from src.simulation.models import DesignFingerprint


SEED_DESIGNS = [
    DesignFingerprint(
        id="seed_000",
        disease_area="Hypertension",
        endpoint="Systolic BP Reduction",
        n_per_arm=120,
        treatment_effect=8,
        variability=14,
        dropout_rate=0.10,
        exclusion_rate=0.05,
        power_achieved=0.72,
        is_viable=False,
        risk_flags=["Low power (72.0% vs target 80%)"],
    ),
    DesignFingerprint(
        id="seed_001",
        disease_area="Hypertension",
        endpoint="Systolic BP Reduction",
        n_per_arm=200,
        treatment_effect=8,
        variability=14,
        dropout_rate=0.10,
        exclusion_rate=0.05,
        power_achieved=0.88,
        is_viable=True,
        risk_flags=[],
    ),
    DesignFingerprint(
        id="seed_002",
        disease_area="Type 2 Diabetes",
        endpoint="HbA1c Reduction",
        n_per_arm=150,
        treatment_effect=0.8,
        variability=1.2,
        dropout_rate=0.15,
        exclusion_rate=0.08,
        power_achieved=0.79,
        is_viable=False,
        risk_flags=["Low power (79.0% vs target 80%)", "High dropout rate (15%)"],
    ),
    DesignFingerprint(
        id="seed_003",
        disease_area="Type 2 Diabetes",
        endpoint="HbA1c Reduction",
        n_per_arm=220,
        treatment_effect=0.8,
        variability=1.2,
        dropout_rate=0.12,
        exclusion_rate=0.08,
        power_achieved=0.91,
        is_viable=True,
        risk_flags=[],
    ),
    DesignFingerprint(
        id="seed_004",
        disease_area="Non-Small Cell Lung Cancer",
        endpoint="Progression-Free Survival",
        n_per_arm=180,
        treatment_effect=0.35,  # hazard ratio
        variability=0.5,
        dropout_rate=0.08,
        exclusion_rate=0.12,
        power_achieved=0.68,
        is_viable=False,
        risk_flags=["Low power (68.0% vs target 80%)", "High exclusion rate (12%)"],
    ),
    DesignFingerprint(
        id="seed_005",
        disease_area="Non-Small Cell Lung Cancer",
        endpoint="Progression-Free Survival",
        n_per_arm=320,
        treatment_effect=0.35,
        variability=0.5,
        dropout_rate=0.08,
        exclusion_rate=0.10,
        power_achieved=0.85,
        is_viable=True,
        risk_flags=[],
    ),
    DesignFingerprint(
        id="seed_006",
        disease_area="Alzheimer's Disease",
        endpoint="ADAS-Cog Score Change",
        n_per_arm=250,
        treatment_effect=2.5,
        variability=6.0,
        dropout_rate=0.20,
        exclusion_rate=0.15,
        power_achieved=0.65,
        is_viable=False,
        risk_flags=[
            "Low power (65.0% vs target 80%)",
            "High dropout rate (20%)",
            "Wide expected confidence interval",
        ],
    ),
    DesignFingerprint(
        id="seed_007",
        disease_area="Alzheimer's Disease",
        endpoint="ADAS-Cog Score Change",
        n_per_arm=450,
        treatment_effect=2.5,
        variability=6.0,
        dropout_rate=0.18,
        exclusion_rate=0.12,
        power_achieved=0.82,
        is_viable=True,
        risk_flags=["High dropout rate (18%) — consider retention strategies"],
    ),
    DesignFingerprint(
        id="seed_008",
        disease_area="Rheumatoid Arthritis",
        endpoint="ACR20 Response",
        n_per_arm=140,
        treatment_effect=0.25,  # response rate difference
        variability=0.45,
        dropout_rate=0.12,
        exclusion_rate=0.10,
        power_achieved=0.71,
        is_viable=False,
        risk_flags=["Low power (71.0% vs target 80%)"],
    ),
    DesignFingerprint(
        id="seed_009",
        disease_area="Rheumatoid Arthritis",
        endpoint="ACR20 Response",
        n_per_arm=220,
        treatment_effect=0.25,
        variability=0.45,
        dropout_rate=0.10,
        exclusion_rate=0.08,
        power_achieved=0.87,
        is_viable=True,
        risk_flags=[],
    ),
]


def seed_memory(store) -> int:
    """Populate an ActianStore with seed designs. Returns count of designs loaded."""
    import asyncio
    count = 0
    for design in SEED_DESIGNS:
        try:
            asyncio.run(store.store(design))
            count += 1
        except RuntimeError:
            # Event loop already running — try alternative
            loop = asyncio.get_event_loop()
            loop.run_until_complete(store.store(design))
            count += 1
    return count


def get_seed_prompt() -> str:
    """Return a description of the seed data for the agent's context."""
    return (
        f"I have {len(SEED_DESIGNS)} pre-loaded trial designs in memory across "
        f"{len(set(d.disease_area for d in SEED_DESIGNS))} disease areas. "
        f"Of these, {sum(1 for d in SEED_DESIGNS if d.is_viable)} were viable "
        f"and {sum(1 for d in SEED_DESIGNS if not d.is_viable)} needed adjustments. "
        f"I can compare new designs against this experience."
    )
