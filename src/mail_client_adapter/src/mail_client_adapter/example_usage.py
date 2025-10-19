"""Example usage of the ServiceClientAdapter."""

from mail_client_adapter import create_service_adapter


def main() -> None:
    """Demonstrate how to use the ServiceClientAdapter."""
    # Create the adapter using the factory function
    # In a real application, you would get these values from configuration
    adapter = create_service_adapter(
        base_url="http://localhost:8000",  # Replace with your service URL
        token="your-auth-token-here",  # noqa: S106  # Replace with your actual token
    )

    try:
        # List messages
        messages = list(adapter.get_messages(max_results=5))

        for _message in messages:
            pass

        # If we have messages, demonstrate other operations
        if messages:
            first_message = messages[0]
            message_id = first_message.id

            # Get a specific message
            adapter.get_message(message_id)

            # Mark as read
            adapter.mark_as_read(message_id)

    except RuntimeError as e:
        print(f"Service operation failed: {e}") # noqa: T201
        print("   This could be due to authentication issues or service errors.")  # noqa: T201
    except (ConnectionError, OSError) as e:
        print(f"Connection failed: {e}") # noqa: T201
        print("   Please check that the mail service is running at http://localhost:8000") # noqa: T201
    except Exception as e: # noqa: BLE001
        print(f"Unexpected error: {e}") # noqa: T201
        print(f"Error type: {type(e).__name__}") # noqa: T201
        print("Please check your configuration and try again.") # noqa: T201


if __name__ == "__main__":
    main()
