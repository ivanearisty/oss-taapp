from unittest.mock import Mock
from fastapi.testclient import TestClient
import pytest
from mail_client_api import Client, Message
from mail_client_service.main import app, get_client

# Create a mock client that conforms to the Client protocol
mock_client = Mock(spec=Client)

# Use FastAPI's dependency override to replace the real client with our mock
def get_mock_client():
    return mock_client

app.dependency_overrides[get_client] = get_mock_client

# Create a TestClient instance for making requests
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test to ensure isolation."""
    mock_client.reset_mock()

def test_get_messages_success():
    """Test the GET /messages endpoint for a successful response."""
    # ARRANGE
    mock_message_data = Mock(spec=Message)
    mock_message_data.id = "123"
    mock_message_data.from_ = "sender@example.com"
    mock_message_data.to = "receiver@example.com"
    mock_message_data.date = "01/01/2025"
    mock_message_data.subject = "Test Subject"
    mock_message_data.body = "Test Body"
    
    mock_client.get_messages.return_value = iter([mock_message_data])

    # ACT
    response = client.get("/messages?limit=1")

    # ASSERT
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["id"] == "123"
    assert response_json[0]["subject"] == "Test Subject"
    assert response_json[0]["from_address"] == "sender@example.com" # Note the alias
    mock_client.get_messages.assert_called_once_with(max_results=1)

def test_delete_message_success():
    """Test the DELETE /messages/{message_id} endpoint."""
    # ARRANGE
    message_id = "abc-123"
    mock_client.delete_message.return_value = True

    # ACT
    response = client.delete(f"/messages/{message_id}")

    # ASSERT
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": f"Message {message_id} deleted."}
    mock_client.delete_message.assert_called_once_with(message_id)

def test_delete_message_failure():
    """Test the DELETE endpoint when the underlying client fails."""
    # ARRANGE
    message_id = "abc-123"
    mock_client.delete_message.return_value = False

    # ACT
    response = client.delete(f"/messages/{message_id}")

    # ASSERT
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to delete message."}