"""Unit tests for GmailClient initialization.

This module contains comprehensive tests for the GmailClient.__init__ method,
covering all authentication scenarios and edge cases.
"""

import os
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

if TYPE_CHECKING:
    from gmail_client_impl import GmailClient
else:
    from gmail_client_impl import GmailClient


class TestGmailClientInit:
    """Test cases for GmailClient.__init__ method."""

    def test_init_with_provided_service(self) -> None:
        """Test initialization with a pre-configured service."""
        mock_service = Mock(spec=Resource)
        
        client = GmailClient(service=mock_service)
        
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token",
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_environment_variables(self, mock_request: Mock, mock_build: Mock) -> None:
        """Test initialization using environment variables (CI mode)."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_creds.to_json.return_value = '{"token": "data"}'  # Mock the to_json method
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service
        
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds_class.return_value = mock_creds
            
            with patch("gmail_client_impl._impl.Path") as mock_path:
                mock_path_instance = Mock()
                mock_path_instance.open.return_value.__enter__ = Mock()
                mock_path_instance.open.return_value.__exit__ = Mock(return_value=None)
                mock_path_instance.open.return_value.__enter__.return_value.write = Mock()
                mock_path.return_value = mock_path_instance
                
                client = GmailClient()
            
            # Verify credentials were created with environment variables
            mock_creds_class.assert_called_once_with(
                None,
                refresh_token="test_refresh_token",
                token_uri="https://oauth2.googleapis.com/token",
                client_id="test_client_id",
                client_secret="test_client_secret",
                scopes=GmailClient.SCOPES,
            )
            
            # Verify credentials were refreshed
            mock_creds.refresh.assert_called_once()
            
            # Verify service was built
            mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
            assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token",
        "GMAIL_TOKEN_URI": "https://custom.oauth.com/token",
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_custom_token_uri(self, mock_request: Mock, mock_build: Mock) -> None:
        """Test initialization with custom token URI from environment."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service
        
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds_class.return_value = mock_creds
            
            GmailClient()
            
            # Verify custom token URI was used
            mock_creds_class.assert_called_once_with(
                None,
                refresh_token="test_refresh_token",
                token_uri="https://custom.oauth.com/token",
                client_id="test_client_id",
                client_secret="test_client_secret",
                scopes=GmailClient.SCOPES,
            )

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    def test_init_with_token_file_valid(self, mock_creds_class: Mock, mock_path: Mock, mock_build: Mock) -> None:
        """Test initialization with valid token file."""
        # Clear environment variables to test token file path
        with patch.dict(os.environ, {}, clear=True):
            mock_creds = Mock(spec=Credentials)
            mock_creds.valid = True
            mock_service = Mock(spec=Resource)
            mock_build.return_value = mock_service
            
            # Mock Path.exists() to return True for token.json
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = True
            mock_path.return_value = mock_path_instance
            
            mock_creds_class.from_authorized_user_file.return_value = mock_creds
            
            client = GmailClient()
            
            # Verify token was loaded from file
            mock_creds_class.from_authorized_user_file.assert_called_once_with(
                "token.json", GmailClient.SCOPES,
            )
        
        # Verify service was built
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_token_file_needs_refresh(self, mock_request: Mock, mock_creds_class: Mock, mock_path: Mock, mock_build: Mock) -> None:
        """Test initialization with token file that needs refresh."""
        # Clear environment variables to test token file path
        with patch.dict(os.environ, {}, clear=True):
            mock_creds = Mock(spec=Credentials)
            mock_creds.valid = False
            mock_creds.refresh_token = "refresh_token"
            mock_service = Mock(spec=Resource)
            mock_build.return_value = mock_service
            
            # Mock Path.exists() to return True for token.json
            mock_path_instance = Mock()
            mock_path_instance.exists.return_value = True
            mock_path.return_value = mock_path_instance
            
            mock_creds_class.from_authorized_user_file.return_value = mock_creds
            
            # After refresh, make credentials valid
            def make_valid(*args: object) -> None:
                mock_creds.valid = True
            mock_creds.refresh.side_effect = make_valid
            
            client = GmailClient()
            
            # Verify token was refreshed
            mock_creds.refresh.assert_called_once()
            
            # Verify service was built
            mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
            assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Credentials")
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_token_file_refresh_fails(self, mock_request: Mock, mock_creds_class: Mock, mock_build: Mock) -> None:
        """Test initialization when token file refresh fails."""
        # Clear environment variables to test token file path
        with patch.dict(os.environ, {}, clear=True):
            mock_creds = Mock(spec=Credentials)
            mock_creds.valid = False
            mock_creds.refresh_token = "refresh_token"
            mock_creds.refresh.side_effect = RefreshError("Refresh failed")  # type: ignore[no-untyped-call]
            
            mock_creds_class.from_authorized_user_file.return_value = mock_creds
            
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock Path.exists() to return True for token.json
                mock_path.return_value.exists.return_value = True
                
                # Should now raise our new error instead of falling back to interactive
                with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
                    GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.InstalledAppFlow")
    @patch("gmail_client_impl._impl.Path")
    def test_init_interactive_flow_success(self, mock_path: Mock, mock_flow_class: Mock, mock_build: Mock) -> None:
        """Test successful interactive authentication flow."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service
        
        # Mock Path.exists() to return True for credentials.json
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        # Mock the interactive flow
        mock_flow = Mock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        
        # Mock file writing for token save
        mock_path_instance.open.return_value.__enter__ = Mock()
        mock_path_instance.open.return_value.__exit__ = Mock()
        mock_creds.to_json.return_value = '{"token": "data"}'
        
        client = GmailClient(interactive=True)
        
        # Verify interactive flow was used
        mock_flow_class.from_client_secrets_file.assert_called_once_with(
            "credentials.json", GmailClient.SCOPES,
        )
        mock_flow.run_local_server.assert_called_once_with(port=0)
        
        # Verify service was built
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.Path")
    def test_init_interactive_flow_missing_credentials(self, mock_path: Mock) -> None:
        """Test interactive flow when credentials.json is missing."""
        # Mock Path.exists() to return False for credentials.json
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
            GmailClient(interactive=True)

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.InstalledAppFlow")
    @patch("gmail_client_impl._impl.Path")
    def test_init_interactive_flow_fails(self, mock_path: Mock, mock_flow_class: Mock, mock_build: Mock) -> None:
        """Test when interactive flow fails."""
        # Mock Path.exists() to return True for credentials.json
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        # Mock the interactive flow to fail
        mock_flow = Mock()
        mock_flow.run_local_server.side_effect = Exception("Flow failed")
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        
        with pytest.raises(Exception, match="Flow failed"):
            GmailClient(interactive=True)

    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token",
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_env_vars_refresh_fails_fallback_to_interactive(self, mock_request: Mock) -> None:
        """Test that environment variable refresh failure raises error in non-interactive mode."""
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds = Mock(spec=Credentials)
            mock_creds.refresh.side_effect = RefreshError("Refresh failed")  # type: ignore[no-untyped-call]
            mock_creds_class.return_value = mock_creds
            
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock no token file exists
                mock_path.return_value.exists.return_value = False
                
                # Should now raise our new error instead of falling back to interactive
                with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
                    GmailClient()

    def test_init_no_valid_credentials_raises_error(self) -> None:
        """Test that RuntimeError is raised when no valid credentials can be obtained."""
        with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock no files exist
                mock_path.return_value.exists.return_value = False
                
                # Should now raise our new error instead of falling back to interactive
                with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
                    GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token",
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_service_build_fails(self, mock_request: Mock, mock_build: Mock) -> None:
        """Test when Gmail service build fails."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_build.side_effect = Exception("Service build failed")
        
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds_class.return_value = mock_creds
            
            with pytest.raises(Exception, match="Service build failed"):
                GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    def test_init_token_file_load_fails_fallback_to_interactive(self, mock_creds_class: Mock, mock_path: Mock, mock_build: Mock) -> None:
        """Test that token file loading failure raises error in non-interactive mode."""
        # Clear environment variables to test token file path
        with patch.dict(os.environ, {}, clear=True):
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock Path.exists() to return True for token.json
                mock_path.return_value.exists.return_value = True
                
                # Make from_authorized_user_file fail
                mock_creds_class.from_authorized_user_file.side_effect = Exception("File load failed")
                
                # Should now raise our new error instead of falling back to interactive
                with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
                    GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.InstalledAppFlow")
    def test_init_token_save_fails_but_continues(self, mock_flow_class: Mock, mock_build: Mock) -> None:
        """Test that token save failure raises an exception during the save process."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.to_json.return_value = '{"token": "data"}'
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service
        
        # Mock the interactive flow
        mock_flow = Mock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.from_client_secrets_file.return_value = mock_flow
        
        with patch("gmail_client_impl._impl.Path") as mock_path_class:
            # Mock Path instances for different files
            def path_constructor_side_effect(path_str: object) -> Mock:
                mock_path_instance = Mock()
                if "credentials.json" in str(path_str):
                    mock_path_instance.exists.return_value = True
                elif "token.json" in str(path_str):
                    mock_path_instance.exists.return_value = False
                    # Mock file writing context manager to fail
                    mock_file = Mock()
                    mock_context_manager = Mock()
                    mock_context_manager.__enter__ = Mock(return_value=mock_file)
                    mock_context_manager.__exit__ = Mock(return_value=None)
                    mock_path_instance.open.return_value = mock_context_manager
                    mock_file.write.side_effect = Exception("Save failed")
                else:
                    mock_path_instance.exists.return_value = False
                return mock_path_instance
            
            mock_path_class.side_effect = path_constructor_side_effect
            
            with pytest.raises(Exception, match="Save failed"):
                GmailClient(interactive=True)

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "",  # Empty string should be treated as missing
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token",
    })
    @patch("gmail_client_impl._impl.Path")
    def test_init_partial_env_vars_fallback(self, mock_path: Mock, mock_build: Mock) -> None:
        """Test that partial environment variables don't cause authentication."""
        # Mock no files exist
        mock_path.return_value.exists.return_value = False
        
        # Should now raise our new error instead of falling back to interactive
        with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
            GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    def test_init_invalid_credentials_no_refresh_token(self, mock_creds_class: Mock, mock_path: Mock, mock_build: Mock) -> None:
        """Test handling of invalid credentials with no refresh token."""
        # Clear environment variables to test token file path
        with patch.dict(os.environ, {}, clear=True):
            mock_creds = Mock(spec=Credentials)
            mock_creds.valid = False
            mock_creds.refresh_token = None  # No refresh token available
            
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock Path.exists() to return True for token.json
                mock_path.return_value.exists.return_value = True
                
                mock_creds_class.from_authorized_user_file.return_value = mock_creds
                
                # Should now raise our new error instead of falling back to interactive
                with pytest.raises(RuntimeError, match="No valid credentials found and interactive mode is disabled"):
                    GmailClient()


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
