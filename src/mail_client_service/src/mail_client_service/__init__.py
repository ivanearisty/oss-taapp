"""Public package interface for the Mail Client Service.

Exports the FastAPI `app`, the dependency getter `get_client`, and the
Pydantic schemas used by the service. Also exposes the package version
via `__version__`.
"""

from importlib import metadata as importlib_metadata

try:
    __version__ = importlib_metadata.version("mail-client-service")
except importlib_metadata.PackageNotFoundError:
    # Fallback when running from source without installation
    __version__ = "0.0.0"

from .main import app, get_client  # noqa: E402
from .schemas import MessageSchema, StatusResponse  # noqa: E402

__all__ = [
    "app",
    "get_client",
    "MessageSchema",
    "StatusResponse",
    "__version__",
]


