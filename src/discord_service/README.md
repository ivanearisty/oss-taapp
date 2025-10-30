# Discord Client Service

FastAPI-based Discord client service. This README explains how to run the service locally in development.

Quick start (development)

1. From the repository root, activate your virtualenv if you have one:

# Discord Client Service

A small FastAPI service that exposes the concrete `DiscordClient` implementation over HTTP. This mirrors the `mail_client_service` pattern in the repo and provides basic OAuth2 flow plus a few chat endpoints for listing channels, reading messages, sending messages, and (where permitted) deleting messages.

Contents

- `src/discord_service/src/discord_service/main.py` — FastAPI application and endpoints
- `pyproject.toml` — package metadata for editable installs

Highlights

- OAuth2 endpoints: start authorization and handle callback
- Channel and message endpoints: list channels, list messages, send message, fetch message by id (scoped to channel), delete message
- Uses `discord_client_impl.DiscordClient` and `chat_client_api` contracts

Quick start (development)

1. Activate your virtualenv (if you use one):

```bash
source .venv/bin/activate
```

2a — Recommended: install the local packages editable into your venv (from repo root):

```bash
# Install the local workspace packages in editable mode
pip install -e src/chat_client_api -e src/discord_client_impl -e src/discord_service

# Run the service
uvicorn discord_service.main:app --reload --host 127.0.0.1 --port 8001
```

Environment variables

Set these for the OAuth flow (or add to a `.env` file):

- `DISCORD_CLIENT_ID` — Discord application client id
- `DISCORD_CLIENT_SECRET` — Discord application client secret

API endpoints (summary)

- GET `/` — Welcome message
- GET `/login` — Return authorization URL (open in browser to authorize)
- GET `/auth/callback?code=...` — Exchange code for access token and store authenticated client in memory
- GET `/logout` — Clear stored client
- GET `/user` — Get current authenticated user's data
- GET `/channels` — List DM/group DM channels
- GET `/channels/{channel_id}/messages?limit=50` — List recent messages in a channel (limit 1-100)
- POST `/channels/{channel_id}/messages?content=...` — Send a message to a channel
- GET `/messages/{message_id}?channel_id=...` — Find a message by id in a channel (scans recent messages)
- DELETE `/channels/{channel_id}/messages/{message_id}` — Delete a message (permissions required)

Notes about behavior and limitations

- The service stores the authenticated client on the FastAPI `app.state` for the running process. This is fine for local testing but not production-ready for multi-worker deployments.
- Discord's API and token types govern what you can do: deleting messages or reading certain channels may require the correct OAuth scopes or bot permissions.
- `GET /messages/{id}` requires `channel_id` because this implementation does not provide a single-message GET; it scans recent messages in the specified channel.

Example flows

- Get authorization URL:

```bash
curl "http://127.0.0.1:8001/login"
```

- After authorizing, Discord will redirect to your `DISCORD_REDIRECT_URI` (which should map to `/auth/callback` in this service). The callback exchanges the code and the service returns the access token in the response body and sets a secure-ish cookie for subsequent requests.

- List channels (after auth):

```bash
curl http://127.0.0.1:8001/channels
```

Testing

- You can write a small integration test using FastAPI's TestClient that imports `discord_service.main:app` and asserts `GET /` returns 200. This test won't hit Discord.
