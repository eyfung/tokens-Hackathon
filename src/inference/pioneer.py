"""
Pioneer Inference API — cost-effective inference for routine operations.

Dual-mode: 
  - real: Uses OpenAI-compatible API (Pioneer or any provider) via httpx
  - mock: Templated responses for offline demo

The API that improves with your traffic — perfect for the
high-volume, routine inference needs of a self-evolving agent.
"""

from typing import Any, Optional
import json
import os


class PioneerClient:
    """
    Client for Pioneer (Fastino Labs) Inference API.

    Provides natural-language reasoning for the agent's routine operations:
    summarization, comparison, risk assessment, and advice generation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.pioneer.ai/v1",
        model: str = "pioneer-1",
        use_mock: Optional[bool] = None,
    ):
        self._api_key = api_key or os.getenv("PIONEER_API_KEY", "demo")
        self._base_url = base_url
        self._model = model
        self._call_count: int = 0
        # Auto-detect: if no real key, stay in mock mode
        if use_mock is None:
            self._use_mock = (self._api_key == "demo" or self._api_key == "")
        else:
            self._use_mock = use_mock

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    async def _call_llm(self, system: str, user: str) -> str:
        """Make an actual HTTP call to the Pioneer API (or compatible endpoint)."""
        self._call_count += 1
        if self._use_mock:
            return self._mock_response(system, user)

        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 512,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Pioneer API unavailable — falling back to offline analysis] {self._mock_response(system, user)}"

    def _mock_response(self, system: str, user: str) -> str:
        """Generate a plausible response without API calls."""
        user_lower = user.lower()
        if "similar" in system.lower() and "similar" in user_lower:
            return (
                "Based on my memory, this design is comparable to past successful trials "
                "in similar disease areas. The key parameters align well, though you "
                "may want to consider the dropout rate more carefully."
            )
        if "risk" in system.lower() or "risk" in user_lower:
            return (
                "I've analyzed the risk profile. The primary concern is the width of the "
                "confidence interval relative to the expected effect size. Consider "
                "increasing sample size or reducing variability through stricter "
                "inclusion criteria."
            )
        if "advice" in system.lower() or "advice" in user_lower:
            return (
                "Here's my recommendation: this design is sound but the power is marginal. "
                "A 20-30% increase in sample size would significantly improve your "
                "chances of detecting a real treatment effect."
            )
        return (
            f"Analysis complete. Based on {self._call_count} inference calls, "
            f"the design appears {'viable' if 'viable' in user_lower else 'reasonable'} "
            f"for further development."
        )

    async def summarize_patterns(
        self,
        similar_designs: list[Any],
        current_request: Any,
    ) -> str:
        """Generate a natural-language insight comparing past designs to the current one."""
        if not similar_designs:
            return "No similar designs found in memory. This is a novel scenario — I'll learn from it."

        past = similar_designs[0]
        system = (
            "You are a clinical trial design expert. Summarize how past trial designs "
            "compare to a proposed new design. Be concise and specific."
        )
        user = (
            f"We have {len(similar_designs)} similar past designs. "
            f"The closest matched a {past.disease_area} trial with n={past.n_per_arm} per arm "
            f"achieving {past.power_achieved:.1%} power. "
            f"The proposed design has n={current_request.n_per_arm} per arm "
            f"with an expected effect of {current_request.expected_effect}. "
            f"How does this compare?"
        )
        return await self._call_llm(system, user)

    async def generate_advice(self, prompt: str, disease: str = "", power: float = 0.0) -> str:
        """Generate actionable advice for the trial designer."""
        self._call_count += 1
        system = (
            "You are Clarity, a self-evolving clinical trial design assistant. "
            "Provide concise, actionable advice for clinical trial designers."
        )
        return await self._call_llm(system, f"[{disease}] Power={power:.1%}: {prompt}")

    async def compare_designs(
        self,
        designs: list[Any],
        current_power: float,
        current_n: int,
    ) -> str:
        """Compare the current design against past designs and provide insight."""
        self._call_count += 1
        if not designs:
            return "No previous designs to compare against."

        best = max(designs, key=lambda d: d.power_achieved)
        system = "You are a clinical trial data analyst. Compare trial designs concisely."
        user = (
            f"Current design: n={current_n}, power={current_power:.1%}. "
            f"Best past design: n={best.n_per_arm}, power={best.power_achieved:.1%} "
            f"({best.disease_area}). "
            f"How has the agent evolved?"
        )
        return await self._call_llm(system, user)

    @property
    def stats(self) -> dict:
        return {"inference_calls": self._call_count, "mode": "mock" if self._use_mock else "live"}
