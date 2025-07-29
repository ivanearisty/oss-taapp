"""A Mail Client Protocol"""

from typing import Iterator, Protocol, runtime_checkable

class Message(Protocol):
    """A Mail Message."""

    @property
    def id(self) -> str:
        """Return the id of the message."""
        raise NotImplementedError()

    @property
    def from_(self) -> str:
        """Return the sender of the message."""
        raise NotImplementedError()

    @property
    def to(self) -> str:
        """Return the recipient of the message."""
        raise NotImplementedError()

    @property
    def date(self) -> str:
        """Return the date of the message."""
        raise NotImplementedError()

    @property
    def subject(self) -> str:
        """Return the subject of the message."""
        raise NotImplementedError()

    @property
    def body(self) -> str:
        """Return the body of the message."""
        raise NotImplementedError()


class Client(Protocol):
    """A Mail Client used to fetch messages."""

    def get_message(self, message_id: str) -> Message:
        """
        Return a message by its ID.
        
        Args:
            message_id (str): The ID of the message to retrieve.
        
        Returns:
            Message: The message object corresponding to the given ID.
        """
        raise NotImplementedError()
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        raise NotImplementedError()

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID."""
        raise NotImplementedError()

    def get_messages(self) -> Iterator[Message]:
        """Return an iterator of messages."""
        raise NotImplementedError()


def get_client() -> Client:
    """Return an instance of a Mail Client."""
    raise NotImplementedError()