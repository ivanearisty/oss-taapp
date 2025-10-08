"""Tests for ServiceClientAdapter in main.py.

These tests monkeypatch the generated API functions so no real HTTP requests are made.
"""

import json
from types import SimpleNamespace


def test_get_messages_respects_max_results(monkeypatch) -> None:
    """Tests get message request max results."""
    import service_client_adapter.src.service_client_adapter.main as main_mod

    class FakeGetMessages:
        @staticmethod
        def sync_detailed(client) -> SimpleNamespace:
            payload = {"messages": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
            return SimpleNamespace(content=json.dumps(payload))

    # Monkeypatch the imported get_messages
    monkeypatch.setattr(main_mod, "get_messages", FakeGetMessages)

    adapter = main_mod.ServiceClientAdapter()
    results = adapter.get_messages(max_results=2)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"


def test_get_message_calls_api_and_returns(monkeypatch) -> None:
    """Tests get message api."""
    import service_client_adapter.src.service_client_adapter.main as main_mod

    captured = {}

    class FakeGetMessage:
        @staticmethod
        def sync_detailed(message_id, client) -> str:
            captured["message_id"] = message_id
            captured["client"] = client
            return "SENTINEL"

    monkeypatch.setattr(main_mod, "get_message", FakeGetMessage)

    adapter = main_mod.ServiceClientAdapter()
    result = adapter.get_message("abc-123")

    assert result == "SENTINEL"
    assert captured["message_id"] == "abc-123"
    assert captured["client"] is adapter.Client


def test_delete_and_mark_and_login(monkeypatch) -> None:
    """Tests delete message, marking messages as read and login."""
    import service_client_adapter.src.service_client_adapter.main as main_mod

    class FakeDelete:
        @staticmethod
        def sync_detailed(message_id, client) -> bool:
            return True

    class FakeMark:
        @staticmethod
        def sync_detailed(message_id, client) -> bool:
            return False

    class FakeLogin:
        @staticmethod
        def sync_detailed(client) -> SimpleNamespace:
            return SimpleNamespace(token="abc")

    monkeypatch.setattr(main_mod, "delete_message", FakeDelete)
    monkeypatch.setattr(main_mod, "mark_message_as_read", FakeMark)
    monkeypatch.setattr(main_mod, "login", FakeLogin)

    adapter = main_mod.ServiceClientAdapter()

    # delete_message returns True
    assert adapter.delete_message("x") is True
    # mark_as_read returns False
    assert adapter.mark_as_read("x") is False
    # login returns fake token object
    login_result = adapter.login()
    assert hasattr(login_result, "token")
    assert login_result.token == "abc"
