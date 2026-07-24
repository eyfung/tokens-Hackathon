"""
Tests for the simulation engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from src.simulation.engine import (
    TrialDesign,
    SimulationResult,
    simulate_trial,
    find_minimum_sample_size,
)


def test_simulate_trial_returns_result():
    """Basic test: simulation runs and returns a result object."""
    design = TrialDesign(n_control=50, n_treatment=50, n_simulations=100)
    result = simulate_trial(design)
    assert isinstance(result, SimulationResult)
    assert 0 <= result.power <= 1


def test_simulate_trial_power_with_large_effect():
    """A huge effect should give near-100% power."""
    design = TrialDesign(
        n_control=50,
        n_treatment=50,
        treatment_effect=100,  # massive effect
        control_std=15,
        treatment_std=15,
        n_simulations=500,
    )
    result = simulate_trial(design)
    assert result.power > 0.95, f"Expected >95% power, got {result.power}"


def test_simulate_trial_power_with_no_effect():
    """No effect should give power ≈ alpha."""
    design = TrialDesign(
        n_control=100,
        n_treatment=100,
        treatment_effect=0,  # no effect
        alpha=0.05,
        n_simulations=2000,
    )
    result = simulate_trial(design, effect_multiplier=0.0)
    # Type I error rate should be in ~[0.03, 0.07]
    assert 0.01 < result.power < 0.10, f"Type I error out of range: {result.power}"


def test_simulate_trial_increasing_n_increases_power():
    """More patients = more power (all else equal)."""
    design_small = TrialDesign(n_control=20, n_treatment=20, treatment_effect=5, n_simulations=500)
    design_large = TrialDesign(n_control=200, n_treatment=200, treatment_effect=5, n_simulations=500)

    result_small = simulate_trial(design_small)
    result_large = simulate_trial(design_large)

    assert result_large.power > result_small.power, (
        f"Larger N should give more power: {result_small.power} vs {result_large.power}"
    )


def test_dropout_reduces_power():
    """Higher dropout = fewer evaluable patients = lower power."""
    design_no_dropout = TrialDesign(n_control=100, n_treatment=100, treatment_effect=5, n_simulations=500)
    design_high_dropout = TrialDesign(n_control=100, n_treatment=100, treatment_effect=5, n_simulations=500, dropout_rate=0.5)

    result_no_dropout = simulate_trial(design_no_dropout)
    result_high_dropout = simulate_trial(design_high_dropout)

    assert result_high_dropout.power < result_no_dropout.power


def test_find_minimum_sample_size():
    """find_minimum_sample_size should return a viable n."""
    n, result = find_minimum_sample_size(
        target_power=0.80,
        effect=8,
        std=15,
        n_simulations=500,
        max_n=400,
    )
    assert n > 0, f"Should find a positive sample size, got {n}"
    assert result.power >= 0.70, f"Result should have decent power: {result.power}"
    # It's a hackathon binary search with limited sims, so 0.80 may not exact


def test_design_is_viable():
    """is_viable() should correctly identify sufficient power."""
    design = TrialDesign(n_control=500, n_treatment=500, treatment_effect=10, n_simulations=500)
    result = simulate_trial(design)
    # 500 per arm with effect 10 and SD 15 should be very high power
    assert result.power > 0.90
    assert result.is_viable(0.80)
