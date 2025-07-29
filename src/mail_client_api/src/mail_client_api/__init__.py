"""Mail Client API - Core protocols and contracts.

This module defines the core protocols (interfaces) for the mail client system.
It provides abstract contracts that concrete implementations must follow.

The main protocols are:

- Message: Defines the structure of an email message
- Client: Defines the operations a mail client must support

Usage:
    from mail_client_api import get_client, Message, Client
    
    client = get_client()  # Returns concrete implementation

    messages = client.get_messages()
"""

from typing import Iterator, Protocol, runtime_checkable

class Message(Protocol):
    """A Mail Message."""

    @property
    def id(self) -> str:
        """Return the unique identifier of the message.
        
        Returns:
            str: The unique message identifier.
        """
        raise NotImplementedError()

    @property
    def from_(self) -> str:
        """Return the sender's email address.
        
        Returns:
            str: The email address of the message sender.
        """
        raise NotImplementedError()

    @property
    def to(self) -> str:
        """Return the recipient's email address.
        
        Returns:
            str: The email address of the message recipient.
        """
        raise NotImplementedError()

    @property
    def date(self) -> str:
        """Return the date the message was sent.
        
        Returns:
            str: The date string when the message was sent.
        """
        raise NotImplementedError()

    @property
    def subject(self) -> str:
        """Return the subject line of the message.
        
        Returns:
            str: The message subject line.
        """
        raise NotImplementedError()

    @property
    def body(self) -> str:
        """Return the plain text content of the message.
        
        Returns:
            str: The plain text body content of the message.
        """
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
        """Delete a message by its ID.
        
        Args:
            message_id (str): The ID of the message to delete.
            
        Returns:
            bool: True if the message was successfully deleted, False otherwise.
        """
        raise NotImplementedError()

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID.
        
        Args:
            message_id (str): The ID of the message to mark as read.
            
        Returns:
            bool: True if the message was successfully marked as read, False otherwise.
        """
        raise NotImplementedError()

    def get_messages(self) -> Iterator[Message]:
        """Return an iterator of all messages in the inbox.
        
        Returns:
            Iterator[Message]: An iterator yielding Message objects from the inbox.
        """
        raise NotImplementedError()


def get_client() -> Client:
    """Return an instance of a Mail Client.
    
    This is a factory function that returns a concrete implementation
    of the Client protocol. The actual implementation is injected
    by implementation packages.
    
    Returns:
        Client: A concrete mail client instance.
        
    Raises:
        NotImplementedError: If no implementation has been registered.
    """
    raise NotImplementedError()