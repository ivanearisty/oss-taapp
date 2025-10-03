"""Test configuration for mail client service."""

from unittest.mock import Mock, create_autospec

import pytest
from fastapi.testclient import TestClient
from mail_client_api import Client, Message

from mail_client_service.app import app, get_mail_client


def create_mock_message(
    msg_id: str,
    from_: str,
    to: str,
    subject: str,
    date: str,
    body: str,
) -> Mock:
    """Create a mock message object with the given properties."""
    mock_msg = create_autospec(Message, spec_set=True)
    mock_msg.id = msg_id
    mock_msg.from_ = from_
    mock_msg.to = to
    mock_msg.subject = subject
    mock_msg.date = date
    mock_msg.body = body
    return mock_msg


# Create mock client once (reused across all tests)
mock_mail_client = create_autospec(Client, spec_set=True)

# Override the dependency once
app.dependency_overrides[get_mail_client] = lambda: mock_mail_client

# Create the test client once
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test() -> None:
    """Reset mock state before each test (but reuse the same mock object)."""
    # Just reset the mock's call history and side effects, don't recreate it
    mock_mail_client.reset_mock()
    # Clear any side effects from previous tests
    mock_mail_client.get_messages.side_effect = None
    mock_mail_client.get_message.side_effect = None
