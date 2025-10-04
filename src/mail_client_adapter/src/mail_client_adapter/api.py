"""API functions for mail service."""

from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from .client import AuthenticatedClient, Client
from .models import (
    DeleteMessageResponse,
    GetMessageResponse,
    ListMessagesResponse,
    MarkAsReadResponse,
)


def list_messages_sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[list[dict[str, str]]]:
    """List Messages

     Get a list of messages from the mail client.

    Args:
        client: The client to use for the request

    Returns:
        List of message dictionaries
    """
    kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/messages",
    }

    response = client.get_httpx_client().request(**kwargs)
    
    if response.status_code == 200:
        return response.json()
    else:
        if client.raise_on_unexpected_status:
            raise Exception(f"Unexpected status code: {response.status_code}")
        return None


def get_message_sync(
    message_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[dict[str, str]]:
    """Get Message

     Get a specific message by ID.

    Args:
        message_id: The ID of the message to retrieve
        client: The client to use for the request

    Returns:
        Message dictionary or None if not found
    """
    kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/messages/{message_id}",
    }

    response = client.get_httpx_client().request(**kwargs)
    
    if response.status_code == 200:
        return response.json()
    else:
        if client.raise_on_unexpected_status:
            raise Exception(f"Unexpected status code: {response.status_code}")
        return None


def delete_message_sync(
    message_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[dict[str, Any]]:
    """Delete Message

     Delete a message by ID by delegating to the mail client implementation.

    Args:
        message_id: The ID of the message to delete
        client: The client to use for the request

    Returns:
        Response dictionary or None if failed
    """
    kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/messages/{message_id}",
    }

    response = client.get_httpx_client().request(**kwargs)
    
    if response.status_code == 200:
        return response.json()
    else:
        if client.raise_on_unexpected_status:
            raise Exception(f"Unexpected status code: {response.status_code}")
        return None


def mark_as_read_sync(
    message_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[dict[str, Any]]:
    """Mark As Read

     Mark a message as read by delegating to the mail client implementation.

    Args:
        message_id: The ID of the message to mark as read
        client: The client to use for the request

    Returns:
        Response dictionary or None if failed
    """
    kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/messages/{message_id}/mark-as-read",
    }

    response = client.get_httpx_client().request(**kwargs)
    
    if response.status_code == 200:
        return response.json()
    else:
        if client.raise_on_unexpected_status:
            raise Exception(f"Unexpected status code: {response.status_code}")
        return None
