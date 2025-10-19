"""Mail client adapter package for wrapping auto-generated client."""

from mail_client_service_client import Client

from .service_client_adapter import ServiceClientAdapter

__all__ = ["ServiceClientAdapter", "create_service_adapter"]


def create_service_adapter(base_url: str) -> ServiceClientAdapter:
    """Create a ServiceClientAdapter with the given service configuration.

    Args:
        base_url: The base URL of the mail service

    Returns:
        ServiceClientAdapter: Configured adapter instance

    """
    service_client = Client(base_url=base_url)

    return ServiceClientAdapter(service_client)
