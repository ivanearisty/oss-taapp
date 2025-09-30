"""Core mail client protocol definitions and factory placeholder."""

from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from mail_client_api.message import Message

__all__ = ["Client", "get_client"]


@runtime_checkable
class Client(Protocol):
    """Protocol representing a mail client for email operations."""

    def get_message(self, message_id: str) -> Message:
        """Return a message by its ID."""
        raise NotImplementedError

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        raise NotImplementedError

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID."""
        raise NotImplementedError

    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        """Return an iterator of messages from the inbox."""
        raise NotImplementedError


def get_client(*, interactive: bool = False) -> Client:
    """Return an instance of a Mail Client."""
    raise NotImplementedError
