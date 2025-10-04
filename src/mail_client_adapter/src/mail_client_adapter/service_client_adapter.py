"""Service client adapter implementation."""

from collections.abc import Iterator
from typing import Union

from mail_client_api.client import Client
from mail_client_api.message import Message, get_message
from .client import AuthenticatedClient
from .api import (
    delete_message_sync,
    get_message_sync,
    list_messages_sync,
    mark_as_read_sync,
)


class ServiceMessage(Message):
    """Message implementation that wraps service response data."""

    def __init__(self, message_data: dict[str, str]):
        """Initialize with message data from service response.
        
        Args:
            message_data: Dictionary containing message fields from service response
        """
        self._data = message_data

    @property
    def id(self) -> str:
        """Return the unique identifier of the message."""
        return self._data.get("id", "")

    @property
    def from_(self) -> str:
        """Return the sender's email address."""
        return self._data.get("from", "")

    @property
    def to(self) -> str:
        """Return the recipient's email address."""
        return self._data.get("to", "")

    @property
    def date(self) -> str:
        """Return the date the message was sent."""
        return self._data.get("date", "")

    @property
    def subject(self) -> str:
        """Return the subject line of the message."""
        return self._data.get("subject", "")

    @property
    def body(self) -> str:
        """Return the plain text content of the message."""
        return self._data.get("body", "")


class ServiceClientAdapter(Client):
    """Adapter that wraps the auto-generated service client to implement the Client protocol."""

    def __init__(self, service_client: AuthenticatedClient):
        """Initialize the adapter with a service client.
        
        Args:
            service_client: The authenticated service client to wrap
        """
        self._service_client = service_client

    def get_message(self, message_id: str) -> Message:
        """Return a message by its ID.
        
        Args:
            message_id: The unique identifier of the message
            
        Returns:
            Message: The requested message
            
        Raises:
            RuntimeError: If the message cannot be retrieved
        """
        try:
            response = get_message_sync(
                message_id=message_id,
                client=self._service_client
            )
            
            if response is None:
                raise RuntimeError(f"Message with ID {message_id} not found")
            
            return ServiceMessage(response)
            
        except Exception as e:
            raise RuntimeError(f"Failed to get message {message_id}: {str(e)}") from e

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID.
        
        Args:
            message_id: The unique identifier of the message to delete
            
        Returns:
            bool: True if the message was successfully deleted, False otherwise
        """
        try:
            response = delete_message_sync(
                message_id=message_id,
                client=self._service_client
            )
            
            # Check if the response indicates success
            if response is None:
                return False
                
            # The response should contain success information
            return response.get('success', True)  # Assume success if we got a response
            
        except Exception as e:
            # Log the error but return False to indicate failure
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by its ID.
        
        Args:
            message_id: The unique identifier of the message to mark as read
            
        Returns:
            bool: True if the message was successfully marked as read, False otherwise
        """
        try:
            response = mark_as_read_sync(
                message_id=message_id,
                client=self._service_client
            )
            
            # Check if the response indicates success
            if response is None:
                return False
                
            # The response should contain success information
            return response.get('success', True)  # Assume success if we got a response
            
        except Exception as e:
            # Log the error but return False to indicate failure
            return False

    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        """Return an iterator of messages from the inbox.
        
        Args:
            max_results: Maximum number of messages to return
            
        Yields:
            Message: Messages from the inbox
        """
        try:
            response = list_messages_sync(
                client=self._service_client
            )
            
            if response is None:
                return
            
            # Handle case where response is not a list
            if not isinstance(response, list):
                return
            
            # Limit results if max_results is specified and positive
            if max_results is not None and max_results > 0:
                messages_to_process = response[:max_results]
            else:
                messages_to_process = response
            
            for message_item in messages_to_process:
                yield ServiceMessage(message_item)
                
        except Exception as e:
            # If there's an error, we'll just return an empty iterator
            # In a real implementation, you might want to log this error
            return

