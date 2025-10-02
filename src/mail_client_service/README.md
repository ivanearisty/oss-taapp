## Mail Client Service (FastAPI)

A minimal FastAPI service that wires up the workspace `mail-client-api` with the `gmail-client-impl`. It initializes the client on startup to ensure the Gmail implementation registers correctly.

There are no HTTP routes yet; you can still start the server and visit the automatic docs page.

### Prerequisites
- **Python 3.11+**
- One of:
  - **uv** (recommended)
  - Or plain **pip** in a virtual environment

Note: This repository already contains a `token.json` at the repo root used by the Gmail implementation for non-interactive startup.

### Run with uv (recommended)
1. Install dependencies for this package (and link workspace members):
   ```bash
   uv sync --all-packages --extra dev
   ```
   
### Notes
- The application imports `gmail_client_impl` and calls `mail_client_api.get_client(interactive=False)` during FastAPI startup to validate registration and basic initialization.
- If Gmail credentials are not present/valid, startup may log an error in environments without `token.json`. In this repo, a `token.json` exists at the root.


