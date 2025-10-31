"""Data models for Trello entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True)
class TrelloBoard:
    """Represents a Trello board."""

    id: str
    name: str
    description: str | None = None
    closed: bool = False
    url: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class TrelloList:
    """Represents a Trello list within a board."""

    id: str
    name: str
    board_id: str
    position: float
    closed: bool = False


@dataclass(frozen=True)
class TrelloCard:
    """Represents a Trello card within a list."""

    id: str
    name: str
    list_id: str
    board_id: str
    description: str | None = None
    position: float = 0.0
    closed: bool = False
    due_date: datetime | None = None
    url: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class TrelloUser:
    """Represents a Trello user."""

    id: str
    username: str
    full_name: str | None = None
    email: str | None = None
