"""Integration tests for the adapter."""
from __future__ import annotations

from unittest.mock import MagicMock, create_autospec

import pytest
from mail_client_adapter.client import AuthenticatedClient
from mail_client_adapter.service_client_adapter import ServiceClientAdapter
from starlette.testclient import TestClient

import gmail_client_impl
import mail_client_api
from mail_client_api import Client, Message
from mail_client_service import app as service_app
from mail_client_service import get_mail_client


class DummyMessage:
    """Dummy message for testing."""

    def __init__(self, message_id: str, sender: str, recipient: str, subject: str, date: str, body: str) -> None: # noqa: PLR0913
        """Initialize the dummy message."""
        self.id = message_id
        self.from_ = sender
        self.to = recipient
        self.subject = subject
        self.date = date
        self.body = body


@pytest.mark.integration
def test_adapter_exercises_service_and_mail_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that the adapter exercises the service and mail client."""
    mock_client = create_autospec(Client, spec_set=True)

    dummy = DummyMessage(
        "int_msg",
        "tester@example.com",
        "recipient@example.com",
        "Integration Test",
        "2025-10-03T12:00:00Z",
        "This is an integration test body.",
    )

    mock_client.get_message.return_value = dummy
    mock_client.get_messages.return_value = [dummy]
    mock_client.mark_as_read.return_value = True
    mock_client.delete_message.return_value = True

    # Ensure the app's lifespan doesn't try to create a real client
    monkeypatch.setattr(mail_client_api, "get_client", lambda: mock_client, raising=True)

    # Force the FastAPI dependency to use our mock client
    service_app.dependency_overrides[get_mail_client] = lambda: mock_client  # type: ignore[assignment]

    try:
        base_url = "http://testserver"
        with TestClient(service_app, base_url=base_url) as httpx_client:
            auth_client = AuthenticatedClient(base_url=base_url, token="fake-token") # noqa: S106
            auth_client.set_httpx_client(httpx_client)

            adapter = ServiceClientAdapter(auth_client)

            got_one: Message = adapter.get_message(dummy.id)
            # Adapter returns an iterator; materialize to a list for assertions
            got_many_iter = adapter.get_messages()
            got_many: list[Message] = list(got_many_iter)

        assert got_one.id == dummy.id
        assert got_one.from_ == dummy.from_
        assert got_one.to == dummy.to
        assert got_one.subject == dummy.subject
        assert got_one.body == dummy.body

        assert isinstance(got_many, list)
        assert len(got_many) == 1
        only = got_many[0]
        assert only.id == dummy.id
        assert only.subject == "Integration Test"

        mock_client.get_message.assert_called_once_with(dummy.id)
        mock_client.get_messages.assert_called_once()
    finally:
        service_app.dependency_overrides.pop(get_mail_client, None)


@pytest.mark.integration
def test_end_to_end_service_call_with_mocked_gmail_impl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end-style integration that wires.

    mail_client_adapter -> mail_client_service -> mocked gmail_client_impl.
    """
    mock_message_data = {
        "id": "circleci_msg_123",
        "from": "sender@circleci.com",
        "to": "recipient@circleci.com",
        "subject": "CircleCI End-to-End Test",
        "date": "2025-10-04T14:30:00Z",
        "body": "This message tests the full integration stack in CI.",
    }

    mock_message = MagicMock()
    mock_message.id = mock_message_data["id"]
    mock_message.from_ = mock_message_data["from"]
    mock_message.to = mock_message_data["to"]
    mock_message.subject = mock_message_data["subject"]
    mock_message.date = mock_message_data["date"]
    mock_message.body = mock_message_data["body"]

    mock_gmail_client = MagicMock(spec=gmail_client_impl.GmailClient)
    mock_gmail_client.get_message.return_value = mock_message
    mock_gmail_client.get_messages.return_value = [mock_message]
    mock_gmail_client.mark_as_read.return_value = True
    mock_gmail_client.delete_message.return_value = True

    # Prevent the app lifespan from creating a real Gmail client
    monkeypatch.setattr(
        mail_client_api,
        "get_client",
        lambda: mock_gmail_client,
        raising=True,
    )

    # Override FastAPI dependency to use the mocked Gmail client
    service_app.dependency_overrides[get_mail_client] = lambda: mock_gmail_client  # type: ignore[assignment]

    try:
        base_url = "http://testserver"
        with TestClient(service_app, base_url=base_url) as httpx_client:
            auth_client = AuthenticatedClient(base_url=base_url, token="circleci-test-token") # noqa: S106
            auth_client.set_httpx_client(httpx_client)

            adapter = ServiceClientAdapter(auth_client)

            # Single message flow
            retrieved_message = adapter.get_message(mock_message_data["id"])
            assert retrieved_message.id == mock_message_data["id"]
            assert retrieved_message.from_ == mock_message_data["from"]
            assert retrieved_message.to == mock_message_data["to"]
            assert retrieved_message.subject == mock_message_data["subject"]
            assert retrieved_message.date == mock_message_data["date"]
            assert retrieved_message.body == mock_message_data["body"]

            # Messages list flow (adapter returns iterator)
            retrieved_messages = list(adapter.get_messages())
            assert len(retrieved_messages) == 1
            first_message = retrieved_messages[0]
            assert first_message.id == mock_message_data["id"]
            assert first_message.subject == mock_message_data["subject"]

            # Mark-as-read and delete
            assert adapter.mark_as_read(mock_message_data["id"]) is True
            assert adapter.delete_message(mock_message_data["id"]) is True

            # Verify delegation to mocked Gmail client
            mock_gmail_client.get_message.assert_called_with(mock_message_data["id"])
            mock_gmail_client.get_messages.assert_called_once()
            mock_gmail_client.mark_as_read.assert_called_with(mock_message_data["id"])
            mock_gmail_client.delete_message.assert_called_with(mock_message_data["id"])
    finally:
        service_app.dependency_overrides.pop(get_mail_client, None)
