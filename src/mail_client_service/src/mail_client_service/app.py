"""FastAPI service for mail client operations."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import gmail_client_impl  # noqa: F401
from fastapi import Depends, FastAPI, Request
from mail_client_api import Client, get_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan and initialize mail client."""
    client = get_client(interactive=True)
    app.state.mail_client = client
    yield


app = FastAPI(
    title="Mail Client Service",
    description="REST API for mail client operations.",
    lifespan=lifespan,
)


# --- Dependency: obtain the mail client ---
def get_mail_client(request: Request) -> Client:
    """Get the already constructed mail client."""
    return request.app.state.mail_client


# --- Define a type alias for reuse (from FastAPI docs) ---
MailClientDep = Annotated[Client, Depends(get_mail_client)]
