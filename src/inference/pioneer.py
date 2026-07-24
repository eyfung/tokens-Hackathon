"""
Pioneer Inference API — cost-effective inference for routine operations.

Used by the agent for:
- Summarizing simulation results in plain English
- Comparing current designs to past patterns
- Generating risk flag descriptions
"""

from typing import Any
import json


class PioneerClient:
    """
    Client for Pioneer (Fastino Labs) Inference API.

    The API that improves with your traffic — perfect for the
    high-volume, routine inference needs of a self-evolving agent.
    """

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.pioneer.ai/v1"):
        self._api_key = api_key or "demo"
        self._base_url = base_url
        self._call_count: int = 0

    async def summarize_patterns(
        self,
        similar_designs: list[Any],
        current_request: Any,
    ) -> str:
        """Generate a natural-language insight comparing past designs to the current one."""
        self._call_count += 1
        # In production: call Pioneer API.
        # In hackathon: return a templated response.
        if not similar_designs:
            return "No similar designs found in memory."

        past = similar_designs[0]
        return (
            f"I found {len(similar_designs)} similar trial designs in my memory. "
            f"The closest match was a {past.disease_area} trial with "
            f"n={past.n_per_arm} per arm, achieving {past.power_achieved:.1%} power. "
            f"Your current design is comparable — expect similar operating characteristics."
        )

    async def generate_advice(self, prompt: str, **kwargs) -> str:
        """General-purpose inference call."""
        self._call_count += 1
        # In production: POST to Pioneer.
        # In hackathon: echo with context.
        return f"[Pioneer analyzed] {prompt[:200]}..."

    @property
    def stats(self) -> dict:
        return {"inference_calls": self._call_count}
