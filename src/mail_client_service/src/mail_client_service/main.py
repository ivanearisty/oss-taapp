"""FastAPI application for the Mail Client Service."""
from contextlib import asynccontextmanager
from typing import Iterator, Annotated
from fastapi import FastAPI, Depends, HTTPException

# --- TRIGGER DEPENDENCY INJECTION ---
# By importing the implementation packages, their init.py files
# run and override the factory functions in the protocol packages.
import gmail_client_impl
import gmail_message_impl
# ---
# Import the abstract interfaces and the service's schemas
import mail_client_api
from .schemas import MessageSchema, StatusResponse

# Global variable to hold the mail client instance
mail_client: mail_client_api.Client | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifespan."""
    global mail_client
    print("Starting up the service and initializing the mail client...")
    # Initialize the client using the factory. It's a GmailClient because of DI.
    mail_client = mail_client_api.get_client(interactive=False)
    yield
    print("Shutting down the service.")

app = FastAPI(
    title="Mail Client Service",
    description="An API for interacting with a mail client.",
    version="1.0.0",
    lifespan=lifespan,
)

def get_client() -> mail_client_api.Client:
    """Dependency function to get the initialized mail client."""
    if mail_client is None:
        # This should not happen if the lifespan event handler is working correctly
        raise HTTPException(status_code=503, detail="Mail client is not available")
    return mail_client

ClientDependency = Annotated[mail_client_api.Client, Depends(get_client)]

@app.get("/messages", response_model=list[MessageSchema])
def get_messages_list(client: ClientDependency, limit: int = 10):
    """Retrieve a list of recent messages from the inbox."""
    try:
        messages_iterator = client.get_messages(max_results=limit)
        return list(messages_iterator)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/messages/{message_id}", response_model=MessageSchema)
def get_message_detail(message_id: str, client: ClientDependency):
    """Retrieve the full details for a specific message by its ID."""
    try:
        message = client.get_message(message_id)
        return message
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Message not found or error occurred: {e}")

@app.post("/messages/{message_id}/read", response_model=StatusResponse)
def mark_message_as_read(message_id: str, client: ClientDependency):
    """Mark a message as read."""
    if client.mark_as_read(message_id):
        return {"status": "success", "message": f"Message {message_id} marked as read."}
    raise HTTPException(status_code=500, detail="Failed to mark message as read.")

@app.delete("/messages/{message_id}", response_model=StatusResponse)
def delete_single_message(message_id: str, client: ClientDependency):
    """Delete a message by its ID."""
    if client.delete_message(message_id):
        return {"status": "success", "message": f"Message {message_id} deleted."}
    raise HTTPException(status_code=500, detail="Failed to delete message.")