"""Integration tests for message retrieval and parsing flow.

This module tests the full flow of fetching and parsing real email messages
from the Gmail API through the entire component stack.
"""

import pytest

import mail_client_api
from gmail_message_impl._impl import GmailMessage

# Mark all tests in this file as integration tests requiring local credentials
pytestmark = [pytest.mark.integration, pytest.mark.local_credentials]


def test_retrieve_and_parse_real_messages() -> None:
    """Tests the full flow of fetching and parsing a real email message.
    
    Requires at least one email in the test account's inbox.
    """
    try:
        client = mail_client_api.get_client(interactive=False)
        messages = client.get_messages(max_results=1)

        first_message = next(messages, None)

        # If the inbox is empty, we can't test parsing but the connection worked.
        if first_message is None:
            print("Inbox is empty, skipping message parsing assertions.")
            return

        # Assert that the parsed message has the correct structure and types
        assert isinstance(first_message.id, str)
        assert len(first_message.id) > 0
        assert isinstance(first_message.subject, str)
        assert isinstance(first_message.body, str)
        assert isinstance(first_message.from_, str)
        assert isinstance(first_message.to, str)
        assert isinstance(first_message.date, str)

        # Verify it's our implementation
        assert isinstance(first_message, GmailMessage)

        # Check that from field contains an email address (if not empty)
        if first_message.from_:
            assert "@" in first_message.from_

        print(f"Successfully parsed message: {first_message.id}")
        print(f"Subject: {first_message.subject[:50]}...")
        print(f"From: {first_message.from_}")

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        pytest.fail(f"Integration test failed during message retrieval/parsing: {e}")


def test_get_specific_message_by_id() -> None:
    """Tests fetching a specific message by ID and parsing it.
    """
    try:
        client = mail_client_api.get_client(interactive=False)

        # First, get a list of messages to get an ID
        messages = list(client.get_messages(max_results=1))

        if not messages:
            pytest.skip("No messages in inbox to test with")

        message_id = messages[0].id

        # Now fetch the same message by ID
        specific_message = client.get_message(message_id)

        # Verify it's the same message
        assert specific_message.id == message_id
        assert isinstance(specific_message, GmailMessage)

        # Properties should be the same
        assert specific_message.subject == messages[0].subject
        assert specific_message.from_ == messages[0].from_
        assert specific_message.to == messages[0].to
        assert specific_message.date == messages[0].date
        assert specific_message.body == messages[0].body

        print(f"Successfully retrieved specific message: {message_id}")

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        pytest.fail(f"Integration test failed during specific message retrieval: {e}")


def test_mark_message_as_read_integration() -> None:
    """Tests marking a message as read using the real Gmail API.
    
    This test is non-destructive but does modify message state.
    """
    try:
        client = mail_client_api.get_client(interactive=False)

        # Get a message to work with
        messages = list(client.get_messages(max_results=1))

        if not messages:
            pytest.skip("No messages in inbox to test with")

        message_id = messages[0].id

        # Try to mark it as read
        result = client.mark_as_read(message_id)

        # Should return True for success
        assert result is True

        print(f"Successfully marked message as read: {message_id}")

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        pytest.fail(f"Integration test failed during mark as read: {e}")


def test_multiple_messages_retrieval() -> None:
    """Tests fetching multiple messages and verifying they're all parsed correctly.
    """
    try:
        client = mail_client_api.get_client(interactive=False)

        # Fetch multiple messages
        messages = list(client.get_messages(max_results=3))

        if not messages:
            pytest.skip("No messages in inbox to test with")

        # Verify all messages are properly parsed
        for i, msg in enumerate(messages):
            assert isinstance(msg, GmailMessage)
            assert isinstance(msg.id, str)
            assert len(msg.id) > 0
            assert isinstance(msg.subject, str)
            assert isinstance(msg.from_, str)
            assert isinstance(msg.to, str)
            assert isinstance(msg.date, str)
            assert isinstance(msg.body, str)

            print(f"Message {i+1}: {msg.id} - {msg.subject[:30]}...")

        # Verify all message IDs are unique
        message_ids = [msg.id for msg in messages]
        assert len(set(message_ids)) == len(message_ids), "Duplicate message IDs found"

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        pytest.fail(f"Integration test failed during multiple message retrieval: {e}")


def test_message_protocol_compliance_with_real_data() -> None:
    """Tests that real Gmail messages comply with the Message protocol.
    """
    try:
        client = mail_client_api.get_client(interactive=False)

        messages = list(client.get_messages(max_results=1))

        if not messages:
            pytest.skip("No messages in inbox to test with")

        msg = messages[0]

        # Test protocol compliance with real data
        required_attributes = ["id", "from_", "to", "subject", "date", "body"]

        for attr in required_attributes:
            assert hasattr(msg, attr), f"Message missing required attribute: {attr}"

            # Get the property value
            value = getattr(msg, attr)

            # All properties should return strings
            assert isinstance(value, str), f"Attribute {attr} should be string, got {type(value)}"

        # Test that properties are not None (though they may be empty strings)
        for attr in required_attributes:
            value = getattr(msg, attr)
            assert value is not None, f"Attribute {attr} should not be None"

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        pytest.fail(f"Integration test failed during protocol compliance check: {e}")


def test_error_handling_with_invalid_message_id() -> None:
    """Tests error handling when trying to fetch a message with invalid ID."""
    try:
        client = mail_client_api.get_client(interactive=False)

        # Try to fetch a message with obviously invalid ID
        invalid_id = "invalid_message_id_12345"

        # This should raise an exception
        with pytest.raises(Exception):
            client.get_message(invalid_id)

        print("Correctly handled invalid message ID")

    except FileNotFoundError:
        pytest.skip("Skipping integration test: credentials.json not found.")
    except Exception as e:
        # If we get here, the test itself failed, not the expected error handling
        pytest.fail(f"Integration test setup failed: {e}")
        raise
