"""Unit tests for GmailClient initialization.

This module contains comprehensive tests for the GmailClient.__init__ method,
covering all authentication scenarios and edge cases.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

from gmail_client_impl import GmailClient


class TestGmailClientInit:
    """Test cases for GmailClient.__init__ method."""

    def test_init_with_provided_service(self):
        """Test initialization with a pre-configured service."""
        mock_service = Mock(spec=Resource)
        
        client = GmailClient(service=mock_service)
        
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret", 
        "GMAIL_REFRESH_TOKEN": "test_refresh_token"
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_environment_variables(self, mock_request, mock_build):
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
        "GMAIL_TOKEN_URI": "https://custom.oauth.com/token"
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_custom_token_uri(self, mock_request, mock_build):
        """Test initialization with custom token URI from environment."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = True
        mock_service = Mock(spec=Resource)
        mock_build.return_value = mock_service
        
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds_class.return_value = mock_creds
            
            client = GmailClient()
            
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
    def test_init_with_token_file_valid(self, mock_creds_class, mock_path, mock_build):
        """Test initialization with valid token file."""
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
            "token.json", GmailClient.SCOPES
        )
        
        # Verify service was built
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    @patch("gmail_client_impl._impl.Request")
    def test_init_with_token_file_needs_refresh(self, mock_request, mock_creds_class, mock_path, mock_build):
        """Test initialization with token file that needs refresh."""
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
        def make_valid(*args):
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
    def test_init_with_token_file_refresh_fails(self, mock_request, mock_creds_class, mock_build):
        """Test initialization when token file refresh fails."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.refresh_token = "refresh_token"
        mock_creds.refresh.side_effect = RefreshError("Refresh failed")
        
        mock_creds_class.from_authorized_user_file.return_value = mock_creds
        
        with patch("gmail_client_impl._impl.Path") as mock_path:
            # Mock Path.exists() to return True for token.json, False for credentials.json
            def path_exists_side_effect(*args, **kwargs):
                path_str = str(args[0]) if args else str(kwargs.get('self', ''))
                if "token.json" in path_str:
                    return True
                elif "credentials.json" in path_str:
                    return False
                return False
            
            mock_path.return_value.exists.side_effect = path_exists_side_effect
            
            # Should raise RuntimeError when interactive flow fails due to missing credentials.json
            with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
                GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.InstalledAppFlow")
    @patch("gmail_client_impl._impl.Path")
    def test_init_interactive_flow_success(self, mock_path, mock_flow_class, mock_build):
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
            "credentials.json", GmailClient.SCOPES
        )
        mock_flow.run_local_server.assert_called_once_with(port=0)
        
        # Verify service was built
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_creds)
        assert client.service is mock_service

    @patch("gmail_client_impl._impl.Path")
    def test_init_interactive_flow_missing_credentials(self, mock_path):
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
    def test_init_interactive_flow_fails(self, mock_path, mock_flow_class, mock_build):
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
        "GMAIL_REFRESH_TOKEN": "test_refresh_token"
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_env_vars_refresh_fails_fallback_to_interactive(self, mock_request):
        """Test fallback to interactive when environment variable refresh fails."""
        with patch("gmail_client_impl._impl.Credentials") as mock_creds_class:
            mock_creds = Mock(spec=Credentials)
            mock_creds.refresh.side_effect = RefreshError("Refresh failed")
            mock_creds_class.return_value = mock_creds
            
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock credentials.json exists but token.json doesn't
                def path_exists_side_effect(*args, **kwargs):
                    path_str = str(args[0]) if args else str(kwargs.get('self', ''))
                    if "credentials.json" in path_str:
                        return False  # This will cause FileNotFoundError
                    return False
                
                mock_path.return_value.exists.side_effect = path_exists_side_effect
                
                with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
                    GmailClient()

    def test_init_no_valid_credentials_raises_error(self):
        """Test that RuntimeError is raised when no valid credentials can be obtained."""
        with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            with patch("gmail_client_impl._impl.Path") as mock_path:
                # Mock no files exist
                mock_path.return_value.exists.return_value = False
                
                with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
                    GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch.dict(os.environ, {
        "GMAIL_CLIENT_ID": "test_client_id",
        "GMAIL_CLIENT_SECRET": "test_client_secret",
        "GMAIL_REFRESH_TOKEN": "test_refresh_token"
    })
    @patch("gmail_client_impl._impl.Request")
    def test_init_service_build_fails(self, mock_request, mock_build):
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
    def test_init_token_file_load_fails_fallback_to_interactive(self, mock_creds_class, mock_path, mock_build):
        """Test fallback to interactive when token file loading fails."""
        with patch("gmail_client_impl._impl.Path") as mock_path:
            # Mock Path.exists() to return True for token.json but False for credentials.json
            def path_exists_side_effect(*args, **kwargs):
                path_str = str(args[0]) if args else str(kwargs.get('self', ''))
                if "token.json" in path_str:
                    return True
                elif "credentials.json" in path_str:
                    return False
                return False
            
            mock_path.return_value.exists.side_effect = path_exists_side_effect
            
            # Make from_authorized_user_file fail
            mock_creds_class.from_authorized_user_file.side_effect = Exception("File load failed")
            
            with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
                GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.InstalledAppFlow")
    def test_init_token_save_fails_but_continues(self, mock_flow_class, mock_build):
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
            def path_constructor_side_effect(path_str):
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
        "GMAIL_REFRESH_TOKEN": "test_refresh_token"
    })
    @patch("gmail_client_impl._impl.Path")
    def test_init_partial_env_vars_fallback(self, mock_path, mock_build):
        """Test that partial environment variables don't cause authentication."""
        # Mock no files exist
        mock_path.return_value.exists.return_value = False
        
        # Should fallback to interactive flow and fail due to missing credentials.json
        with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
            GmailClient()

    @patch("gmail_client_impl._impl.build")
    @patch("gmail_client_impl._impl.Path")
    @patch("gmail_client_impl._impl.Credentials")
    def test_init_invalid_credentials_no_refresh_token(self, mock_creds_class, mock_path, mock_build):
        """Test handling of invalid credentials with no refresh token."""
        mock_creds = Mock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.refresh_token = None  # No refresh token available
        
        with patch("gmail_client_impl._impl.Path") as mock_path:
            # Mock Path.exists() to return True for token.json, False for credentials.json
            def path_exists_side_effect(*args, **kwargs):
                path_str = str(args[0]) if args else str(kwargs.get('self', ''))
                if "token.json" in path_str:
                    return True
                elif "credentials.json" in path_str:
                    return False
                return False
            
            mock_path.return_value.exists.side_effect = path_exists_side_effect
            
            mock_creds_class.from_authorized_user_file.return_value = mock_creds
            
            # Should fallback to interactive flow and fail due to missing credentials.json
            with pytest.raises(FileNotFoundError, match="'credentials.json' not found"):
                GmailClient()
