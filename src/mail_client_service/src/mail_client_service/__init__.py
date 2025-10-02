"""Mail Client Service package."""

# Re-export FastAPI app for ASGI servers (e.g., uvicorn: mail_client_service.app:app)
from .app import app  # noqa: F401


