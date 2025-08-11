"""Gmail Message Implementation Package.

This module handles the dependency injection for the Gmail message implementation
and exposes the concrete `GmailMessage` class for direct use if needed.

Upon import, this module overrides the `get_message` factory function in the
`message` package, making `GmailMessage` the default implementation for all
code that uses `message.get_message()`.

Exports:
    GmailMessage: The concrete Gmail message implementation.
    get_message_impl: Factory function for creating GmailMessage instances.
"""

import message

from ._impl import GmailMessage


def get_message_impl(msg_id: str, raw_data: str) -> message.Message:
    """Return an instance of the concrete GmailMessage implementation.

    This factory function creates a GmailMessage instance that implements
    the Message protocol. It serves as the concrete implementation for
    the message.get_message() factory function.

    Args:
        msg_id (str): The unique identifier for the message from Gmail.
        raw_data (str): The base64url-encoded raw email data from Gmail API.

    Returns:
        message.Message: An instance of GmailMessage conforming to the Message protocol.

    Example:
        >>> msg = get_message_impl("12345", "encoded_data...")
        >>> print(msg.subject)
        "Important Email Subject"

    """
    return GmailMessage(msg_id=msg_id, raw_data=raw_data)


# --- Dependency Injection ---
# Override the get_message function in the protocol package
# Now, anyone calling message.get_message(id, data) will get our implementation.
message.get_message = get_message_impl
# --- Dependency Injection ---
