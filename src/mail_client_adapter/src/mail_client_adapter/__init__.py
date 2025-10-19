"""Mail client adapter package for wrapping auto-generated client."""

from .client import AuthenticatedClient
from .service_client_adapter import ServiceClientAdapter

__all__ = ["ServiceClientAdapter", "create_service_adapter"]


def create_service_adapter(base_url: str, token: str) -> ServiceClientAdapter:
    """Create a ServiceClientAdapter with the given service configuration.

    Args:
        base_url: The base URL of the mail service
        token: Authentication token for the service

    Returns:
        ServiceClientAdapter: Configured adapter instance

    """
    service_client = AuthenticatedClient(base_url=base_url, token=token)

    return ServiceClientAdapter(service_client)
