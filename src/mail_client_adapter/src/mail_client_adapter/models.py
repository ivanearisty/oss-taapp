"""Simple models for API responses."""

from typing import Any

from mail_client_api.message import Message


class ServiceMessage(Message):
    """Message implementation that wraps service response data."""

    def __init__(self, message_data: dict[str, str]) -> None:
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


class ListMessagesResponse:
    """Response for list messages API."""

    def __init__(self, data: list[dict[str, str]]) -> None:
        """Initialize the response with message data.

        Args:
            data: List of message dictionaries containing message data.

        """
        self.data = data

    def to_dict(self) -> list[dict[str, str]]:
        """Convert the response to a dictionary format.

        Returns:
            List of message dictionaries.

        """
        return self.data


class GetMessageResponse:
    """Response for get message API."""

    def __init__(self, data: dict[str, str]) -> None:
        """Initialize the response with message data.

        Args:
            data: Dictionary containing message data.

        """
        self.data = data

    def to_dict(self) -> dict[str, str]:
        """Convert the response to a dictionary format.

        Returns:
            Dictionary containing message data.

        """
        return self.data


class DeleteMessageResponse:
    """Response for delete message API."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize the response with deletion result data.

        Args:
            data: Dictionary containing deletion result data.

        """
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary format.

        Returns:
            Dictionary containing deletion result data.

        """
        return self.data


class MarkAsReadResponse:
    """Response for mark as read API."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize the response with mark as read result data.

        Args:
            data: Dictionary containing mark as read result data.

        """
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary format.

        Returns:
            Dictionary containing mark as read result data.

        """
        return self.data
