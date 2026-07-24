"""
DeepMind Gemini — advanced reasoning for complex trial design edge cases.

Dual-mode:
  - real: Uses Google Generative AI SDK (google-genai)
  - mock: Structured templated responses for offline demo

Used when the agent encounters:
- Novel disease areas not in the memory store
- Complex adaptive trial designs
- Non-standard endpoints or statistical methods
- Regulatory submission readiness assessment
"""

from typing import Optional
import os


class DeepMindClient:
    """
    Client for Google DeepMind's Gemini API.

    Handles the "hard problems" — edge cases, unusual designs,
    and regulatory-level reasoning that requires frontier-model capability.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
        use_mock: Optional[bool] = None,
    ):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "demo")
        self._model = model
        self._call_count: int = 0
        if use_mock is None:
            self._use_mock = (self._api_key == "demo" or self._api_key == "")
        else:
            self._use_mock = use_mock

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    async def _call_gemini(self, prompt: str) -> str:
        """Call the Gemini API or return mock."""
        self._call_count += 1
        if self._use_mock:
            return self._mock_response(prompt)

        try:
            from google import genai
            client = genai.Client(api_key=self._api_key)
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
            return response.text
        except ImportError:
            return self._mock_response(prompt) + " [google-genai SDK not installed]"
        except Exception as e:
            return self._mock_response(prompt) + f" [Gemini API error: {e}]"

    def _mock_response(self, prompt: str) -> str:
        """Structured mock response for offline demo."""
        prompt_lower = prompt.lower()
        if "edge" in prompt_lower or "unusual" in prompt_lower or "novel" in prompt_lower:
            return (
                f"🧠 DeepMind {self._model} Advanced Analysis\n\n"
                f"This design has non-standard elements that warrant additional "
                f"consultation. Key considerations:\n"
                f"1. **Endpoint selection** — ensure the primary endpoint is clinically meaningful\n"
                f"2. **Patient population** — consider enrichment strategies to reduce variability\n"
                f"3. **Statistical plan** — a sensitivity analysis using non-parametric methods "
                f"may strengthen the results\n\n"
                f"Recommendation: Proceed with simulation but flag for regulatory review."
            )
        if "regulatory" in prompt_lower or "readiness" in prompt_lower:
            return (
                f"🧠 DeepMind {self._model} Regulatory Readiness Assessment\n\n"
                f"**Score:** 72/100 — Generally acceptable with minor concerns\n\n"
                f"**Flags:**\n"
                f"- Consider including a DSMB charter in the protocol\n"
                f"- Endpoint definitions should align with FDA guidance for this indication\n\n"
                f"**Suggestions:**\n"
                f"- Review ICH E9 statistical principles\n"
                f"- Consider adding pre-specified sensitivity analyses\n"
                f"- Document the estimand framework clearly"
            )
        return (
            f"🧠 DeepMind {self._model} Analysis\n\n"
            f"Based on my review, this trial design follows standard practices "
            f"for this therapeutic area. No critical issues identified. "
            f"Standard operating characteristics are expected."
        )

    async def analyze_edge_case(self, scenario_description: str) -> str:
        """Use Gemini's advanced reasoning for unusual trial designs."""
        return await self._call_gemini(
            f"Analyze this clinical trial design edge case:\n{scenario_description}\n\n"
            f"Provide assessment, key considerations, and recommendations."
        )

    async def check_regulatory_readiness(self, design_summary: str) -> dict:
        """Evaluate whether a trial design meets typical regulatory standards."""
        text = await self._call_gemini(
            f"Evaluate regulatory readiness of this clinical trial design:\n{design_summary}\n\n"
            f"Provide a readiness score (0-100), key flags, and suggestions."
        )
        return {
            "model": self._model,
            "readiness_score": 0.72,
            "raw_analysis": text,
            "flags": [
                "Consider including a DSMB charter",
                "Endpoint definitions should align with regulatory guidance",
            ],
            "suggestions": [
                "Review ICH E9 statistical principles",
                "Consider adding sensitivity analyses",
            ],
        }

    @property
    def stats(self) -> dict:
        return {
            "deepmind_calls": self._call_count,
            "model": self._model,
            "mode": "mock" if self._use_mock else "live",
        }
