"""Database models for storing user credentials."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional


class UserCredential:
    """Database model for storing user OAuth credentials."""
    
    def __init__(
        self,
        user_id: str,
        access_token: str,
        token_secret: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize UserCredential.
        
        Args:
            user_id: Unique identifier for the user
            access_token: OAuth access token
            token_secret: OAuth token secret
            created_at: When the credential was created
            updated_at: When the credential was last updated
        """
        self.user_id = user_id
        self.access_token = access_token
        self.token_secret = token_secret
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def generate_user_id(cls) -> str:
        """Generate a new unique user ID."""
        return str(uuid.uuid4())


# SQL for creating the credentials table
CREATE_CREDENTIALS_TABLE = """
CREATE TABLE IF NOT EXISTS user_credentials (
    user_id VARCHAR(36) PRIMARY KEY,
    access_token TEXT NOT NULL,
    token_secret TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_credentials_user_id ON user_credentials(user_id);
"""
