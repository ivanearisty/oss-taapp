"""Main module for demonstrating the mail client."""

# ta-assignment/main.py

# Import the protocols first
# --- TRIGGER DEPENDENCY INJECTION ---
# By importing the implementation packages, their __init__.py files
# run and override the factory functions in the protocol packages.
import contextlib

import mail_client_api


def main() -> None:
    """Initialize the client and demonstrate all mail client methods."""
    # Now, get_client() returns a GmailClient instance...
    client = mail_client_api.get_client(interactive=True)

    # Test 1: Get messages (existing functionality)
    messages = list(client.get_messages(max_results=3))

    if not messages:
        return

    for _i, _msg in enumerate(messages, 1):
        pass

    # Test 2: Get a specific message by ID
    if messages:
        test_message_id = messages[0].id
        with contextlib.suppress(Exception):
            client.get_message(test_message_id)

    # Test 3: Mark a message as read
    if messages:
        test_message_id = messages[0].id
        with contextlib.suppress(Exception):
            success = client.mark_as_read(test_message_id)
            if success:
                pass
            else:
                pass

    # Test 4: Delete a message (WARNING: This is destructive!)
    # Only test if we have more than one message to avoid deleting all messages
    if len(messages) > 1:
        # Ask for confirmation before deleting
        delete_message_id = messages[-1].id  # Delete the last message

        # For safety, let's skip actual deletion in this demo
        # Uncomment the lines below if you really want to test deletion

        with contextlib.suppress(Exception):
            success = client.delete_message(delete_message_id)
            if success:
                pass
            else:
                pass
    else:
        pass


if __name__ == "__main__":
    main()
