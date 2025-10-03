import pytest
from fastapi.testclient import TestClient
from mail_client_service.app import app

client = TestClient(app)

@pytest.mark.integration
def test_get_messages_end_to_end():
    r = client.get("/messages")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)