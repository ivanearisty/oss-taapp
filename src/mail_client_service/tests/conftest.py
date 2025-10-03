"""Test configuration for mail client service."""

from unittest.mock import Mock, create_autospec

import os
import pytest
from fastapi.testclient import TestClient
from mail_client_api import Client, Message

from mail_client_service.app import app, get_mail_client
from enum import Enum

LONG_BODY_LEN = 10_000


class HTTPStatus(Enum):
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


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


USE_REAL = os.getenv("USE_REAL_MAIL_CLIENT", "0") == "1"

# Create mock client and client TestClient only when not running real integration
mock_mail_client = None
client = None
if not USE_REAL:
    mock_mail_client = create_autospec(Client, spec_set=True)
    mock_mail_client.get_messages.return_value = []
    mock_mail_client.get_message.return_value = create_mock_message(
        "default_id",
        "noreply@example.com",
        "recipient@example.com",
        "(no subject)",
        "1970-01-01T00:00:00Z",
        "",
    )
    mock_mail_client.mark_as_read.return_value = True
    mock_mail_client.delete_message.return_value = True

    # Override the dependency once
    app.dependency_overrides[get_mail_client] = lambda: mock_mail_client

    # Create the test client once
    client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test() -> None:
    """Reset mock state before each test (but reuse the same mock object).

    Note: when running real integration tests (USE_REAL_MAIL_CLIENT=1) the
    mocked client is not created and this fixture is a no-op.
    """
    if not USE_REAL and mock_mail_client is not None:
        # Just reset the mock's call history and side effects, don't recreate it
        mock_mail_client.reset_mock()
        # Clear any side effects from previous tests
        mock_mail_client.get_messages.side_effect = None
        mock_mail_client.get_message.side_effect = None
        mock_mail_client.mark_as_read.side_effect = None
        mock_mail_client.delete_message.side_effect = None
