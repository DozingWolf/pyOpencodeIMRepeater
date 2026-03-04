"""FastAPI application entry point."""

import json
from lark_oapi import AESCipher
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.storage.database import init_db
from src.feishu.client import get_feishu_client
from src.middleware.error_handler import register_error_handlers
from src.utils.logger import setup_logging

# Configure logging
# setup_logging() will be called in lifespan
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Setup logging
    setup_logging()
    logger.info("Starting IM Repeater v0.1.0")
    logger.info("Debug mode: False")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Initialize Feishu client
    client = get_feishu_client()
    logger.info("Feishu client initialized")

    yield

    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="OpenCode IM Repeater",
    description="Feishu bot integration for OpenCode",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "OpenCode IM Repeater", "status": "running"}


@app.post("/")
async def root_webhook(request: Request) -> dict[str, Any]:
    """Root webhook endpoint (备选，飞书可能请求到根路径)."""
    logger.info("=== Root POST request received ===")
    return await feishu_webhook(request)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/webhook/feishu")
async def feishu_webhook(request: Request) -> dict[str, Any]:
    """Feishu webhook endpoint.

    Receives and processes incoming Feishu message events.
    Only processes P2P (private) messages, ignores group messages.
    """
    client = get_feishu_client()
    headers = dict(request.headers)
    raw_body = await request.body()
    body = await request.json()
    # Log incoming request
    logger.info(f"=== Incoming webhook request ===")
    logger.info(f"Headers: {headers}")
    logger.info(f"Body: {body}")

    # Handle encrypted request (if Encrypt Key is configured)
    settings = get_settings()
    if "encrypt" in body and settings.feishu_encrypt_key:
        try:
            # Decrypt the request
            from lark_oapi import AESCipher
            cipher = AESCipher(settings.feishu_encrypt_key)
            decrypted = cipher.decrypt_str(body["encrypt"])
            body = json.loads(decrypted)
            logger.info(f"Decrypted body: {body}")
        except Exception as e:
            logger.error(f"Failed to decrypt request: {e}")
            return {"code": -1, "msg": "decryption failed"}
    # Handle URL verification (飞书配置 webhook 时的验证请求)
    if body.get("type") == "url_verification":
        challenge = body.get("challenge", "")
        logger.info(f"URL verification request, returning challenge: {challenge}")
        return {"challenge": challenge}

    # Verify signature
    if not client.verify_request(headers, raw_body):
        logger.warning("Invalid webhook signature")
        return {"code": -1, "msg": "invalid signature"}

    # Parse event
    event = client.parse_event(body)
    if event is None:
        # Not a P2P message or unknown event
        return {"code": 0, "msg": "ignored"}

    logger.info(f"Received P2P message: {event}")

    logger.info(f"Received P2P message: {event}")


    # Process message - check for commands first
    from src.commands.handler import parse_command, handle_command
    from src.services.streaming import stream_and_forward
    from src.services.media_handler import handle_image_message, handle_file_message
    from src.storage.session_manager import get_session_manager
    from src.opencode.client import get_opencode_client

    content = event.get("content", {})
    content_type = event.get("content_type", "text")
    user_id = event.get("user_id", "")
    chat_id = event.get("chat_id", "")
    message_id = event.get("message_id", "")

    # Handle media messages
    if content_type == "image":
        image_key = content.get("image_key", "")
        response = await handle_image_message(user_id, image_key, chat_id, message_id)
        logger.info(f"Image response: {response}")
        return {"code": 0, "msg": "success", "response": response}
    
    if content_type == "file":
        file_key = content.get("file_key", "")
        file_name = content.get("file_name", "")
        response = await handle_file_message(user_id, file_key, file_name, chat_id, message_id)
        logger.info(f"File response: {response}")
        return {"code": 0, "msg": "success", "response": response}

    # Get text content for commands and regular messages
    text_content = content.get("text", "") if isinstance(content, dict) else str(content)
    
    command, args = parse_command(text_content)
    if command:
        # Handle command and return response
        response = await handle_command(user_id, command, args, chat_id)
        logger.info(f"Command response: {response}")
        # TODO: Send response back to Feishu in Task 11
        return {"code": 0, "msg": "success", "response": response}

    # Process regular message
    logger.info(f"Received message: {text_content}")
    
    # Get current session for user
    session_manager = get_session_manager()
    current_session = session_manager.get_current_session(user_id)
    
    if not current_session:
        # No active session, prompt user to create one
        response = "⚠️ No active session. Use `/new` to create a session first."
        # TODO: Send response back to Feishu in Task 11
        return {"code": 0, "msg": "success", "response": response}
    
    try:
        # Send message to OpenCode
        opencode_client = await get_opencode_client()
        await opencode_client.send_message(
            session_id=current_session.opencode_session_id,
            content=text_content
        )
        
        # Stream response and forward to Feishu
        response_text = await stream_and_forward(
            session_id=current_session.opencode_session_id,
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id
        )
        
        # TODO: Send response back to Feishu in Task 11
        logger.info(f"Response: {response_text[:100]}...")
        return {"code": 0, "msg": "success", "response": response_text}
        
    except Exception as e:
        logger.error(f"Failed to process message: {e}", exc_info=True)
        response = f"❌ Failed to process message: {str(e)}"
        # TODO: Send error response back to Feishu in Task 11
        return {"code": 0, "msg": "success", "response": response}


@app.post("/admin/cleanup")
async def cleanup_sessions(days: int = 30) -> dict[str, Any]:
    """Clean up old sessions.
    
    Manual trigger for session cleanup. Removes inactive sessions
    not updated in the specified number of days.
    
    Args:
        days: Number of days to keep sessions (default 30)
        
    Returns:
        Number of deleted sessions
    """
    from src.storage.session_manager import get_session_manager
    
    session_manager = get_session_manager()
    deleted = session_manager.cleanup_old_sessions(days)
    return {"deleted": deleted, "message": f"Cleaned up {deleted} sessions"}




# Register error handlers
register_error_handlers(app)

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )
