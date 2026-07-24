"""Pydantic models for trial design data across the system."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TrialPhase(str, Enum):
    PHASE_I = "phase_i"
    PHASE_II = "phase_ii"
    PHASE_III = "phase_iii"
    PHASE_IV = "phase_iv"


class EndpointType(str, Enum):
    CONTINUOUS = "continuous"
    BINARY = "binary"
    TIME_TO_EVENT = "time_to_event"


class TrialDesignRequest(BaseModel):
    """Input from the user — what they want to simulate."""
    disease_area: str = Field(..., description="e.g., hypertension, diabetes, NSCLC")
    endpoint: str = Field(..., description="e.g., systolic blood pressure reduction")
    endpoint_type: EndpointType = EndpointType.CONTINUOUS
    expected_effect: float = Field(..., description="Expected treatment effect in endpoint units")
    variability: float = Field(..., description="Standard deviation of the endpoint")
    n_per_arm: int = Field(100, ge=10, description="Patients per arm")
    alpha: float = Field(0.05, ge=0.01, le=0.10)
    target_power: float = Field(0.80, ge=0.50, le=0.99)
    dropout_rate: float = Field(0.0, ge=0.0, le=0.50)
    estimated_exclusion_rate: float = Field(0.0, ge=0.0, le=0.50)

    @property
    def summary(self) -> str:
        return (
            f"{self.disease_area} | {self.endpoint} | "
            f"n={self.n_per_arm}x2 | Δ={self.expected_effect} ± {self.variability} | "
            f"α={self.alpha} | power≥{self.target_power}"
        )


class TrialDesignResult(BaseModel):
    """Output from the simulation — what the agent found."""
    request: TrialDesignRequest
    power_achieved: float
    is_viable: bool
    recommended_n_per_arm: Optional[int] = None
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    risk_flags: list[str] = Field(default_factory=list)
    similar_designs_found: int = 0
    agent_advice: str = ""


class DesignFingerprint(BaseModel):
    """Vector-storable record of a trial design + outcome."""
    id: Optional[str] = None
    disease_area: str
    endpoint: str
    n_per_arm: int
    treatment_effect: float
    variability: float
    dropout_rate: float
    exclusion_rate: float
    power_achieved: float
    is_viable: bool
    risk_flags: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list, description="Vector embedding for similarity search")
