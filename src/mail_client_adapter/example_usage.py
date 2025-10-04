"""Example usage of the ServiceClientAdapter."""

from mail_client_adapter import create_service_adapter


def main():
    """Demonstrate how to use the ServiceClientAdapter."""
    # Create the adapter using the factory function
    # In a real application, you would get these values from configuration
    adapter = create_service_adapter(
        base_url="http://localhost:8000",  # Replace with your service URL
        token="your-auth-token-here"       # Replace with your actual token
    )
    
    try:
        # List messages
        print("Fetching messages...")
        messages = list(adapter.get_messages(max_results=5))
        
        print(f"Found {len(messages)} messages:")
        for message in messages:
            print(f"- ID: {message.id}")
            print(f"  From: {message.from_}")
            print(f"  Subject: {message.subject}")
            print(f"  Date: {message.date}")
            print()
        
        # If we have messages, demonstrate other operations
        if messages:
            first_message = messages[0]
            message_id = first_message.id
            
            # Get a specific message
            print(f"Getting message {message_id}...")
            specific_message = adapter.get_message(message_id)
            print(f"Message body: {specific_message.body[:100]}...")
            
            # Mark as read
            print(f"Marking message {message_id} as read...")
            success = adapter.mark_as_read(message_id)
            print(f"Mark as read successful: {success}")
            
            # Delete message (uncomment if you want to test deletion)
            # print(f"Deleting message {message_id}...")
            # success = adapter.delete_message(message_id)
            # print(f"Delete successful: {success}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()