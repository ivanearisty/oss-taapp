"""Compatibility wrapper for the mail_client_service FastAPI app.

This repository embeds the actual package code under ``src/mail_client_service/src``.
The tests (and other callers) expect ``mail_client_service`` to expose the FastAPI
``app`` instance and its dependencies directly, so we re-export them here.
"""

from .src.mail_client_service.app import app, get_mail_client

__all__ = ["app", "get_mail_client"]
