"""Test configuration for mail client service."""

from enum import Enum
from typing import cast
from unittest.mock import Mock, create_autospec

import pytest
from fastapi.testclient import TestClient
from mail_client_api import Client, Message

from mail_client_service import app, get_mail_client

LONG_BODY_LEN = 10_000


class HTTPStatus(Enum):
    """HTTP status codes used in the API."""

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


def create_mock_message(  # noqa: PLR0913
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
    return cast("Mock", mock_msg)


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
    mock_mail_client.mark_as_read.side_effect = None
    mock_mail_client.delete_message.side_effect = None
