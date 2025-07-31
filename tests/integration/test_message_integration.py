"""Tests for gmail_message_impl factory function.

This module tests the get_message_impl factory function in isolation,
without dependencies on other components or external systems.
"""

import base64

import pytest

from gmail_message_impl import get_message_impl
from gmail_message_impl._impl import GmailMessage

# Mark all tests in this file as suitable for CI
pytestmark = [pytest.mark.integration, pytest.mark.circleci]


class TestMessageFactory:
    """Test cases for the message factory function."""

    def test_get_message_impl_returns_gmail_message(self) -> None:
        """Test that get_message_impl returns a GmailMessage instance."""
        # Create test data
        email_content = (
            "From: test@example.com\r\n"
            "Subject: Factory Test\r\n"
            "\r\n"
            "Test message body"
        )
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()

        # Call factory function
        msg = get_message_impl(msg_id="factory123", raw_data=encoded_data)

        # Verify it returns a GmailMessage instance
        assert isinstance(msg, GmailMessage)
        assert msg.id == "factory123"
        assert msg.from_ == "test@example.com"
        assert msg.subject == "Factory Test"
        assert msg.body == "Test message body"

    def test_message_protocol_compliance(self) -> None:
        """Test that GmailMessage implements the Message protocol correctly."""
        email_content = (
            "From: protocol@example.com\r\n"
            "To: recipient@example.com\r\n"
            "Subject: Protocol Test\r\n"
            "Date: Wed, 30 Jul 2025 12:00:00 +0000\r\n"
            "\r\n"
            "Protocol compliance test"
        )
        encoded_data = base64.urlsafe_b64encode(email_content.encode()).decode()

        msg = get_message_impl(msg_id="protocol123", raw_data=encoded_data)

        # Test all required Message protocol properties
        assert hasattr(msg, "id")
        assert hasattr(msg, "from_")
        assert hasattr(msg, "to")
        assert hasattr(msg, "subject")
        assert hasattr(msg, "date")
        assert hasattr(msg, "body")

        # Test that properties return expected types
        assert isinstance(msg.id, str)
        assert isinstance(msg.from_, str)
        assert isinstance(msg.to, str)
        assert isinstance(msg.subject, str)
        assert isinstance(msg.date, str)
        assert isinstance(msg.body, str)

        # Test actual values
        assert msg.id == "protocol123"
        assert msg.from_ == "protocol@example.com"
        assert msg.to == "recipient@example.com"
        assert msg.subject == "Protocol Test"
        assert msg.date == "07/30/2025"
        assert msg.body == "Protocol compliance test"

    def test_factory_with_empty_data(self) -> None:
        """Test factory function with empty/minimal data."""
        # Test with minimal valid base64 data
        minimal_email = "\r\n\r\n"
        encoded_data = base64.urlsafe_b64encode(minimal_email.encode()).decode()

        msg = get_message_impl(msg_id="empty123", raw_data=encoded_data)

        assert isinstance(msg, GmailMessage)
        assert msg.id == "empty123"
        # Should handle empty fields gracefully
        assert msg.from_ == ""
        assert msg.to == ""
        assert msg.subject == ""

    def test_factory_parameter_validation(self) -> None:
        """Test that factory function handles various parameter inputs."""
        # Test with different msg_id formats
        test_cases = [
            ("12345", "simple_id"),
            ("gmail_msg_67890", "prefixed_id"),
            ("msg-with-hyphens-123", "hyphenated_id"),
            ("", "empty_id"),  # Edge case
        ]

        simple_email = "Subject: Test\r\n\r\nBody"
        encoded_data = base64.urlsafe_b64encode(simple_email.encode()).decode()

        for msg_id, test_name in test_cases:
            msg = get_message_impl(msg_id=msg_id, raw_data=encoded_data)
            assert msg.id == msg_id, f"Failed for {test_name}"
            assert isinstance(msg, GmailMessage), f"Failed for {test_name}"
