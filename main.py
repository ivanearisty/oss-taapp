import mail_client_api


def main() -> None:
    """Initialize client, trigger the auth flow if needed."""
    print("Attempting to initialize Gmail client...")
    try:
        client = mail_client_api.get_client(interactive=True)
        client.get_messages()
        print("\nSuccessfully created token.json and connected to the Gmail API.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
