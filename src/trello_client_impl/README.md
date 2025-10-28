# Trello Client Implementation

This package provides a concrete implementation of the Trello client API that wraps the Trello REST API.

## Features

- Full OAuth 2.0 authentication flow
- Secure credential storage in PostgreSQL
- Async/await support
- Comprehensive error handling
- Type-safe operations

## Authentication

The implementation uses OAuth 2.0 with Trello's API. Users are redirected to Trello for authentication, and tokens are securely stored in the database.

## Usage

```python
from trello_client_impl import TrelloClientImpl

# Create client with database connection
client = TrelloClientImpl(db_url="postgresql://...")

# Use the client (OAuth flow handled automatically)
boards = await client.get_boards()
```

## Environment Variables

- `TRELLO_API_KEY`: Your Trello API key
- `TRELLO_API_SECRET`: Your Trello API secret  
- `DATABASE_URL`: PostgreSQL connection string
- `REDIRECT_URI`: OAuth callback URL
