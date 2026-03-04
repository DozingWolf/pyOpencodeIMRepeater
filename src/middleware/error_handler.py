"""Error handling middleware for FastAPI application."""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions.

    Logs full stack trace and returns user-friendly error message.
    Includes error ID for tracking purposes.
    """
    error_id = id(exc)  # Simple error ID for tracking
    logger.error(
        f"Unhandled exception (ID: {error_id}): {exc}\nTraceback:\n{traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": -1,
            "msg": "An internal error occurred",
            "error_id": error_id,
            "detail": str(exc) if logger.isEnabledFor(logging.DEBUG) else None,
            "show_details": True,  # Flag to show detailed error button
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors.

    Logs validation errors and returns detailed error information.
    """
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": -1, "msg": "Invalid request data", "errors": exc.errors()},
    )


def register_error_handlers(app):
    """Register error handlers with FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    logger.info("Error handlers registered")
