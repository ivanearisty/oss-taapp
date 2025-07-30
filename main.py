import mail_client_api
import gmail_client_impl # This import is necessary to ensure the dependency injection works correctly.

def main() -> None:
    """Initialize client, trigger the auth flow if needed."""
    print("Attempting to initialize Gmail client...")
    try:
        client = mail_client_api.get_client(interactive=True)
        print("\nSuccessfully created token.json and connected to the Gmail API.")
        messages = client.get_messages(max_results=5)
        for i, message in enumerate(messages, 1):
            print(f"\nMessage {i}:")
            print(f"Subject: {message.subject}")
            print(f"From: {message.from_}")
            print(f"Date: {message.date}")
            print(f"Body: {message.body[:100]}...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
