# Inbox Client Workspace

## Description

This repository defines a modular, protocol-based interface and implementation for a Gmail client. It utilizes Python's `typing.Protocol` to describe standardized, mockable interfaces for both email messages and the inbox client itself, promoting separation of concerns and testability.

The project follows a workspace structure managed by `uv`, with distinct packages for protocols and their concrete implementations.

### Scope

This inbox client is designed primarily to read, parse, and interact with messages from a Gmail account.

#### Implemented Features

### Core Components

## API Usage Example

```python
import logging
import os
from dotenv import load_dotenv

# Load .env file for local development (contains GMAIL_* variables)
load_dotenv()

# Import the protocol's factory function
# The implementation package overrides this during import
import inbox_client_protocol
from message import Message # Import Message protocol for type hinting

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

try:
    # Get the client instance (will be GmailClient due to override)
    client: inbox_client_protocol.Client = inbox_client_protocol.get_client()
    logger.info("Client initialized.")

    # Get messages
    logger.info("Fetching messages...")
    messages: Iterator[Message] = client.get_messages()
    first_message = next(messages, None) # Get the first message if available

    if first_message:
        logger.info(f"First message - ID: {first_message.id}, Subject: {first_message.subject}")

        # Mark as read
        # logger.info(f"Marking message {first_message.id} as read...")
        # success = client.mark_as_read(first_message.id)
        # logger.info(f"Mark as read status: {success}")

        # Delete (Use with caution!)
        # logger.info(f"Deleting message {first_message.id}...")
        # success = client.delete_message(first_message.id)
        # logger.info(f"Delete status: {success}")

    else:
        logger.info("No messages found in the inbox.")

    # Send a message (Use with caution!)
    # logger.info("Sending test message...")
    # sent = client.send_message("your_email@example.com", "Test from Client", "Hello there!")
    # logger.info(f"Send status: {sent}")

except (FileNotFoundError, RuntimeError, Exception) as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
```

## Requirements

- Python 3.11 or higher  
- `uv` (for dependency and workspace management)  
- Google Cloud Project with Gmail API enabled  
- `credentials.json` downloaded from Google Cloud Console (for initial local auth)  
- See individual component `pyproject.toml` files for specific dependencies.

## Setup Instructions

### Clone

```bash
git clone https://github.com/khamseaffan/Inbox-Client.git # Replace with your repo URL
cd Inbox-Client
```

### Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh # macOS/Linux
# Or use PowerShell command for Windows
```

### Setup Google Credentials

1. Follow Google Cloud instructions to enable the Gmail API and download `credentials.json`.
2. Place `credentials.json` in the project root (`Inbox-Client/`).
3. Run the application once locally (e.g., `uvx python main.py`) to perform the initial OAuth flow and generate `token.json`.
4. Add `credentials.json` and `token.json` to your `.gitignore` file.
5. For easier local development, create a `.env` file (also add to `.gitignore`) and store the `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, and `GMAIL_REFRESH_TOKEN` values (see `main.py` and `inbox_client_impl` for usage).

### Install Dependencies

```bash
# Installs all workspace members and dependencies defined in uv.lock
uv sync --all-packages --extra dev --extra test
source 
```

## Testing

### Run all tests (Unit + Integration)

```bash
# Activate venv first: source .venv/bin/activate
pytest .
# Or use uvx:
uvx pytest .
```

### Run only unit tests

```bash
uvx pytest . -m "not integration"
```

### Run only integration tests (requires local .env or CI context)

```bash
pytest . -m integration
```

### Run with coverage (unit tests only)

```bash
pytest . -m "not integration" --cov=src --cov-report=term-missing
```

## Linting & Formatting

```bash
# Check formatting
ruff format --check .

# Check linting
ruff check .

# Apply fixes (use with caution)
ruff check . --fix
ruff format .
```

## Static Analysis

```bash
mypy src tests
```

## Contributions

Please follow the guidelines in `pull_request_template.md`. Use GitHub issues for tracking.
