"""SSE streaming response forwarding service."""

import logging
from typing import Optional

from src.opencode.client import get_opencode_client
from src.feishu.client import get_feishu_client

logger = logging.getLogger(__name__)


async def stream_and_forward(session_id: str, user_id: str, chat_id: str, message_id: str) -> str:
    """Stream OpenCode response and forward to Feishu.

    Args:
        session_id: OpenCode session ID
        user_id: Feishu user ID
        chat_id: Feishu chat ID
        message_id: Original Feishu message ID

    Returns:
        Final response text
    """
    opencode_client = await get_opencode_client()
    feishu_client = get_feishu_client()

    full_response = []

    try:
        async for event in opencode_client.receive_sse_stream(session_id):
            # Extract text from event
            # Try different possible field names for content
            text = (
                event.get("content")
                or event.get("text")
                or event.get("delta", {}).get("content", "")
                or ""
            )

            if text:
                full_response.append(text)
                # TODO: Send chunk to Feishu (Task 11 will implement this)
                # For now, just accumulate
                logger.debug(f"Received chunk: {text[:50]}...")

        final_text = "".join(full_response)

        # TODO: Send complete response to Feishu (Task 11 will implement this)
        logger.info(f"Stream complete for user {user_id}: {len(final_text)} chars")

        return final_text

    except Exception as e:
        logger.error(f"Streaming error: {e}", exc_info=True)
        raise
