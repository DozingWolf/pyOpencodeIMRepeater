"""Media handler service for processing files and images."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def handle_multi_file_message(
    user_id: str, files: List[Dict[str, Any]], chat_id: str, message_id: str
) -> str:
    """Handle message with multiple files.

    Args:
        user_id: Feishu user ID
        files: List of file info dicts with file_key, file_name, type
        chat_id: Feishu chat ID
        message_id: Feishu message ID

    Returns:
        Response text
    """
    logger.info(f"Received {len(files)} files from user {user_id}")

    results = []
    for i, file_info in enumerate(files, 1):
        file_type = file_info.get("type", "file")
        file_name = file_info.get("file_name", f"file_{i}")
        results.append(f"{i}. {file_name} ({file_type})")

    # TODO: Process each file individually
    # for file_info in files:
    #     if file_info["type"] == "image":
    #         await handle_image_message(...)
    #     else:
    #         await handle_file_message(...)

    return (
        f"📦 Received {len(files)} files:\n\n"
        + "\n".join(results)
        + "\n\nMulti-file processing will be available soon."
    )


async def handle_image_message(
    user_id: str,
    image_key: str,
    chat_id: str,
    message_id: str
) -> str:
    """Handle incoming image message from Feishu.
    
    Args:
        user_id: Feishu user ID
        image_key: Feishu image key for download
        chat_id: Feishu chat ID
        message_id: Feishu message ID
        
    Returns:
        Response text
    """
    logger.info(f"Received image from user {user_id}: image_key={image_key}")
    
    # TODO: Download image from Feishu
    # feishu_client = get_feishu_client()
    # image_data = await feishu_client.download_image(image_key)
    
    # TODO: Upload to OpenCode
    # opencode_client = await get_opencode_client()
    # attachment = await opencode_client.upload_file(image_data, "image.png")
    
    # Placeholder response
    return "🖼️ I received your image! Image processing will be available soon.\n\n(Image support requires Feishu file download API configuration)"


async def handle_file_message(
    user_id: str,
    file_key: str,
    file_name: str,
    chat_id: str,
    message_id: str
) -> str:
    """Handle incoming file message from Feishu.
    
    Args:
        user_id: Feishu user ID
        file_key: Feishu file key for download
        file_name: Original file name
        chat_id: Feishu chat ID
        message_id: Feishu message ID
        
    Returns:
        Response text
    """
    logger.info(f"Received file from user {user_id}: file_name={file_name}, file_key={file_key}")
    
    # TODO: Download file from Feishu
    # feishu_client = get_feishu_client()
    # file_data = await feishu_client.download_file(file_key)
    
    # TODO: Upload to OpenCode
    # opencode_client = await get_opencode_client()
    # attachment = await opencode_client.upload_file(file_data, file_name)
    
    # Placeholder response
    return f"📎 I received your file: **{file_name}**\n\nFile processing will be available soon.\n(File support requires Feishu file download API configuration)"
