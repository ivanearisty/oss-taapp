"""Example main demonstrating integration with other teams' implementations."""

from __future__ import annotations

import asyncio
import logging
import os

from chat_ticket_integration import ChatTicketIntegration
from chat_ticket_integration.integration import ChatAPI, TicketAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MailClientAdapter(ChatAPI):
    """Adapter wrapping mail client as chat API."""

    def __init__(self, mail_client) -> None:
        """Initialize with mail client."""
        self.mail_client = mail_client

    def get_messages(self, channel_id: str, max_results: int = 10) -> list:
        """Get messages from mail client."""
        try:
            return list(self.mail_client.get_messages(max_results=max_results))
        except Exception:
            logger.exception("Error getting messages")
            return []


class KanbanClientAdapter(TicketAPI):
    """Adapter wrapping kanban client as ticket API."""

    def __init__(self, kanban_client) -> None:
        """Initialize with kanban client."""
        self.kanban_client = kanban_client

    async def create_card(self, list_id: str, name: str, description: str | None = None):
        """Create a card."""
        return await self.kanban_client.create_card(list_id, name, description)

    async def get_card(self, card_id: str):
        """Get a card."""
        return await self.kanban_client.get_card(card_id)

    async def update_card(
        self,
        card_id: str,
        name: str | None = None,
        description: str | None = None,
        list_id: str | None = None,
    ):
        """Update a card."""
        return await self.kanban_client.update_card(card_id, name=name, description=description, list_id=list_id)

    async def delete_card(self, card_id: str) -> bool:
        """Delete a card."""
        return await self.kanban_client.delete_card(card_id)

    async def get_cards(self, list_id: str) -> list:
        """Get cards in a list."""
        return await self.kanban_client.get_cards(list_id)

    async def get_lists(self, board_id: str) -> list:
        """Get lists in a board."""
        return await self.kanban_client.get_lists(board_id)


async def main() -> None:
    """Run the integration with other teams' implementations."""
    # Configuration
    channel_id = os.getenv("CHAT_CHANNEL_ID", "inbox")
    board_id = os.getenv("TICKET_BOARD_ID", "default-board")
    poll_interval = float(os.getenv("POLL_INTERVAL", "1.0"))

    logger.info("Starting chat-ticket integration")
    logger.info("Channel ID: %s", channel_id)
    logger.info("Board ID: %s", board_id)
    logger.info("Poll interval: %s seconds", poll_interval)

    # Import other teams' implementations
    # Example: Using Ivan's vertical (uncomment when dependencies are installed)
    # from mail_client_api import get_client as get_mail_client
    # from kanban_client_api import get_client as get_kanban_client
    #
    # mail_client = get_mail_client(interactive=False)
    # kanban_client = get_kanban_client()
    #
    # chat_api = MailClientAdapter(mail_client)
    # ticket_api = KanbanClientAdapter(kanban_client)
    #
    # integration = ChatTicketIntegration(
    #     chat_api=chat_api,
    #     ticket_api=ticket_api,
    #     channel_id=channel_id,
    #     board_id=board_id,
    #     poll_interval=poll_interval,
    # )
    #
    # try:
    #     await integration.start()
    # except KeyboardInterrupt:
    #     integration.stop()
    #     logger.info("Integration stopped")

    logger.info("To use with other teams' implementations:")
    logger.info("1. Clone their repository separately")
    logger.info("2. Install it: uv pip install -e /path/to/their/repo")
    logger.info("3. Uncomment the import and integration code above")


if __name__ == "__main__":
    asyncio.run(main())
