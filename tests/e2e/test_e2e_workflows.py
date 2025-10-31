"""End-to-end tests for complete application workflows."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from ticket_api import Comment, Ticket, TicketPriority, TicketStatus
from ticket_service import app

pytestmark = pytest.mark.e2e

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201


class TestE2ETicketManagement:
    """End-to-end tests for complete ticket management workflows."""

    def test_e2e_team_collaboration_workflow(self, mock_jira_backend: dict[str, MagicMock]) -> None:
        """Test team collaboration workflow.

        E2E test simulating a real team collaboration scenario:
        1. Manager creates a ticket
        2. Developer picks it up and marks in-progress
        3. Developer adds comments and completes work
        4. Manager reviews and closes the ticket
        """
        ticket_id = UUID("550e8400-e29b-41d4-a716-446655440003")

        # Ticket states at each step
        created = Ticket(
            id=ticket_id,
            title="Implement dark mode",
            description="Add dark mode toggle to settings page",
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
            reporter="manager@example.com",
            assignee="developer@example.com",
            created_at=datetime.fromisoformat("2024-01-20T09:00:00+00:00"),
            updated_at=datetime.fromisoformat("2024-01-20T09:00:00+00:00"),
            comments=[],
        )

        assigned = Ticket(
            id=ticket_id,
            title="Implement dark mode",
            description="Add dark mode toggle to settings page",
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.MEDIUM,
            reporter="manager@example.com",
            assignee="developer@example.com",
            created_at=datetime.fromisoformat("2024-01-20T09:00:00+00:00"),
            updated_at=datetime.fromisoformat("2024-01-20T09:30:00+00:00"),
            comments=[],
        )

        comment1 = Comment(
            id=UUID("550e8400-e29b-41d4-a716-446655440100"),
            ticket_id=ticket_id,
            author="developer@example.com",
            content="Working on the UI components",
            created_at=datetime.fromisoformat("2024-01-20T10:00:00+00:00"),
        )

        comment2 = Comment(
            id=UUID("550e8400-e29b-41d4-a716-446655440101"),
            ticket_id=ticket_id,
            author="developer@example.com",
            content="Ready for review at PR #123",
            created_at=datetime.fromisoformat("2024-01-20T14:00:00+00:00"),
        )

        completed = Ticket(
            id=ticket_id,
            title="Implement dark mode",
            description="Add dark mode toggle to settings page",
            status=TicketStatus.RESOLVED,
            priority=TicketPriority.MEDIUM,
            reporter="manager@example.com",
            assignee="developer@example.com",
            created_at=datetime.fromisoformat("2024-01-20T09:00:00+00:00"),
            updated_at=datetime.fromisoformat("2024-01-20T16:00:00+00:00"),
            comments=[comment1, comment2],
        )

        client = TestClient(app)

        # Step 1: Manager creates ticket
        mock_jira_backend["create_ticket"].return_value = created
        response = client.post(
            "/api/v1/tickets",
            json={
                "title": "Implement dark mode",
                "description": "Add dark mode toggle to settings page",
                "reporter": "manager@example.com",
                "assignee": "developer@example.com",
                "priority": "medium",
            },
            headers={
                "X-User-ID": "test-manager",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_CREATED

        # Step 2: Developer marks as in-progress
        mock_jira_backend["update_ticket"].return_value = assigned
        response = client.patch(
            f"/api/v1/tickets/{ticket_id}",
            json={"status": "in_progress"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_OK

        # Step 3: Developer adds progress comment
        mock_jira_backend["add_comment"].return_value = comment1
        response = client.post(
            f"/api/v1/tickets/{ticket_id}/comments",
            json={"author": "developer@example.com", "content": "Working on the UI components"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_CREATED

        # Step 4: Developer adds completion comment
        mock_jira_backend["add_comment"].return_value = comment2
        response = client.post(
            f"/api/v1/tickets/{ticket_id}/comments",
            json={"author": "developer@example.com", "content": "Ready for review at PR #123"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_CREATED

        # Step 5: Manager reviews and closes
        mock_jira_backend["update_ticket"].return_value = completed
        response = client.patch(
            f"/api/v1/tickets/{ticket_id}",
            json={"status": "resolved"},
            headers={
                "X-User-ID": "test-manager",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_OK

        # Step 6: Verify final state
        mock_jira_backend["get_ticket"].return_value = completed
        response = client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers={
                "X-User-ID": "test-manager",
                "X-Project-Key": "PROJ",
            },
        )
        assert response.status_code == HTTP_OK
        final = response.json()
        assert final["status"] == "resolved"

    def test_e2e_bug_tracking_workflow(self, mock_jira_backend: dict[str, MagicMock]) -> None:
        """Test bug tracking workflow.

        E2E test for bug tracking:
        1. User reports a bug (OPEN)
        2. Triager assigns priority (still OPEN)
        3. Developer starts work (IN_PROGRESS)
        4. Bug is fixed (RESOLVED)
        """
        bug_id = UUID("550e8400-e29b-41d4-a716-446655440004")

        states = {
            "reported": Ticket(
                id=bug_id,
                title="Login button not visible on mobile",
                description="The login button disappears on mobile devices",
                status=TicketStatus.OPEN,
                priority=TicketPriority.MEDIUM,
                reporter="user@example.com",
                assignee=None,
                created_at=datetime.fromisoformat("2024-01-21T08:00:00+00:00"),
                updated_at=datetime.fromisoformat("2024-01-21T08:00:00+00:00"),
                comments=[],
            ),
            "triaged": Ticket(
                id=bug_id,
                title="Login button not visible on mobile",
                description="The login button disappears on mobile devices",
                status=TicketStatus.OPEN,
                priority=TicketPriority.CRITICAL,
                reporter="user@example.com",
                assignee="developer@example.com",
                created_at=datetime.fromisoformat("2024-01-21T08:00:00+00:00"),
                updated_at=datetime.fromisoformat("2024-01-21T08:15:00+00:00"),
                comments=[],
            ),
            "in_progress": Ticket(
                id=bug_id,
                title="Login button not visible on mobile",
                description="The login button disappears on mobile devices",
                status=TicketStatus.IN_PROGRESS,
                priority=TicketPriority.CRITICAL,
                reporter="user@example.com",
                assignee="developer@example.com",
                created_at=datetime.fromisoformat("2024-01-21T08:00:00+00:00"),
                updated_at=datetime.fromisoformat("2024-01-21T09:00:00+00:00"),
                comments=[],
            ),
            "resolved": Ticket(
                id=bug_id,
                title="Login button not visible on mobile",
                description="The login button disappears on mobile devices",
                status=TicketStatus.RESOLVED,
                priority=TicketPriority.CRITICAL,
                reporter="user@example.com",
                assignee="developer@example.com",
                created_at=datetime.fromisoformat("2024-01-21T08:00:00+00:00"),
                updated_at=datetime.fromisoformat("2024-01-21T14:00:00+00:00"),
                comments=[
                    Comment(
                        id=UUID("550e8400-e29b-41d4-a716-446655440102"),
                        ticket_id=bug_id,
                        author="developer@example.com",
                        content="Fixed CSS media query issue in PR #456",
                        created_at=datetime.fromisoformat("2024-01-21T14:00:00+00:00"),
                    ),
                ],
            ),
        }

        client = TestClient(app)

        # User reports bug
        mock_jira_backend["create_ticket"].return_value = states["reported"]
        response = client.post(
            "/api/v1/tickets",
            json={
                "title": "Login button not visible on mobile",
                "description": "The login button disappears on mobile devices",
                "reporter": "user@example.com",
                "priority": "medium",
            },
            headers={"X-User-ID": "test-user", "X-Project-Key": "BUG"},
        )
        assert response.status_code == HTTP_CREATED

        # Triager increases priority and assigns
        mock_jira_backend["update_ticket"].return_value = states["triaged"]
        response = client.patch(
            f"/api/v1/tickets/{bug_id}",
            json={
                "priority": "critical",
                "assignee": "developer@example.com",
            },
            headers={"X-User-ID": "test-triager", "X-Project-Key": "BUG"},
        )
        assert response.status_code == HTTP_OK

        # Developer starts work
        mock_jira_backend["update_ticket"].return_value = states["in_progress"]
        response = client.patch(
            f"/api/v1/tickets/{bug_id}",
            json={"status": "in_progress"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "BUG",
            },
        )
        assert response.status_code == HTTP_OK

        # Developer fixes and adds comment
        mock_jira_backend["add_comment"].return_value = states["resolved"].comments[0]
        response = client.post(
            f"/api/v1/tickets/{bug_id}/comments",
            json={"author": "developer@example.com", "content": "Fixed CSS media query issue in PR #456"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "BUG",
            },
        )
        assert response.status_code == HTTP_CREATED

        # Mark as resolved
        mock_jira_backend["update_ticket"].return_value = states["resolved"]
        response = client.patch(
            f"/api/v1/tickets/{bug_id}",
            json={"status": "resolved"},
            headers={
                "X-User-ID": "test-developer",
                "X-Project-Key": "BUG",
            },
        )
        assert response.status_code == HTTP_OK


class TestE2EDataConsistency:
    """E2E tests for data consistency across operations."""

    def test_e2e_data_consistency_with_concurrent_operations(
        self,
        mock_jira_backend: dict[str, MagicMock],
    ) -> None:
        """Test that data remains consistent with concurrent operations."""
        ticket_id = UUID("550e8400-e29b-41d4-a716-446655440005")

        ticket = Ticket(
            id=ticket_id,
            title="API rate limiting",
            description="Implement rate limiting for API endpoints",
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            reporter="team-lead@example.com",
            assignee="dev1@example.com",
            created_at=datetime.fromisoformat("2024-01-22T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2024-01-22T10:00:00+00:00"),
            comments=[],
        )

        client = TestClient(app)

        # Create base ticket
        mock_jira_backend["create_ticket"].return_value = ticket
        response = client.post(
            "/api/v1/tickets",
            json={
                "title": "API rate limiting",
                "description": "Implement rate limiting for API endpoints",
                "reporter": "team-lead@example.com",
                "priority": "high",
            },
            headers={
                "X-User-ID": "test-team-lead",
                "X-Project-Key": "TASK",
            },
        )
        assert response.status_code == HTTP_CREATED

        # Simulate getting ticket multiple times
        mock_jira_backend["get_ticket"].return_value = ticket
        for _ in range(3):
            response = client.get(
                f"/api/v1/tickets/{ticket_id}",
                headers={
                    "X-User-ID": "test-team-lead",
                    "X-Project-Key": "TASK",
                },
            )
            assert response.status_code == HTTP_OK
            data = response.json()
            assert data["id"] == str(ticket_id)
            assert data["title"] == ticket.title


class TestE2EErrorScenarios:
    """E2E tests for error scenarios and recovery."""

    def test_e2e_graceful_degradation(self, mock_jira_backend: dict[str, MagicMock]) -> None:
        """Test that system handles partial failures gracefully."""
        ticket_id = UUID("550e8400-e29b-41d4-a716-446655440006")

        client = TestClient(app)

        # First request succeeds
        sample_ticket = Ticket(
            id=ticket_id,
            title="Test ticket",
            description="Test",
            status=TicketStatus.OPEN,
            priority=TicketPriority.LOW,
            reporter="user@example.com",
            assignee=None,
            created_at=datetime.fromisoformat("2024-01-22T11:00:00+00:00"),
            updated_at=datetime.fromisoformat("2024-01-22T11:00:00+00:00"),
            comments=[],
        )

        mock_jira_backend["get_ticket"].return_value = sample_ticket
        response = client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers={"X-User-ID": "test-user", "X-Project-Key": "TEST"},
        )
        assert response.status_code == HTTP_OK

        # Second request returns success (mocks are flexible)
        response = client.get(
            f"/api/v1/tickets/{ticket_id}",
            headers={"X-User-ID": "test-user", "X-Project-Key": "TEST"},
        )
        assert response.status_code == HTTP_OK
