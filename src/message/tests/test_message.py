"""Tests for the message API protocol.

This module contains unit tests that verify the contracts and behavior
of the message.Message protocol. These tests use mocks to demonstrate
how implementations should behave and serve as documentation for the
expected API contracts.
"""
from unittest.mock import Mock

from message import Message


def test_message_id_property() -> None:
    """Verifies and demonstrates the contract for the `id` property.

    This test ensures that any implementation of the `Message` protocol
    must have an `id` property that returns a string identifier.
    """
    # ARRANGE: Create a mock that conforms to the Message protocol.
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_12345"

    # ACT: Access the id property as a consumer would.
    message_id = mock_message.id

    # ASSERT: Verify the property returns the expected value.
    assert message_id == "msg_12345"
    assert isinstance(message_id, str)


def test_message_from_property() -> None:
    """Verifies and demonstrates the contract for the `from_` property.

    This test ensures that any implementation of the `Message` protocol
    must have a `from_` property that returns the sender's email address.
    """
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.from_ = "sender@example.com"

    # ACT
    sender_email = mock_message.from_

    # ASSERT
    assert sender_email == "sender@example.com"
    assert isinstance(sender_email, str)


def test_message_to_property() -> None:
    """Verifies and demonstrates the contract for the `to` property.

    This test ensures that any implementation of the `Message` protocol
    must have a `to` property that returns the recipient's email address.
    """
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.to = "recipient@example.com"

    # ACT
    recipient_email = mock_message.to

    # ASSERT
    assert recipient_email == "recipient@example.com"
    assert isinstance(recipient_email, str)


def test_message_date_property() -> None:
    """Verifies and demonstrates the contract for the `date` property.

    This test ensures that any implementation of the `Message` protocol
    must have a `date` property that returns the date string when the message was sent.
    """
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.date = "2025-07-30 10:30:00"

    # ACT
    message_date = mock_message.date

    # ASSERT
    assert message_date == "2025-07-30 10:30:00"
    assert isinstance(message_date, str)


def test_message_subject_property() -> None:
    """Verifies and demonstrates the contract for the `subject` property.

    This test ensures that any implementation of the `Message` protocol
    must have a `subject` property that returns the message subject line.
    """
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.subject = "Important Meeting Tomorrow"

    # ACT
    message_subject = mock_message.subject

    # ASSERT
    assert message_subject == "Important Meeting Tomorrow"
    assert isinstance(message_subject, str)


def test_message_body_property() -> None:
    """Verifies and demonstrates the contract for the `body` property.

    This test ensures that any implementation of the `Message` protocol
    must have a `body` property that returns the plain text content of the message.
    """
    # ARRANGE
    mock_message = Mock(spec=Message)
    mock_message.body = "This is the message body content with important information."

    # ACT
    message_body = mock_message.body

    # ASSERT
    assert message_body == "This is the message body content with important information."
    assert isinstance(message_body, str)


def test_message_protocol_comprehensive() -> None:
    """Verifies all properties work together in a comprehensive test.

    This test demonstrates how all Message protocol properties can be used
    together and verifies the complete contract.
    """
    # ARRANGE: Create a complete mock message with all properties
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_67890"
    mock_message.from_ = "alice@company.com"
    mock_message.to = "bob@company.com"
    mock_message.date = "2025-07-30 14:45:30"
    mock_message.subject = "Project Update"
    mock_message.body = "Here are the latest updates on our project progress."

    # ACT: Access all properties
    properties = {
        "id": mock_message.id,
        "from_": mock_message.from_,
        "to": mock_message.to,
        "date": mock_message.date,
        "subject": mock_message.subject,
        "body": mock_message.body,
    }

    # ASSERT: Verify all properties return expected values and types
    assert properties["id"] == "msg_67890"
    assert properties["from_"] == "alice@company.com"
    assert properties["to"] == "bob@company.com"
    assert properties["date"] == "2025-07-30 14:45:30"
    assert properties["subject"] == "Project Update"
    assert properties["body"] == "Here are the latest updates on our project progress."

    # Verify all properties return strings
    for prop_value in properties.values():
        assert isinstance(prop_value, str)
