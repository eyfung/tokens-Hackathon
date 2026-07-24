"""
Trial simulation engine — the statistical core.

Runs thousands of virtual clinical trials to estimate power,
type I error rate, and operating characteristics under different
design scenarios.

Scope for hackathon: two-arm, fixed-design, superiority trial
with a continuous endpoint (blood pressure reduction).
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from scipy import stats


@dataclass
class TrialDesign:
    """Parameters defining a clinical trial design."""
    # Sample sizes
    n_control: int = 100
    n_treatment: int = 100

    # Treatment effect (mean difference in endpoint units)
    treatment_effect: float = 10.0  # e.g., 10 mmHg reduction

    # Variability
    control_std: float = 15.0
    treatment_std: float = 15.0

    # Baseline
    control_mean: float = 0.0

    # Statistical parameters
    alpha: float = 0.05  # significance threshold
    n_simulations: int = 10_000

    # Optional dropout rate (patients who don't complete)
    dropout_rate: float = 0.0

    # Exclusion criteria effect (fraction of patients excluded)
    exclusion_rate: float = 0.0

    @property
    def total_n(self) -> int:
        return self.n_control + self.n_treatment


@dataclass
class SimulationResult:
    """Results from running the simulation engine."""
    design: TrialDesign
    power: float  # fraction of simulations where p < alpha
    mean_effect_observed: float
    std_effect_observed: float
    ci_lower: float  # 95% CI of treatment effect
    ci_upper: float
    type_i_error_rate: Optional[float] = None  # when effect = 0
    effective_sample_size: float = 0.0

    def is_viable(self, target_power: float = 0.80) -> bool:
        """A design is viable if it achieves target power."""
        return self.power >= target_power


def simulate_trial(design: TrialDesign, effect_multiplier: float = 1.0) -> SimulationResult:
    """
    Run thousands of virtual trials and compute operating characteristics.

    This is a hackathon-grade simulation using a two-sample t-test.
    Real trial simulations use far more complex models (survival analysis,
    non-inferiority margins, adaptive designs, etc.).

    Args:
        design: The trial design parameters
        effect_multiplier: Override the treatment effect (1.0 = as-designed)
    """
    actual_effect = design.treatment_effect * effect_multiplier
    p_values = np.zeros(design.n_simulations)
    observed_effects = np.zeros(design.n_simulations)

    for i in range(design.n_simulations):
        # Account for dropout
        n_control_eff = int(design.n_control * (1 - design.dropout_rate))
        n_treatment_eff = int(design.n_treatment * (1 - design.dropout_rate))

        # Exclusions
        n_control_eff = int(n_control_eff * (1 - design.exclusion_rate))
        n_treatment_eff = int(n_treatment_eff * (1 - design.exclusion_rate))

        # Generate virtual patient data
        control_group = np.random.normal(
            loc=design.control_mean,
            scale=design.control_std,
            size=max(n_control_eff, 2),
        )
        treatment_group = np.random.normal(
            loc=design.control_mean + actual_effect,
            scale=design.treatment_std,
            size=max(n_treatment_eff, 2),
        )

        # Two-sample t-test
        t_stat, p_val = stats.ttest_ind(treatment_group, control_group)
        p_values[i] = p_val
        observed_effects[i] = treatment_group.mean() - control_group.mean()

    # Compute operating characteristics
    power = np.mean(p_values < design.alpha)
    mean_effect = np.mean(observed_effects)
    std_effect = np.std(observed_effects)
    ci_lower = np.percentile(observed_effects, 2.5)
    ci_upper = np.percentile(observed_effects, 97.5)

    # Type I error (when there's truly no effect)
    type_i_error = None
    if effect_multiplier == 0.0:
        type_i_error = power  # under null, power = type I error rate

    effective_n = (design.n_control + design.n_treatment) * (1 - design.dropout_rate) * (1 - design.exclusion_rate)

    return SimulationResult(
        design=design,
        power=power,
        mean_effect_observed=mean_effect,
        std_effect_observed=std_effect,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        type_i_error_rate=type_i_error,
        effective_sample_size=effective_n,
    )


def find_minimum_sample_size(
    target_power: float = 0.80,
    effect: float = 10.0,
    std: float = 15.0,
    alpha: float = 0.05,
    n_simulations: int = 5_000,
    max_n: int = 1000,
    step: int = 20,
) -> tuple[int, SimulationResult]:
    """
    Binary-search for the minimum sample size that achieves target power.
    Returns (n_per_arm, simulation_result_at_that_n).
    """
    lo, hi = 10, max_n
    best_n = max_n
    best_result = None

    while lo <= hi:
        mid = (lo + hi) // 2
        design = TrialDesign(
            n_control=mid,
            n_treatment=mid,
            treatment_effect=effect,
            control_std=std,
            treatment_std=std,
            alpha=alpha,
            n_simulations=n_simulations,
        )
        result = simulate_trial(design)

        if result.power >= target_power:
            best_n = mid
            best_result = result
            hi = mid - step
        else:
            lo = mid + step

    return best_n, best_result
