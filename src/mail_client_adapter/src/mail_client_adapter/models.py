"""Simple models for API responses."""

from typing import Any


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
