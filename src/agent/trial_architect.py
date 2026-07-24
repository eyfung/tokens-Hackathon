"""
Trial Architect Agent — the main agent workflow.

Orchestrates the simulation → evaluation → learning loop.
Uses Guild AI for lifecycle management.
"""

from typing import Optional

from src.simulation.engine import (
    TrialDesign,
    SimulationResult,
    simulate_trial,
    find_minimum_sample_size,
)
from src.simulation.models import (
    TrialDesignRequest,
    TrialDesignResult,
    DesignFingerprint,
)
from src.memory.actian_store import ActianStore
from src.communication.band import BandRoom
from src.inference.pioneer import PioneerClient
from src.inference.deepmind import DeepMindClient


class TrialArchitect:
    """
    Core agent: receives a trial design request, simulates it,
    evaluates viability, escalates if needed, and stores the result
    for future learning.
    """

    def __init__(
        self,
        memory: ActianStore,
        band: BandRoom,
        pioneer: PioneerClient,
        deepmind: Optional[DeepMindClient] = None,
    ):
        self.memory = memory
        self.band = band
        self.pioneer = pioneer
        self.deepmind = deepmind
        self._designs_evaluated: int = 0

    @property
    def evolution_stats(self) -> dict:
        """How many designs this agent has learned from."""
        return {
            "designs_evaluated": self._designs_evaluated,
            "patterns_stored": self.memory.count(),
            "human_escalations": self.band.total_rooms_opened,
        }

    async def evaluate_design(self, request: TrialDesignRequest) -> TrialDesignResult:
        """
        The main evaluation loop:
        1. Check memory for similar past designs
        2. Run simulation
        3. Assess viability
        4. If underpowered → open Band room, suggest fixes
        5. Store the result in Actian for future learning
        """

        # Step 1: Check memory for similar designs
        similar = self.memory.search_similar(request)
        advice = ""
        if similar:
            advice = await self.pioneer.summarize_patterns(similar, request)
        else:
            advice = "No similar designs in memory. This is a novel scenario."

        # Step 2: Build & run simulation
        design = TrialDesign(
            n_control=request.n_per_arm,
            n_treatment=request.n_per_arm,
            treatment_effect=request.expected_effect,
            control_std=request.variability,
            treatment_std=request.variability,
            alpha=request.alpha,
            dropout_rate=request.dropout_rate,
            exclusion_rate=request.estimated_exclusion_rate,
        )

        result = simulate_trial(design)

        # Step 3: Assess viability
        is_viable = result.is_viable(request.target_power)
        risk_flags = self._assess_risks(result, request)
        recommended_n = None

        # Step 4: If not viable, find minimum sample size
        if not is_viable:
            recommended_n, optimal_result = find_minimum_sample_size(
                target_power=request.target_power,
                effect=request.expected_effect,
                std=request.variability,
                alpha=request.alpha,
            )

            # Open Band room for human consultation
            escalation_msg = (
                f"⚠️ **Design underpowered** — {result.power:.1%} vs target {request.target_power:.0%}.\n"
                f"Recommended: {recommended_n} patients per arm to achieve {request.target_power:.0%} power "
                f"(current: {request.n_per_arm}).\n"
                f"Risk flags: {', '.join(risk_flags)}\n"
                f"Similar designs in memory: {len(similar) if similar else 0}"
            )
            human_response = await self.band.escalate(
                title=f"Underpowered trial: {request.disease_area}",
                message=escalation_msg,
                suggested_action=f"Increase sample size to {recommended_n} per arm",
            )
            advice += f"\n\n--- Human consultation ---\n{human_response}"

        # Step 5: Store in Actian for future learning
        fingerprint = DesignFingerprint(
            disease_area=request.disease_area,
            endpoint=request.endpoint,
            n_per_arm=request.n_per_arm,
            treatment_effect=request.expected_effect,
            variability=request.variability,
            dropout_rate=request.dropout_rate,
            exclusion_rate=request.estimated_exclusion_rate,
            power_achieved=result.power,
            is_viable=is_viable,
            risk_flags=risk_flags,
        )
        await self.memory.store(fingerprint)
        self._designs_evaluated += 1

        # Build response
        return TrialDesignResult(
            request=request,
            power_achieved=result.power,
            is_viable=is_viable,
            recommended_n_per_arm=recommended_n,
            confidence_interval=(result.ci_lower, result.ci_upper),
            risk_flags=risk_flags,
            similar_designs_found=len(similar) if similar else 0,
            agent_advice=advice,
        )

    def _assess_risks(self, result: SimulationResult, request: TrialDesignRequest) -> list[str]:
        """Generate human-readable risk flags for a trial design."""
        flags = []
        if result.power < request.target_power:
            flags.append(
                f"Low power ({result.power:.1%} vs target {request.target_power:.0%})"
            )
        if request.dropout_rate > 0.2:
            flags.append(f"High dropout rate ({request.dropout_rate:.0%}) — may bias results")
        if request.estimated_exclusion_rate > 0.2:
            flags.append(
                f"High exclusion rate ({request.estimated_exclusion_rate:.0%}) — "
                f"may delay recruitment"
            )
        width = result.ci_upper - result.ci_lower
        if width > 2 * request.expected_effect:
            flags.append(
                f"Wide confidence interval ({result.ci_lower:.1f}–{result.ci_upper:.1f}) — "
                f"effect may not be precisely estimated"
            )
        return flags
