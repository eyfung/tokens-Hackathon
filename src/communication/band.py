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
        room_name: str = "clarity-trials",
        use_mock: Optional[bool] = None,
    ):
        self._api_key = api_key or os.getenv("BAND_API_KEY", "demo")
        self._room_name = room_name
        self._client = None
        self.total_rooms_opened: int = 0
        self._conversation_log: list[dict] = []
        if use_mock is None:
            self._use_mock = (self._api_key == "demo" or self._api_key == "")
        else:
            self._use_mock = use_mock

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    async def _get_client(self):
        """Lazy-init the Band async REST client."""
        if self._client is None and not self._use_mock:
            from band.client.rest import AsyncRestClient
            self._client = AsyncRestClient(api_key=self._api_key)
        return self._client

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
            from band.client.rest import (
                ChatRoomRequest,
                ChatMessageRequest,
                ChatMessageRequestMentionsItem,
                ParticipantRequest,
                DEFAULT_REQUEST_OPTIONS,
            )

            client = await self._get_client()
            if client is None:
                return (
                    f"[Band client not initialized] "
                    f"{self._mock_human_response(title, suggested_action)}"
                )

            # ---- Step 1: Create a chat room ----
            room_resp = await client.agent_api_chats.create_agent_chat(
                chat=ChatRoomRequest(
                    task_id=room_ref,
                    title=f"[Clarity] {title}",
                ),
                request_options=DEFAULT_REQUEST_OPTIONS,
            )

            # Handle both dict-like and object responses
            if hasattr(room_resp, 'id'):
                room_id = room_resp.id
            elif hasattr(room_resp, 'get'):
                room_id = room_resp.get('id', room_resp.get('chat_id', ''))
            elif isinstance(room_resp, str):
                room_id = room_resp
            else:
                room_id = str(room_resp)

            # ---- Step 2: Add the human as a participant ----
            try:
                await client.agent_api_participants.add_agent_chat_participant(
                    chat_id=room_id,
                    participant=ParticipantRequest(
                        participant_id=human_id,
                        role="member",
                    ),
                    request_options=DEFAULT_REQUEST_OPTIONS,
                )
            except Exception as part_err:
                # Participant add is best-effort; room creation is the critical part
                pass

            # ---- Step 3: Post the escalation message ----
            await client.agent_api_messages.create_agent_chat_message(
                chat_id=room_id,
                message=ChatMessageRequest(
                    content=(
                        f"{message}\n\n"
                        f"**Suggested action:** {suggested_action}\n"
                        f"**Room ref:** {room_ref}\n"
                        f"---\n"
                        f"This escalation was sent by the Clarity trial agent."
                    ),
                    mentions=[
                        ChatMessageRequestMentionsItem(
                            id=human_id,
                            name="Principal Investigator",
                        ),
                    ],
                ),
                request_options=DEFAULT_REQUEST_OPTIONS,
            )

            # ---- Step 4: Poll for human response (15s timeout) ----
            import asyncio
            human_reply = None
            poll_attempts = 0
            max_attempts = 15  # 15 * 1s = 15s total

            while poll_attempts < max_attempts:
                await asyncio.sleep(1)
                poll_attempts += 1
                try:
                    next_msg = await client.agent_api_messages.get_agent_next_message(
                        chat_id=room_id,
                        request_options=DEFAULT_REQUEST_OPTIONS,
                    )
                    if next_msg:
                        if hasattr(next_msg, 'content'):
                            human_reply = next_msg.content
                        elif hasattr(next_msg, 'get'):
                            human_reply = next_msg.get('content', '')
                        else:
                            human_reply = str(next_msg)

                        if human_reply:
                            # Mark as processed so we don't re-read it
                            try:
                                await client.agent_api_messages.mark_agent_message_processed(
                                    chat_id=room_id,
                                    message_id=(
                                        next_msg.id
                                        if hasattr(next_msg, 'id')
                                        else next_msg.get('id', '')
                                    ),
                                    request_options=DEFAULT_REQUEST_OPTIONS,
                                )
                            except Exception:
                                pass
                            break
                except Exception:
                    await asyncio.sleep(2)

            if human_reply:
                return (
                    f"[Band room {room_id}] Human {human_id} responded: "
                    f"\"{human_reply}\""
                )

            return (
                f"[Band room {room_id}] Escalation sent to {human_id}. "
                f"Suggested action: {suggested_action}. "
                f"No response received within polling window — proceeding autonomously."
            )

        except ImportError as ie:
            return (
                f"[Band SDK not installed] Install with: pip install band-sdk. "
                f"Using fallback: {self._mock_human_response(title, suggested_action)}"
            )
        except Exception as e:
            return (
                f"[Band escalation failed: {e}] "
                f"{self._mock_human_response(title, suggested_action)}"
            )

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
