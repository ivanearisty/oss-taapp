"""Tests for model classes."""

from mail_client_adapter.models import (
    DeleteMessageResponse,
    GetMessageResponse,
    ListMessagesResponse,
    MarkAsReadResponse,
)


class TestListMessagesResponse:
    """Test cases for ListMessagesResponse class."""

    def test_list_messages_response_initialization(self) -> None:
        """Test ListMessagesResponse initialization."""
        data = [
            {"id": "msg1", "from": "sender1@example.com", "subject": "Test 1"},
            {"id": "msg2", "from": "sender2@example.com", "subject": "Test 2"},
        ]

        response = ListMessagesResponse(data)

        assert response.data == data

    def test_list_messages_response_to_dict(self) -> None:
        """Test ListMessagesResponse to_dict method."""
        data = [
            {"id": "msg1", "from": "sender1@example.com", "subject": "Test 1"},
            {"id": "msg2", "from": "sender2@example.com", "subject": "Test 2"},
        ]

        response = ListMessagesResponse(data)
        result = response.to_dict()

        assert result == data
        assert isinstance(result, list)

    def test_list_messages_response_empty_list(self) -> None:
        """Test ListMessagesResponse with empty list."""
        data = []

        response = ListMessagesResponse(data)

        assert response.data == []
        assert response.to_dict() == []

    def test_list_messages_response_single_item(self) -> None:
        """Test ListMessagesResponse with single item."""
        data = [{"id": "msg1", "from": "sender@example.com", "subject": "Test"}]

        response = ListMessagesResponse(data)

        assert response.data == data
        assert response.to_dict() == data

    def test_list_messages_response_data_mutation(self) -> None:
        """Test that modifying the original data affects the response (no copying)."""
        original_data = [{"id": "msg1", "subject": "Test"}]
        response = ListMessagesResponse(original_data)

        # Modify original data
        original_data.append({"id": "msg2", "subject": "Test 2"})

        # Response data should be modified since it's the same reference
        assert len(response.data) == len(original_data[0].keys())
        assert response.data[0]["id"] == "msg1"
        assert response.data[1]["id"] == "msg2"


class TestGetMessageResponse:
    """Test cases for GetMessageResponse class."""

    def test_get_message_response_initialization(self) -> None:
        """Test GetMessageResponse initialization."""
        data = {
            "id": "msg123",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test Body",
        }

        response = GetMessageResponse(data)

        assert response.data == data

    def test_get_message_response_to_dict(self) -> None:
        """Test GetMessageResponse to_dict method."""
        data = {"id": "msg123", "from": "sender@example.com", "subject": "Test Subject"}

        response = GetMessageResponse(data)
        result = response.to_dict()

        assert result == data
        assert isinstance(result, dict)

    def test_get_message_response_empty_dict(self) -> None:
        """Test GetMessageResponse with empty dictionary."""
        data = {}

        response = GetMessageResponse(data)

        assert response.data == {}
        assert response.to_dict() == {}

    def test_get_message_response_data_mutation(self) -> None:
        """Test that modifying the original data affects the response (no copying)."""
        original_data = {"id": "msg123", "subject": "Test"}
        response = GetMessageResponse(original_data)

        # Modify original data
        original_data["subject"] = "Modified"

        # Response data should be modified since it's the same reference
        assert response.data["subject"] == "Modified"


class TestDeleteMessageResponse:
    """Test cases for DeleteMessageResponse class."""

    def test_delete_message_response_initialization(self) -> None:
        """Test DeleteMessageResponse initialization."""
        data = {"success": True, "message": "Message deleted successfully"}

        response = DeleteMessageResponse(data)

        assert response.data == data

    def test_delete_message_response_to_dict(self) -> None:
        """Test DeleteMessageResponse to_dict method."""
        data = {"success": True, "message": "Message deleted successfully"}

        response = DeleteMessageResponse(data)
        result = response.to_dict()

        assert result == data
        assert isinstance(result, dict)

    def test_delete_message_response_with_different_data_types(self) -> None:
        """Test DeleteMessageResponse with various data types."""
        data = {
            "success": True,
            "message": "Success",
            "count": 1,
            "timestamp": "2024-01-01T00:00:00Z",
            "metadata": {"deleted_by": "user123"},
        }

        response = DeleteMessageResponse(data)

        assert response.data == data
        assert response.to_dict() == data

    def test_delete_message_response_failure(self) -> None:
        """Test DeleteMessageResponse with failure data."""
        data = {"success": False, "error": "Message not found"}

        response = DeleteMessageResponse(data)

        assert response.data == data
        assert response.to_dict() == data


