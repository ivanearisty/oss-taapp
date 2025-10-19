"""Example usage of the ServiceClientAdapter."""

from mail_client_adapter import create_service_adapter


def main() -> None:
    """Demonstrate how to use the ServiceClientAdapter."""
    # Create the adapter using the factory function
    # In a real application, you would get these values from configuration
    adapter = create_service_adapter(
        base_url="http://localhost:8000",  # Replace with your service URL
    )

    try:
        # List messages

        print("Testing GET /messages")  # noqa: T201
        messages = list(adapter.get_messages(max_results=5))
        print(f"\tLength messages = {len(messages)}")  # noqa: T201
        for _message in messages:
            print("\tMessage:", _message.subject)  # noqa: T201

        # If we have messages, demonstrate other operations
        if messages:
            first_message = messages[0]
            message_id = first_message.id

            # Get a specific message
            print(f"Testing GET /messages/{message_id}")  # noqa: T201
            message = adapter.get_message(message_id)
            print("\tMessage:", message.subject)  # noqa: T201

            # Mark as read
            print(f"Testing PUT /messages/{message_id}/mark-as-read")  # noqa: T201
            success = adapter.mark_as_read(message_id)
            print("\tMark as read:", success)  # noqa: T201

            # Delete the message
            print(f"Testing DELETE /messages/{message_id}")  # noqa: T201
            confirmation = input("Y/N  to continue: ")
            if confirmation.lower() == "y":

                print(f"\tbefore: length messages = {len(messages)}")  # noqa: T201

                success = adapter.delete_message(message_id)

                print(f"\tDelete: {success}")  # noqa: T201

                print(  # noqa: T201
                    f"\tafter: length messages = {len(list(adapter.get_messages(max_results=5)))}",
                )
            else:
                print("\tSkipping delete")  # noqa: T201

    except RuntimeError as e:
        print(f"Service operation failed: {e}")  # noqa: T201
        print(  # noqa: T201
            "   This could be due to authentication issues or service errors.",
        )
    except (ConnectionError, OSError) as e:
        print(f"Connection failed: {e}")  # noqa: T201
        print(  # noqa: T201
            "   Please check that the mail service is running at http://localhost:8000",
        )
    except Exception as e:  # noqa: BLE001
        print(f"Unexpected error: {e}")  # noqa: T201
        print(f"Error type: {type(e).__name__}")  # noqa: T201
        print("Please check your configuration and try again.")  # noqa: T201


if __name__ == "__main__":
    main()
