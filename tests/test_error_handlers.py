"""Test error handlers integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.middleware.error_handler import register_error_handlers
from fastapi import FastAPI


def test_error_handlers_registration():
    """Verify error handlers can be registered."""
    app = FastAPI()

    # Register handlers
    register_error_handlers(app)

    # Verify handlers are present
    from fastapi.exceptions import RequestValidationError

    assert Exception in app.exception_handlers, "Generic Exception handler not found"
    assert RequestValidationError in app.exception_handlers, (
        "RequestValidationError handler not found"
    )

    print("[PASS] Error handlers registered successfully")
    print(f"[INFO] Total exception handlers: {len(app.exception_handlers)}")
    print("[PASS] All required handlers present")
    return True


if __name__ == "__main__":
    try:
        test_error_handlers_registration()
        print("\n[SUCCESS] All tests passed!")
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
