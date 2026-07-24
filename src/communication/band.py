"""
Band AI — human-in-the-loop escalation.

When the agent detects a risky design, it opens a Band room
and pulls in a human for consultation. The human's feedback
is fed back into the agent's learning loop.
"""

from typing import Optional


class BandRoom:
    """
    A communication room for agent ↔ human collaboration.

    Wraps the Band AI SDK for real-time agent-human messaging.
    For hackathon: a simple in-memory simulation.
    In production: Band's full multi-peer room infrastructure.
    """

    def __init__(self, api_key: str | None = None, room_name: str = "clarity-trials"):
        self._api_key = api_key or "demo"
        self._room_name = room_name
        self.total_rooms_opened: int = 0
        self._conversation_log: list[dict] = []

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

        # Log the escalation
        entry = {
            "type": "escalation",
            "room": f"{self._room_name}-{self.total_rooms_opened}",
            "title": title,
            "message": message,
            "suggested_action": suggested_action,
            "human_id": human_id,
            "status": "pending",
        }
        self._conversation_log.append(entry)

        # In production: Band creates a real room and notifies the human.
        # In hackathon: simulate a human response.
        human_response = self._simulate_human_response(title, suggested_action)

        # Log the response
        self._conversation_log.append({
            "type": "human_response",
            "human_id": human_id,
            "response": human_response,
            "room": entry["room"],
        })

        return human_response

    def _simulate_human_response(self, title: str, suggested_action: str) -> str:
        """
        Simulate a human response for demo purposes.
        In production, this is a real Band room with a real human.
        """
        if "underpowered" in title.lower():
            return (
                f"Good catch. {suggested_action} seems reasonable. "
                f"Let me check feasibility with our clinical ops team, "
                f"but proceed with the simulation assuming we can recruit that many."
            )
        return (
            f"Thanks for the alert. I've reviewed your recommendation. "
            f"Please proceed and share the full results."
        )

    def get_log(self) -> list[dict]:
        """Return the full conversation log for audit / Replay capture."""
        return list(self._conversation_log)
