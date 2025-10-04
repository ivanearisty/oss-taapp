"""Simple models for API responses."""

from typing import Any, Dict, List, Optional


class ListMessagesResponse:
    """Response for list messages API."""
    
    def __init__(self, data: List[Dict[str, str]]):
        self.data = data
    
    def to_dict(self) -> List[Dict[str, str]]:
        return self.data


class GetMessageResponse:
    """Response for get message API."""
    
    def __init__(self, data: Dict[str, str]):
        self.data = data
    
    def to_dict(self) -> Dict[str, str]:
        return self.data


class DeleteMessageResponse:
    """Response for delete message API."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        return self.data


class MarkAsReadResponse:
    """Response for mark as read API."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        return self.data
