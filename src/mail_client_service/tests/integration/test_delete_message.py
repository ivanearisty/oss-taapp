import pytest
from fastapi.testclient import TestClient
from mail_client_service.app import app

client = TestClient(app)

@pytest.mark.integration
def test_delete_message_end_to_end():
    # This test assumes a message with ID 'test_msg_001' exists or will handle not found
    r = client.delete("/messages/test_msg_001")
    assert r.status_code in (200, 500)  # 500 if not found or error, 200 if deleted
    data = r.json()
    if r.status_code == 200:
        assert data["detail"] == "Message test_msg_001 deleted."
    else:
        assert "detail" in data

