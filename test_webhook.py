"""Test webhook endpoint."""

import httpx
import json

# Test data for P2P message
test_p2p_message = {
    "type": "p2p_message.created",
    "event": {
        "message": {
            "user_id": "test_user_123",
            "message_id": "msg_456",
            "chat_id": "chat_789",
            "message_type": "text",
            "content": json.dumps({"text": "Hello from test"}),
            "chat_type": "p2p",
            "create_time": "2024-01-01T12:00:00Z",
        }
    },
}

# Test data for group message (should be ignored)
test_group_message = {
    "type": "message.created",
    "event": {
        "message": {
            "user_id": "test_user_123",
            "message_id": "msg_456",
            "chat_id": "chat_789",
            "message_type": "text",
            "content": json.dumps({"text": "Hello from group"}),
            "chat_type": "group",
            "create_time": "2024-01-01T12:00:00Z",
        }
    },
}


def test_webhook():
    """Test the webhook endpoint."""
    base_url = "http://localhost:8080"

    with httpx.Client() as client:
        # Test health check
        print("Testing health check...")
        response = client.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")

        # Test P2P message
        print("\nTesting P2P message...")
        response = client.post(
            f"{base_url}/webhook/feishu",
            json=test_p2p_message,
            headers={"Content-Type": "application/json"},
        )
        print(f"P2P message: {response.status_code} - {response.json()}")

        # Test group message (should be ignored)
        print("\nTesting group message...")
        response = client.post(
            f"{base_url}/webhook/feishu",
            json=test_group_message,
            headers={"Content-Type": "application/json"},
        )
        print(f"Group message: {response.status_code} - {response.json()}")


if __name__ == "__main__":
    test_webhook()
