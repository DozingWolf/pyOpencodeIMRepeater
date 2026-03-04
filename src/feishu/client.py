"""Feishu API client wrapper."""

import json
import hashlib
import time
import logging
from typing import Any, Optional

from lark_oapi import Client, FEISHU_DOMAIN

from src.config import get_settings

logger = logging.getLogger(__name__)


class FeishuClient:
    """Feishu API client wrapper."""

    def __init__(self) -> None:
        """Initialize Feishu client with configuration."""
        settings = get_settings()
        self.client = Client.builder() \
            .app_id(settings.feishu_app_id) \
            .app_secret(settings.feishu_app_secret) \
            .domain(FEISHU_DOMAIN) \
            .build()
        self.verification_token = settings.feishu_verification_token
        self.encrypt_key = settings.feishu_encrypt_key

    def verify_request(self, headers: dict[str, str], body: str) -> bool:
        """Verify webhook request signature.

        Args:
            headers: HTTP request headers.
            body: Request body as JSON string.

        Returns:
            True if request is valid, False otherwise.
        """
        # If no encrypt_key configured, skip verification
        if not self.encrypt_key:
            logger.warning("No encrypt_key configured, skipping signature verification")
            return True

        # Get required headers
        timestamp = headers.get("x-lark-request-timestamp", "")
        nonce = headers.get("x-lark-request-nonce", "")
        signature = headers.get("x-lark-signature", "")

        if not all([timestamp, nonce, signature]):
            logger.warning("Missing required signature headers")
            return False

        # Prevent replay attack (allow 5 minutes)
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - request_time) > 300:
                logger.warning(f"Request timestamp expired: {request_time}, current: {current_time}")
                return False
        except ValueError:
            logger.warning(f"Invalid timestamp format: {timestamp}")
            return False

        # Calculate signature: sha256(timestamp + nonce + encrypt_key + body)
        sign_base = f"{timestamp}{nonce}{self.encrypt_key}{body}"
        calculated_signature = hashlib.sha256(sign_base.encode('utf-8')).hexdigest()

        # Compare signatures
        if calculated_signature != signature:
            logger.warning(f"Signature mismatch: calculated={calculated_signature}, received={signature}")
            return False

        return True

    def parse_event(self, body: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Parse webhook event body.

        Args:
            body: Webhook event body as dictionary.

        Returns:
            Parsed event data if it's a P2P message, None otherwise.
        """
        event = body.get("event", {})
        event_type = body.get("type") or body.get("header", {}).get("event_type")

        if (
            event_type == "p2p_message.created"
            or event.get("message", {}).get("chat_type") == "p2p"
        ):
            return self._parse_p2p_message(event)

        # Ignore group messages and other events
        logger.debug(f"Ignoring event type: {event_type}")
        return None

    def _parse_p2p_message(self, event: dict[str, Any]) -> dict[str, Any]:
        """Parse P2P message event.

        Args:
            event: P2P message event data.

        Returns:
            Parsed message information.
        """
        message = event.get("message", {})
        return {
            "type": "p2p_message",
            "user_id": message.get("user_id"),
            "message_id": message.get("message_id"),
            "chat_id": message.get("chat_id"),
            "content": self._parse_message_content(message),
            "content_type": message.get("message_type", "text"),
            "create_time": message.get("create_time"),
        }

    def _parse_message_content(self, message: dict[str, Any]) -> dict[str, Any]:
        """Parse message content based on type.

        Args:
            message: Message data with content and type.

        Returns:
            Parsed content dict with type and data.
        """
        content_type = message.get("message_type", "text")
        content = message.get("content", "{}")

        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                return {"type": "text", "text": content}

        if content_type == "text":
            return {"type": "text", "text": content.get("text", "")}
        elif content_type == "image":
            image_key = content.get("image_key", "")
            return {
                "type": "image",
                "image_key": image_key,
                "text": f"[Image: {image_key}]"
            }
        elif content_type == "file":
            file_name = content.get("file_name", "")
            file_key = content.get("file_key", "")
            return {
                "type": "file",
                "file_key": file_key,
                "file_name": file_name,
                "text": f"[File: {file_name}]"
            }

        return {"type": "unknown", "text": str(content)}

# Singleton instance
_feishu_client: Optional[FeishuClient] = None


def get_feishu_client() -> FeishuClient:
    """Get Feishu client singleton.

    Returns:
        FeishuClient instance.
    """
    global _feishu_client
    if _feishu_client is None:
        _feishu_client = FeishuClient()
    return _feishu_client
