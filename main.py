# ta-assignment/main.py

# Import the protocols first
import mail_client_api
import message

# --- TRIGGER DEPENDENCY INJECTION ---
# By importing the implementation packages, their __init__.py files
# run and override the factory functions in the protocol packages.
import gmail_client_impl
import gmail_message_impl

def main() -> None:
    """Initializes the client and demonstrates fetching messages."""
    print("Attempting to initialize Gmail client...")
    try:
        # Now, get_client() returns a GmailClient instance...
        client = mail_client_api.get_client(interactive=True)
        print("\nSuccessfully authenticated and connected to the Gmail API.")

        # ...and when get_messages calls message.get_message(),
        # it will return a GmailMessage instance.
        messages = client.get_messages(max_results=5)
        
        print("\n--- Fetched Messages ---")
        for i, msg in enumerate(messages, 1):
            print(f"\nMessage {i}:")
            print(f"  ID: {msg.id}")
            print(f"  Subject: {msg.subject}")
            print(f"  From: {msg.from_}")
            print(f"  Date: {msg.date}")
            print(f"  Body: {msg.body[:100].replace('/n', ' ')}...")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        raise

if __name__ == "__main__":
    main()