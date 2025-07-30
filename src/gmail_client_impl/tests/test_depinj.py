from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

if TYPE_CHECKING:
    from gmail_client_impl import GmailClient
else:
    from gmail_client_impl import GmailClient

class TestGetClientImpl:
    """Test cases for the get_client_impl factory function."""
    
    @patch("gmail_client_impl.GmailClient")
    def test_get_client_impl_default(self, mock_gmail_client: Mock) -> None:
        """Test get_client_impl with default parameters."""
        from gmail_client_impl import get_client_impl
        
        mock_instance = Mock()
        mock_gmail_client.return_value = mock_instance
        
        result = get_client_impl()
        
        mock_gmail_client.assert_called_once_with(interactive=False)
        assert result is mock_instance

    @patch("gmail_client_impl.GmailClient")
    def test_get_client_impl_interactive(self, mock_gmail_client: Mock) -> None:
        """Test get_client_impl with interactive=True."""
        from gmail_client_impl import get_client_impl
        
        mock_instance = Mock()
        mock_gmail_client.return_value = mock_instance
        
        result = get_client_impl(interactive=True)
        
        mock_gmail_client.assert_called_once_with(interactive=True)
        assert result is mock_instance

    def test_dependency_injection(self) -> None:
        """Test that the dependency injection modifies mail_client_api.get_client."""
        import mail_client_api
        from gmail_client_impl import get_client_impl
        
        # Verify that mail_client_api.get_client is now our implementation
        assert mail_client_api.get_client is get_client_impl