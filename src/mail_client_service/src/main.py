import gmail_client_impl  # Import to register the implementation
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from mail_client_api import get_client
from message import Message

from .models import (
    ErrorResponse,
    MessageDetail,
    MessageListResponse,
    MessageSummary,
    SuccessResponse,
)

app = FastAPI(
    title="Mail Client Service",
    description="RESTful API for email operations using Gmail client",
    version="1.0.0",
)


def get_mail_client():
    """Dependency to get mail client instance."""
    return get_client(interactive=False)


@app.get(
    "/messages",
    response_model=MessageListResponse,
    summary="Get message summaries",
    description="Fetch a list of message summaries from the inbox",
)
async def get_messages(
    max_results: int = Query(default=10, ge=1, le=100, description="Maximum number of messages to return"),
    client=Depends(get_mail_client),
):
    """Fetch a list of message summaries."""
    try:
        messages = list(client.get_messages(max_results=max_results))
        message_summaries = [
            MessageSummary(
                id=msg.id,
                from_=msg.from_,
                to=msg.to,
                date=msg.date,
                subject=msg.subject,
            )
            for msg in messages
        ]
        
        return MessageListResponse(
            messages=message_summaries,
            count=len(message_summaries),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages: {str(e)}"
        )


@app.get(
    "/messages/{message_id}",
    response_model=MessageDetail,
    summary="Get message details",
    description="Fetch full details of a specific message including body content",
)
async def get_message(
    message_id: str,
    client=Depends(get_mail_client),
):
    """Fetch full details of a specific message."""
    try:
        message = client.get_message(message_id)
        return MessageDetail(
            id=message.id,
            from_=message.from_,
            to=message.to,
            date=message.date,
            subject=message.subject,
            body=message.body,
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Message not found or failed to fetch: {str(e)}"
        )


@app.post(
    "/messages/{message_id}/mark-as-read",
    response_model=SuccessResponse,
    summary="Mark message as read",
    description="Mark a specific message as read",
)
async def mark_message_as_read(
    message_id: str,
    client=Depends(get_mail_client),
):
    
    try:
        success = client.mark_as_read(message_id)
        if success:
            return SuccessResponse(
                success=True,
                message=f"Message {message_id} marked as read successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to mark message {message_id} as read"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark message as read: {str(e)}"
        )


@app.delete(
    "/messages/{message_id}",
    response_model=SuccessResponse,
    summary="Delete message",
    description="Delete a specific message",
)
async def delete_message(
    message_id: str,
    client=Depends(get_mail_client),
):
    """Delete a message."""
    try:
        success = client.delete_message(message_id)
        if success:
            return SuccessResponse(
                success=True,
                message=f"Message {message_id} deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete message {message_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete message: {str(e)}"
        )



# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )
