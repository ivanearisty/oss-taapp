import mail_client_api
import gmail_client_impl  # This import triggers the dependency injection

def main() -> None:
    """Initializes the client, triggering the auth flow if needed."""
    print("Attempting to initialize Gmail client...")
    try:
        client = mail_client_api.get_client(interactive=True)
        client.get_messages()
        print("\nSuccessfully created token.json and connected to the Gmail API.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()