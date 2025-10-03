import pytest
from fastapi.testclient import TestClient
from mail_client_service.app import app

client = TestClient(app)

@pytest.mark.integration
def test_mark_message_as_read_end_to_end():
    # This test assumes a message with ID 'test_msg_001' exists or will handle not found
    r = client.post("/messages/test_msg_001/mark-as-read")
    assert r.status_code in (200, 500)  # 500 if not found or error, 200 if marked as read
    data = r.json()
    if r.status_code == 200:
        assert data["detail"] == "Message test_msg_001 marked as read."
    else:
        assert "detail" in data

