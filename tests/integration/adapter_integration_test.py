from __future__ import annotations
from typing import List
from unittest.mock import create_autospec, patch, MagicMock
from starlette.testclient import TestClient
import pytest
import mail_client_api
from mail_client_api import Message, Client
from mail_client_service.app import app as service_app, get_mail_client
from mail_client_adapter.client import AuthenticatedClient
from mail_client_adapter.service_client_adapter import ServiceClientAdapter
import gmail_client_impl


class DummyMessage:
    def __init__(
        self, id: str, sender: str, recipient: str, subject: str, date: str, body: str
    ) -> None:
        self.id = id
        # Use the correct property names that match the Message interface
        self.from_ = sender  # Note: from_ not sender
        self.to = recipient  # Note: to not recipient
        self.subject = subject
        self.date = date
        self.body = body


@pytest.mark.integration
def test_adapter_exercises_service_and_mail_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    monkeypatch.setattr(
        mail_client_api,
        "get_client",
        lambda interactive=True: mock_client,
        raising=True,
    )

    # 关键：覆盖依赖，强制服务使用我们的 mock_client
    service_app.dependency_overrides[get_mail_client] = lambda: mock_client  # type: ignore[assignment]

    try:
        base_url = "http://testserver"
        with TestClient(service_app, base_url=base_url) as httpx_client:
            auth_client = AuthenticatedClient(base_url=base_url, token="fake-token")
            auth_client.set_httpx_client(httpx_client)

            adapter = ServiceClientAdapter(auth_client)

            got_one: Message = adapter.get_message(dummy.id)
            got_many: List[Message] = adapter.get_messages()

        # 断言
        assert got_one.id == dummy.id
        assert got_one.from_ == dummy.from_  # Updated to use from_
        assert got_one.to == dummy.to  # Updated to use to
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
def test_end_to_end_service_call_with_mocked_gmail_impl() -> None:
    """
    CircleCI integration test that verifies end-to-end service call:
    mail_client_adapter -> mail_client_service -> mocked gmail_client_impl

    This test ensures all layers are connected correctly by:
    1. Mocking the Gmail API layer (gmail_client_impl)
    2. Running the actual FastAPI service
    3. Using the mail_client_adapter to make HTTP calls
    4. Verifying data flows correctly through all layers
    """
    # Create mock message data that mimics GmailMessage structure
    mock_message_data = {
        "id": "circleci_msg_123",
        "from": "sender@circleci.com",
        "to": "recipient@circleci.com",
        "subject": "CircleCI End-to-End Test",
        "date": "2025-10-04T14:30:00Z",
        "body": "This message tests the full integration stack in CircleCI.",
    }

    # Create a mock message object that behaves like GmailMessage
    mock_message = MagicMock()
    mock_message.id = mock_message_data["id"]
    mock_message.from_ = mock_message_data["from"]
    mock_message.to = mock_message_data["to"]
    mock_message.subject = mock_message_data["subject"]
    mock_message.date = mock_message_data["date"]
    mock_message.body = mock_message_data["body"]

    # Mock the GmailClient at the implementation level
    mock_gmail_client = MagicMock(spec=gmail_client_impl.GmailClient)
    mock_gmail_client.get_message.return_value = mock_message
    mock_gmail_client.get_messages.return_value = [mock_message]
    mock_gmail_client.mark_as_read.return_value = True
    mock_gmail_client.delete_message.return_value = True

    # Use dependency override to inject our mock client into the service
    # This is the key difference from the first test - we override the service dependency
    service_app.dependency_overrides[get_mail_client] = lambda: mock_gmail_client  # type: ignore[assignment]

    try:
        base_url = "http://testserver"

        with TestClient(service_app, base_url=base_url) as httpx_client:
            # Create authenticated client for the adapter
            auth_client = AuthenticatedClient(
                base_url=base_url, token="circleci-test-token"
            )
            auth_client.set_httpx_client(httpx_client)

            # Create the service client adapter - this is our entry point
            adapter = ServiceClientAdapter(auth_client)

            # Test 1: Get single message through the full stack
            retrieved_message = adapter.get_message(mock_message_data["id"])

            # Verify the message data flowed correctly through all layers
            assert retrieved_message.id == mock_message_data["id"]
            assert retrieved_message.from_ == mock_message_data["from"]
            assert retrieved_message.to == mock_message_data["to"]
            assert retrieved_message.subject == mock_message_data["subject"]
            assert retrieved_message.date == mock_message_data["date"]
            assert retrieved_message.body == mock_message_data["body"]

            # Test 2: Get messages list through the full stack
            retrieved_messages = list(adapter.get_messages())

            # Verify messages list functionality
            assert len(retrieved_messages) == 1
            first_message = retrieved_messages[0]
            assert first_message.id == mock_message_data["id"]
            assert first_message.subject == mock_message_data["subject"]

            # Test 3: Mark as read through the full stack
            mark_result = adapter.mark_as_read(mock_message_data["id"])
            assert mark_result is True

            # Test 4: Delete message through the full stack
            delete_result = adapter.delete_message(mock_message_data["id"])
            assert delete_result is True

            # Verify that the mocked Gmail client was called correctly
            # This ensures the service layer properly delegates to the implementation
            mock_gmail_client.get_message.assert_called_with(mock_message_data["id"])
            mock_gmail_client.get_messages.assert_called_once()
            mock_gmail_client.mark_as_read.assert_called_with(mock_message_data["id"])
            mock_gmail_client.delete_message.assert_called_with(mock_message_data["id"])

    finally:
        # Clean up the dependency override
        service_app.dependency_overrides.pop(get_mail_client, None)
