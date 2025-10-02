"""Implement a FastAPI-based Gmail client service.

It provides endpoints for:
- Root ("/"): Returns a welcome message for the Mail Client Service.
- Login ("/login"): Authenticates the user's Gmail account using the mail_client_api.
    If already authenticated, it returns a corresponding message. Otherwise, it attempts
    interactive authentication and stores the client in the application state. Handles
    authentication errors gracefully.

Dependencies:
- FastAPI for API framework.
- mail_client_api for Gmail client authentication and management.
- gmail_client_impl for Gmail client implementation (imported for side effects).

Typical usage:
        Run this module to start the Mail Client Service API, then interact with the
        endpoints to authenticate and manage Gmail accounts.
"""
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse

import gmail_client_impl  # noqa: F401
import mail_client_api

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    """Return a welcome message for the Mail Client Service."""
    return {"message": "Welcome to Mail Client Service!"}


@app.get("/login")
def login() -> JSONResponse:
    """Authenticate the user's Gmail account.

    Returns:
        JSONResponse: Success message if authenticated, error details if failed.

    Raises:
        HTTPException: 500 if authentication fails, 409 if already authenticated.

    """
    # Check if already authenticated by checking if client exists in app state
    if hasattr(app.state, "client") and app.state.client is not None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Already authenticated", "status": "success"},
        )

    try:
        # Attempt interactive authentication
        # Prevent multiple simultaneous authentication attempts
        if getattr(app.state, "auth_in_progress", False):
            raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Authentication in progress",
                "message": "Authentication is already in progress. Please wait.",
                "status": "error",
            },
            )
        app.state.auth_in_progress = True
        try:
            client = mail_client_api.get_client(interactive=True)
        finally:
            app.state.auth_in_progress = False

        # Store client in application state
        app.state.client = client

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Authentication successful", "status": "success"},
        )

    except RuntimeError as e:
        # Handle authentication errors (missing credentials, invalid tokens, etc.)
        error_message = str(e)
        if "No valid credentials found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Authentication failed",
                    "message": (
                        "No valid credentials found. Please ensure credentials.json "
                        "exists or environment variables are set."
                    ),
                    "status": "error",
                },
            ) from e
        if "Interactive authentication failed" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Authentication failed",
                    "message": "Interactive authentication failed. Please try again.",
                    "status": "error",
                },
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Authentication error",
                "message": error_message,
                "status": "error",
            },
        ) from e

    except FileNotFoundError as e:
        # Handle missing credentials.json file
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Configuration error",
                "message": "credentials.json file not found. Please ensure it exists in the project root.",
                "status": "error",
            },
        ) from e

    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Unexpected error",
                "message": f"An unexpected error occurred during authentication: {e!s}",
                "status": "error",
            },
        ) from e

@app.get("/messages")
def get_messages(
    max_results: int = Query(3, ge=1, le=100, description="Maximum number of messages to return")
) -> JSONResponse:
    """Get messages from the authenticated Gmail client.
    Args:
        max_results (int): Maximum number of messages to return (default: 3, min: 1, max: 100).
    Returns:
        JSONResponse: List of messages if successful, error details if failed.
    Raises:
        HTTPException: 401 if not authenticated, 500 if message retrieval fails.
    """
    # Check if user is authenticated
    if not hasattr(app.state, "client") or app.state.client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Not authenticated",
                "message": "User is not authenticated. Please log in first.",
                "status": "error",
            },
        )
    
     # Validate max_results query parameter
    if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Invalid query parameter",
                "message": "max_results must be an integer between 1 and 100.",
                "status": "error",
            },
        )
    
    try:
        messages = list(app.state.client.get_messages(max_results=max_results))
        
        # Convert GmailMessage objects to dictionaries for JSON serialization
        serialized_messages = []
        for message in messages:
            serialized_messages.append({
                "id": message.id,
                "from": message.from_,
                "to": message.to,
                "date": message.date,
                "subject": message.subject,
                "body": message.body,
            })

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"messages": serialized_messages, "status": "success"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to fetch messages",
                "message": str(e),
                "status": "error",
            },
        ) from e
    
