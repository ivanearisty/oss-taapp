"""Module for the GmailClient implementation."""

import mail_client_api

from ._impl import GmailClient

def get_client_impl() -> mail_client_api.Client:
    """Get an instance of the GmailClient."""
    return GmailClient()

# --- Dependency Injection ---
# Override the get_client function in the protocol package
# Now, anyone calling mail_client_api.get_client() will get our implementation.
mail_client_api.get_client = get_client_impl
# --- Dependency Injection ---
