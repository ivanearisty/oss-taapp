"""Gmail Client Implementation Package.

This module handles the dependency injection for the Gmail client
and exposes the concrete `GmailClient` class for direct use if needed.

Upon import, this module overrides the `get_client` factory function in the
`mail_client_api` package, making `GmailClient` the default implementation
for all code that uses `mail_client_api.get_client()`.

Exports:
    GmailClient: The concrete Gmail client implementation.
    get_client_impl: Factory function for creating GmailClient instances.
"""

import mail_client_api

from ._impl import GmailClient

# Export the main class so it's documented by mkdocstrings
__all__ = ["GmailClient", "get_client_impl"]


def get_client_impl(interactive: bool = False) -> mail_client_api.Client:
    """Get an instance of the GmailClient.

    This factory function creates and returns a new GmailClient instance
    with default authentication handling.

    Args:
        interactive (bool): If True, the client may prompt for user input
        during initialization (e.g., for OAuth2 flow). If False, it will
        use environment variables or other non-interactive methods.

    Returns:
        mail_client_api.Client: A GmailClient instance implementing the
        mail_client_api.Client protocol.

    """
    return GmailClient(interactive=interactive)


# --- Dependency Injection ---
# Override the get_client function in the protocol package
# Now, anyone calling mail_client_api.get_client() will get our implementation.
mail_client_api.get_client = get_client_impl
# --- Dependency Injection ---
