"""OpenCode API client for communicating with OpenCode server."""

import logging
import json
from typing import Optional, Dict, Any, AsyncGenerator

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class OpenCodeClient:
    """OpenCode API client.

    Handles HTTP communication with OpenCode server including:
    - Session management (create, get, list, delete)
    - Message sending
    - SSE event stream receiving
    """

    def __init__(self):
        """Initialize OpenCode client with settings."""
        settings = get_settings()
        self.base_url = settings.opencode_api_url.rstrip("/")
        self.password = settings.opencode_password
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client.

        Returns:
            Configured AsyncClient instance
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(60.0, connect=10.0),
                headers={
                    "Authorization": f"Bearer {self.password}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def create_session(self, name: str = "New Session") -> str:
        """Create a new OpenCode session.

        Args:
            name: Session name

        Returns:
            Session ID string
        """
        client = await self._get_client()
        response = await client.post("/api/session", json={"name": name})
        response.raise_for_status()
        data = response.json()
        return data.get("sessionId") or data.get("session_id") or data.get("id")

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details.

        Args:
            session_id: OpenCode session ID

        Returns:
            Session data dictionary
        """
        client = await self._get_client()
        response = await client.get(f"/api/session/{session_id}")
        response.raise_for_status()
        return response.json()

    async def send_message(
        self, session_id: str, content: str, attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """Send a message to an OpenCode session.

        Args:
            session_id: OpenCode session ID
            content: Message content (text)
            attachments: Optional list of attachments

        Returns:
            Response data dictionary
        """
        client = await self._get_client()
        payload = {
            "content": content,
        }
        if attachments:
            payload["attachments"] = attachments

        response = await client.post(f"/api/session/{session_id}/message", json=payload)
        response.raise_for_status()
        return response.json()

    async def receive_sse_stream(self, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Receive SSE event stream from OpenCode.

        This is a skeleton - full implementation in Task 9.

        Args:
            session_id: OpenCode session ID

        Yields:
            Parsed SSE events as dictionaries
        """
        client = await self._get_client()
        # TODO: Implement SSE stream handling
        # The endpoint is likely /api/session/{session_id}/events or similar
        async with client.stream("GET", f"/api/session/{session_id}/events") as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse SSE data: {line}")

    async def list_sessions(self) -> list:
        """List all OpenCode sessions.

        Returns:
            List of session data
        """
        client = await self._get_client()
        response = await client.get("/api/sessions")
        response.raise_for_status()
        return response.json()

    async def delete_session(self, session_id: str) -> bool:
        """Delete an OpenCode session.

        Args:
            session_id: OpenCode session ID

        Returns:
            True if successful
        """
        client = await self._get_client()
        response = await client.delete(f"/api/session/{session_id}")
        response.raise_for_status()
        return True


# Singleton instance
_opencode_client: Optional[OpenCodeClient] = None


async def get_opencode_client() -> OpenCodeClient:
    """Get OpenCode client singleton.

    Returns:
        OpenCodeClient instance
    """
    global _opencode_client
    if _opencode_client is None:
        _opencode_client = OpenCodeClient()
    return _opencode_client
