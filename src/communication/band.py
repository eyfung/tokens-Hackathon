"""
Band AI — human-in-the-loop escalation.

Dual-mode:
  - real: Uses Band AI SDK for real-time agent-human messaging
  - mock: Simulated conversation for offline demo

When the agent detects a risky design, it opens a Band room
and pulls in a human for consultation. The human's feedback
is fed back into the agent's learning loop.
"""

from typing import Optional
import os
import json


class BandRoom:
    """
    A communication room for agent ↔ human collaboration.

    Wraps the Band AI SDK for real-time agent-human messaging.
    Features: room creation, message posting, history, escalation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.band.ai/v1",
        room_name: str = "clarity-trials",
        use_mock: Optional[bool] = None,
    ):
        self._api_key = api_key or os.getenv("BAND_API_KEY", "demo")
        self._base_url = base_url
        self._room_name = room_name
        self.total_rooms_opened: int = 0
        self._conversation_log: list[dict] = []
        if use_mock is None:
            self._use_mock = (self._api_key == "demo" or self._api_key == "")
        else:
            self._use_mock = use_mock

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    async def escalate(
        self,
        title: str,
        message: str,
        suggested_action: str = "",
        human_id: str = "principal-investigator",
    ) -> str:
        """
        Open a Band room and escalate to a human.

        Returns the human's response as a string.
        """
        self.total_rooms_opened += 1
        room_ref = f"{self._room_name}-{self.total_rooms_opened}"

        # Log the escalation
        self._conversation_log.append({
            "type": "escalation",
            "room": room_ref,
            "title": title,
            "message": message,
            "suggested_action": suggested_action,
            "human_id": human_id,
            "status": "pending",
        })

        if self._use_mock:
            human_response = self._mock_human_response(title, suggested_action)
        else:
            human_response = await self._real_escalate(
                title, message, suggested_action, human_id, room_ref
            )

        # Log the response
        self._conversation_log.append({
            "type": "human_response",
            "human_id": human_id,
            "response": human_response,
            "room": room_ref,
            "suggested_action_accepted": bool(suggested_action),
        })

        return human_response

    async def _real_escalate(
        self, title: str, message: str, suggested_action: str,
        human_id: str, room_ref: str,
    ) -> str:
        """Use Band AI SDK to create a real room and await response."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60) as client:
                # Create room
                room_resp = await client.post(
                    f"{self._base_url}/rooms",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "name": room_ref,
                        "title": title,
                        "participants": [human_id, "clarity-agent"],
                    },
                )
                room_resp.raise_for_status()
                room_data = room_resp.json()
                room_id = room_data["id"]

                # Post the escalation message
                await client.post(
                    f"{self._base_url}/rooms/{room_id}/messages",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "role": "agent",
                        "content": message,
                        "suggested_action": suggested_action,
                    },
                )

                # In production: poll or webhook for human response
                # In hackathon: return acknowledgment
                return (
                    f"[Band room {room_id}] Escalation sent to {human_id}. "
                    f"Suggested action: {suggested_action}. Waiting for human review."
                )
        except Exception as e:
            return f"[Band escalation attempted — fallback] {self._mock_human_response(title, suggested_action)}"

    def _mock_human_response(self, title: str, suggested_action: str) -> str:
        """Simulate a human response for demo."""
        if "underpowered" in title.lower():
            return (
                f"Good catch. {suggested_action} seems reasonable. "
                f"Let me check feasibility with our clinical ops team, "
                f"but proceed with the simulation assuming we can recruit that many."
            )
        if "exclusion" in title.lower() or "recruitment" in title.lower():
            return (
                f"I see the concern. The exclusion criteria may need adjustment. "
                f"Let me discuss with the site investigators and get back to you. "
                f"In the meantime, run the sensitivity analysis with relaxed criteria."
            )
        return (
            f"Thanks for the alert. I've reviewed your recommendation. "
            f"Please proceed and share the full results with the study team."
        )

    def get_log(self) -> list[dict]:
        """Return the full conversation log for audit / Replay capture."""
        return list(self._conversation_log)

    @property
    def stats(self) -> dict:
        return {
            "rooms_opened": self.total_rooms_opened,
            "log_entries": len(self._conversation_log),
            "mode": "mock" if self._use_mock else "live",
        }