class TestMarkAsReadResponse:
    """Test cases for MarkAsReadResponse class."""

    def test_mark_as_read_response_initialization(self) -> None:
        """Test MarkAsReadResponse initialization."""
        data = {"success": True, "message": "Message marked as read"}

        response = MarkAsReadResponse(data)

        assert response.data == data

    def test_mark_as_read_response_to_dict(self) -> None:
        """Test MarkAsReadResponse to_dict method."""
        data = {"success": True, "message": "Message marked as read"}

        response = MarkAsReadResponse(data)
        result = response.to_dict()

        assert result == data
        assert isinstance(result, dict)

    def test_mark_as_read_response_with_different_data_types(self) -> None:
        """Test MarkAsReadResponse with various data types."""
        data = {
            "success": True,
            "message": "Success",
            "read_at": "2024-01-01T00:00:00Z",
            "user_id": "user123",
            "metadata": {"read_by": "user123", "timestamp": "2024-01-01T00:00:00Z"},
        }

        response = MarkAsReadResponse(data)

        assert response.data == data
        assert response.to_dict() == data

    def test_mark_as_read_response_failure(self) -> None:
        """Test MarkAsReadResponse with failure data."""
        data = {"success": False, "error": "Message not found"}

        response = MarkAsReadResponse(data)

        assert response.data == data
        assert response.to_dict() == data

    def test_mark_as_read_response_data_mutation(self) -> None:
        """Test that modifying the original data affects the response (no copying)."""
        original_data = {"success": True, "message": "Success"}
        response = MarkAsReadResponse(original_data)

        # Modify original data
        original_data["success"] = False

        # Response data should be modified since it's the same reference
        assert response.data["success"] is False


class TestModelClassesGeneral:
    """General test cases for all model classes."""

    def test_all_models_have_data_attribute(self) -> None:
        """Test that all model classes have a data attribute."""
        data = {"test": "value"}

        list_response = ListMessagesResponse([data])
        get_response = GetMessageResponse(data)
        delete_response = DeleteMessageResponse(data)
        mark_response = MarkAsReadResponse(data)

        assert hasattr(list_response, "data")
        assert hasattr(get_response, "data")
        assert hasattr(delete_response, "data")
        assert hasattr(mark_response, "data")

    def test_all_models_have_to_dict_method(self) -> None:
        """Test that all model classes have a to_dict method."""
        data = {"test": "value"}

        list_response = ListMessagesResponse([data])
        get_response = GetMessageResponse(data)
        delete_response = DeleteMessageResponse(data)
        mark_response = MarkAsReadResponse(data)

        assert hasattr(list_response, "to_dict")
        assert hasattr(get_response, "to_dict")
        assert hasattr(delete_response, "to_dict")
        assert hasattr(mark_response, "to_dict")

        assert callable(list_response.to_dict)
        assert callable(get_response.to_dict)
        assert callable(delete_response.to_dict)
        assert callable(mark_response.to_dict)

    def test_models_with_none_data(self) -> None:
        """Test model classes with None data."""
        # This should work without raising exceptions
        list_response = ListMessagesResponse(None)
        get_response = GetMessageResponse(None)
        delete_response = DeleteMessageResponse(None)
        mark_response = MarkAsReadResponse(None)

        assert list_response.data is None
        assert get_response.data is None
        assert delete_response.data is None
        assert mark_response.data is None

    def test_models_to_dict_with_none_data(self) -> None:
        """Test to_dict method with None data."""
        list_response = ListMessagesResponse(None)
        get_response = GetMessageResponse(None)
        delete_response = DeleteMessageResponse(None)
        mark_response = MarkAsReadResponse(None)

        assert list_response.to_dict() is None
        assert get_response.to_dict() is None
        assert delete_response.to_dict() is None
        assert mark_response.to_dict() is None
