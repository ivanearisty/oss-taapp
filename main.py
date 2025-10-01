"""Main module for demonstrating the mail client."""

# ta-assignment/main.py

import contextlib
import logging

import gmail_client_impl  # noqa: F401
import mail_client_api

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Initialize the client and demonstrate all mail client methods."""
    # Now, get_client() returns a GmailClient instance...
    client = mail_client_api.get_client(interactive=False)

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
            pass

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
        try:
            confirmation = input("Type 'DELETE' to confirm deletion: ")
            if confirmation == "DELETE":
                success = client.delete_message(delete_message_id)
                if success:
                    print(f"Message {delete_message_id} deleted successfully.")
                else:
                    print(f"Failed to delete message {delete_message_id}.")
        except EOFError:
            # This means that CircleCI or another non-interactive environment is not going to actually delete anything
            print("Skipping deletion in non-interactive mode")
    else:
        print("Not enough messages to test deletion")

    print("Demo complete")


if __name__ == "__main__":
    main()
