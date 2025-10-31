"""Demo script for the Jira ticket service with OAuth 2.0 authentication.

This script demonstrates:
1. OAuth 2.0 authentication with Atlassian
2. Token storage and retrieval
3. All ticket service operations (CRUD operations on tickets)
"""

import asyncio
import logging
import sys
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
# Suppress verbose httpx and httpcore debug logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


async def start_callback_server(port: int = 8000) -> str:
    """Start a local HTTP server to capture OAuth callback.

    Returns:
        The authorization code from the callback
    """
    auth_code_holder: dict[str, str] = {}
    done_event = asyncio.Event()

    async def handle_callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle the OAuth callback request."""
        code_received = False
        try:
            # Read the request line
            request_line = await reader.readline()
            request_str = request_line.decode().strip()
            logger.debug(f"Received request: {request_str}")

            # Skip headers until empty line
            while True:
                line = await reader.readline()
                if line == b"\r\n" or line == b"\n" or not line:
                    break

            # Extract the authorization code from the query string
            if "GET" in request_str and "/auth/callback" in request_str:
                path = request_str.split()[1]
                parsed = urlparse(path)
                query_params = parse_qs(parsed.query)
                logger.debug(f"Query params: {query_params}")

                if "code" in query_params:
                    auth_code_holder["code"] = query_params["code"][0]
                    code_received = True
                    logger.info(
                        f"Received authorization code: {auth_code_holder['code'][:20]}...",
                    )
                    response_body = (
                        "<html><head><script>"
                        "setTimeout(function() { window.close(); }, 2000);"
                        "</script></head>"
                        "<body><h1 style='text-align:center'>Authorization Successful!</h1>"
                        "<p style='text-align:center'>You can close this window now.</p>"
                        "</body></html>"
                    )
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "Connection: close\r\n\r\n"
                        + response_body
                    )
                elif "error" in query_params:
                    error = query_params.get("error", ["unknown"])[0]
                    logger.error(f"OAuth error: {error}")
                    response_body = (
                        "<html><body><h1>Authorization Failed</h1>"
                        f"<p>Error: {error}</p>"
                        "</body></html>"
                    )
                    response = (
                        "HTTP/1.1 400 Bad Request\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "Connection: close\r\n\r\n"
                        + response_body
                    )
                else:
                    response_body = (
                        "<html><body><h1>Authorization Failed</h1>"
                        "<p>No authorization code received.</p>"
                        "</body></html>"
                    )
                    response = (
                        "HTTP/1.1 400 Bad Request\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(response_body)}\r\n"
                        "Connection: close\r\n\r\n"
                        + response_body
                    )
            else:
                response_body = (
                    "<html><body><h1>Wrong Path</h1>"
                    "<p>Expected callback at /auth/callback</p>"
                    "</body></html>"
                )
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(response_body)}\r\n"
                    "Connection: close\r\n\r\n"
                    + response_body
                )

            writer.write(response.encode())
            await writer.drain()
            writer.close()

            # Always signal completion when we get a request
            done_event.set()

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            done_event.set()

    try:
        server = await asyncio.start_server(handle_callback, "localhost", port)
    except OSError:
        logger.warning(f"Port {port} already in use, trying {port + 1}")
        server = await asyncio.start_server(handle_callback, "localhost", port + 1)
        port = port + 1

    logger.info(f"Started callback server on http://localhost:{port}")

    async with server:
        await done_event.wait()

    return auth_code_holder.get("code", "")


async def authenticate_with_atlassian() -> None:
    """Handle OAuth 2.0 authentication with Atlassian.

    Steps:
    1. Check for existing valid tokens
    2. Start local HTTP server for callback
    3. Open browser to authorization URL
    4. Exchange authorization code for tokens
    5. Store tokens securely in SQLite database
    """
    logger.info("Starting Atlassian OAuth 2.0 authentication flow...")

    try:
        from ticket_impl.oauth import (
            build_authorize_url,
            exchange_code_for_tokens,
        )
        from ticket_impl.storage import get_tokens

        # Check if we already have valid tokens
        from ticket_impl.storage import is_expired
        stored_tokens = get_tokens("demo_user")
        if stored_tokens and not is_expired(stored_tokens):
            logger.info("Using existing valid tokens")
            return

        # Step 1: Start callback server
        logger.info("\n--- Step 1: Starting OAuth callback server ---")
        callback_task = asyncio.create_task(start_callback_server(8000))

        # Step 2: Generate authorization URL and open browser
        logger.info("--- Step 2: Opening authorization URL in browser ---")
        auth_url = build_authorize_url("demo_state")
        logger.info(f"Authorization URL: {auth_url}")
        logger.info("Opening browser for authorization...")

        # Open the browser
        webbrowser.open(auth_url)

        try:
            # Wait for callback (with 5 minute timeout)
            auth_code = await asyncio.wait_for(
                callback_task,
                timeout=300.0,
            )

            if not auth_code:
                logger.error("Authorization failed: no code received")
                return

            # Step 3: Exchange code for tokens
            logger.info("\n--- Step 3: Exchanging code for access tokens ---")
            access_token, refresh_token, expires_in = await exchange_code_for_tokens(
                "demo_user",
                auth_code,
            )

            if access_token:
                logger.info("Successfully obtained and stored access tokens")
                logger.info("Access token stored for user: demo_user")
                logger.info(f"Token expires in: {expires_in} seconds")

                # Extract cloud ID from Atlassian API
                logger.info("\n--- Step 4: Fetching Jira Cloud ID from Atlassian API ---")
                from ticket_impl.oauth import fetch_cloud_id_from_api

                cloud_id = await fetch_cloud_id_from_api(access_token)
                if cloud_id:
                    logger.info(f"Fetched Jira Cloud ID: {cloud_id}")
                    logger.info("Update your .env file with:")
                    logger.info(f'  JIRA_CLOUD_ID="{cloud_id}"')

                    # Optionally update .env file automatically
                    import os

                    env_path = os.path.join(os.path.dirname(__file__), ".env")
                    if os.path.exists(env_path):
                        with open(env_path, "r") as f:
                            env_content = f.read()

                        # Replace or add JIRA_CLOUD_ID
                        import re

                        pattern = r'JIRA_CLOUD_ID="[^"]*"'
                        if re.search(pattern, env_content):
                            env_content = re.sub(
                                pattern,
                                f'JIRA_CLOUD_ID="{cloud_id}"',
                                env_content,
                            )
                        else:
                            env_content += f'\nJIRA_CLOUD_ID="{cloud_id}"'

                        with open(env_path, "w") as f:
                            f.write(env_content)
                        logger.info("Updated .env file with JIRA_CLOUD_ID")

                    # Step 5: Fetch and save project key
                    logger.info("\n--- Step 5: Fetching Jira Project Key ---")
                    from ticket_impl.oauth import fetch_project_key_from_api

                    project_key = await fetch_project_key_from_api(access_token, cloud_id)
                    if project_key:
                        logger.info(f"Found project key: {project_key}")

                        # Update .env with project key
                        env_path = os.path.join(os.path.dirname(__file__), ".env")
                        if os.path.exists(env_path):
                            with open(env_path, "r") as f:
                                env_content = f.read()

                            # Replace or add JIRA_PROJECT_KEY
                            pattern = r'JIRA_PROJECT_KEY="[^"]*"'
                            if re.search(pattern, env_content):
                                env_content = re.sub(
                                    pattern,
                                    f'JIRA_PROJECT_KEY="{project_key}"',
                                    env_content,
                                )
                            else:
                                env_content += f'\nJIRA_PROJECT_KEY="{project_key}"'

                            with open(env_path, "w") as f:
                                f.write(env_content)
                            logger.info("Updated .env file with JIRA_PROJECT_KEY")
                    else:
                        logger.warning(
                            "\nCould not fetch project key automatically."
                        )
                        logger.info("To complete setup:")
                        logger.info("  1. Go to your Jira Cloud instance")
                        logger.info("  2. Click on 'Projects' in the sidebar")
                        logger.info("  3. Find your project and copy its KEY (e.g., 'PROJ')")
                        logger.info('  4. Update .env: JIRA_PROJECT_KEY="PROJ"')
                        logger.info("  5. Run this script again")
                else:
                    logger.warning(
                        "Could not fetch cloud ID from Atlassian API. "
                        "You may need to manually set JIRA_CLOUD_ID in .env"
                    )
            else:
                logger.error("Failed to exchange code for tokens")
                return

        except asyncio.TimeoutError:
            logger.error("Authorization timeout: no callback received within 5 minutes")
            return
        except EOFError:
            logger.warning("Non-interactive environment - skipping OAuth setup")
            logger.info("Ensure your .env file contains:")
            logger.info("  - OAUTH_CLIENT_ID")
            logger.info("  - OAUTH_CLIENT_SECRET")
            logger.info("  - OAUTH_REDIRECT_URI")
            logger.info("  - JIRA_CLOUD_ID")

    except ImportError as e:
        logger.exception("Cannot import ticket_impl modules: %s", e)
        logger.info("Please ensure ticket_impl package is properly implemented")


async def demo_ticket_operations() -> None:
    """Demonstrate all ticket service operations.

    Operations demonstrated:
    1. Create a new ticket
    2. Retrieve a ticket by ID
    3. List tickets
    4. Update ticket status and priority
    5. Add comments to a ticket
    6. Retrieve comments
    7. Delete a ticket (with confirmation)
    """
    import os

    # Check if project key is configured
    project_key = os.getenv("JIRA_PROJECT_KEY", "").strip()
    if not project_key or project_key == "your-project-key-here":
        logger.info("\n--- Skipping Ticket Demo ---")
        logger.info("Project key not configured yet.")
        logger.info("Once you've set JIRA_PROJECT_KEY in .env, run this script again to see the full demo!")
        return

    logger.info("\n--- Initializing Jira Ticket Service ---")

    try:
        from ticket_api.models import TicketPriority, TicketStatus
        from ticket_impl.impl import TicketImpl
        from ticket_impl.storage import get_tokens, is_expired

        # Verify we have tokens
        tokens = get_tokens("demo_user")
        if not tokens or is_expired(tokens):
            logger.error("No valid tokens found. Please authenticate first.")
            return

        # Initialize the ticket service implementation
        ticket_service = TicketImpl(user_id="demo_user", project_key=project_key)
        logger.info("Ticket service initialized successfully")
        logger.info(f"  Using project key: {project_key}")

        # Demo 1: Create a ticket
        logger.info("\n--- Demo 1: Creating a new ticket ---")
        try:
            new_ticket = await ticket_service.create_ticket(
                title="Demo Ticket: Feature Implementation",
                description="This is a demo ticket created by the script",
                reporter="demo_user",
                priority=TicketPriority.MEDIUM,
                assignee=None,
            )
            logger.info(f"Created ticket: {new_ticket.id}")
            logger.info(f"  Title: {new_ticket.title}")
            logger.info(f"  Priority: {new_ticket.priority}")
            demo_ticket_id = new_ticket.id
        except Exception as e:  # noqa: BLE001
            logger.exception("Failed to create ticket")
            return

        # Demo 2: Retrieve the ticket
        logger.info("\n--- Demo 2: Retrieving the created ticket ---")
        try:
            retrieved_ticket = await ticket_service.get_ticket(demo_ticket_id)
            logger.info(f"Retrieved ticket: {retrieved_ticket.id}")
            logger.info(f"  Title: {retrieved_ticket.title}")
            logger.info(f"  Status: {retrieved_ticket.status}")
            logger.info(f"  Priority: {retrieved_ticket.priority}")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to retrieve ticket")

        # Demo 3: List tickets
        logger.info("\n--- Demo 3: Listing recent tickets ---")
        try:
            tickets = await ticket_service.list_tickets(limit=5)
            logger.info(f"Retrieved {len(tickets)} tickets:")
            for idx, ticket in enumerate(tickets, 1):
                logger.info(
                    f"  {idx}. {ticket.title} (ID: {ticket.id}, "
                    f"Status: {ticket.status})",
                )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to list tickets")

        # Demo 4: Update ticket
        logger.info("\n--- Demo 4: Updating ticket status ---")
        try:
            updated_ticket = await ticket_service.update_ticket(
                ticket_id=demo_ticket_id,
                status=TicketStatus.IN_PROGRESS,
                priority=TicketPriority.HIGH,
            )
            logger.info(f"Updated ticket: {updated_ticket.id}")
            logger.info(f"  New Status: {updated_ticket.status}")
            logger.info(f"  New Priority: {updated_ticket.priority}")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to update ticket")

        # Demo 5: Add a comment
        logger.info("\n--- Demo 5: Adding a comment to the ticket ---")
        try:
            comment = await ticket_service.add_comment(
                ticket_id=demo_ticket_id,
                author="demo_user",
                content="Demo comment added by script. Great progress!",
            )
            if comment:
                logger.info(f"Comment added to ticket {demo_ticket_id}")
                logger.info(f"  Comment: {comment.content}")
            else:
                logger.warning("Comment was not created")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to add comment")

        # Demo 6: Get comments
        logger.info("\n--- Demo 6: Retrieving ticket comments ---")
        try:
            comments = await ticket_service.get_ticket_comments(demo_ticket_id)
            logger.info(f"Retrieved {len(comments)} comments:")
            for idx, comment in enumerate(comments, 1):
                logger.info(f"  {idx}. {comment.content}")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to retrieve comments")

        # Demo 7: Delete the ticket (optional - requires confirmation)
        logger.info("\n--- Demo 7: Ticket deletion ---")
        try:
            confirmation = input(
                "Delete the demo ticket? (type 'DELETE' to confirm): ",
            ).strip()
            if confirmation == "DELETE":
                success = await ticket_service.delete_ticket(demo_ticket_id)
                if success:
                    logger.info(f"Ticket {demo_ticket_id} successfully deleted")
                else:
                    logger.warning(f"Failed to delete ticket {demo_ticket_id}")
            else:
                logger.info("Deletion cancelled")
        except EOFError:
            logger.info("Non-interactive environment - skipping deletion demo")

    except ImportError as e:
        logger.exception("Cannot import ticket service modules: %s", e)
        logger.info("Please ensure the following packages are implemented:")
        logger.info("  - ticket_impl")
        logger.info("  - ticket_api")


async def main() -> None:
    """Run the Jira ticket service demo.

    This is the main entry point that orchestrates the full demo workflow.
    """
    logger.info("Jira Ticket Service Demo Script")

    # Step 1: Authenticate with Atlassian
    await authenticate_with_atlassian()

    # Step 2: Demonstrate ticket operations
    await demo_ticket_operations()


if __name__ == "__main__":
    asyncio.run(main())
