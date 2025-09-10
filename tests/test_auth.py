"""
Tests for authentication flows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sellerlegend_api.auth import OAuth2Client
from sellerlegend_api.exceptions import AuthenticationError
from tests.fixtures.responses import (
    AUTH_SUCCESS_RESPONSE,
    AUTH_ERROR_RESPONSE
)


class TestOAuth2Client:
    """Test OAuth2 authentication client."""
    
    def test_initialization(self):
        """Test OAuth2Client initialization."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com",
            redirect_uri="http://localhost:5001/callback"
        )
        
        assert client.client_id == "test_id"
        assert client.client_secret == "test_secret"
        assert client.base_url == "https://test.sellerlegend.com"
        assert client.redirect_uri == "http://localhost:5001/callback"
        assert client.access_token is None
        assert client.refresh_token is None
    
    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com",
            redirect_uri="http://localhost:5001/callback"
        )
        
        auth_url, state = client.get_authorization_url(scope="read write")
        
        assert "https://test.sellerlegend.com/oauth/authorize" in auth_url
        assert "client_id=test_id" in auth_url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A5001%2Fcallback" in auth_url
        assert "response_type=code" in auth_url
        assert "scope=read+write" in auth_url
        assert f"state={state}" in auth_url
        assert len(state) == 43  # Default state length (token_urlsafe(32) creates 43 chars)
    
    def test_get_authorization_url_with_custom_state(self):
        """Test authorization URL with custom state."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        
        custom_state = "custom_state_123"
        auth_url, state = client.get_authorization_url(state=custom_state)
        
        assert f"state={custom_state}" in auth_url
        assert state == custom_state
    
    
    @patch('requests.post')
    def test_authenticate_with_client_credentials(self, mock_post):
        """Test client credentials authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = AUTH_SUCCESS_RESPONSE
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.authenticate_with_client_credentials()
        
        assert result == AUTH_SUCCESS_RESPONSE
        assert client.access_token == AUTH_SUCCESS_RESPONSE["access_token"]
        
        # Verify the request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "client_credentials"
        assert call_args[1]["data"]["client_id"] == "test_id"
        assert call_args[1]["data"]["client_secret"] == "test_secret"
    
    @patch('requests.post')
    def test_authenticate_with_authorization_code(self, mock_post):
        """Test authorization code authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = AUTH_SUCCESS_RESPONSE
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com",
            redirect_uri="http://localhost:5001/callback"
        )
        
        result = client.authenticate_with_authorization_code("auth_code_123")
        
        assert result == AUTH_SUCCESS_RESPONSE
        assert client.access_token == AUTH_SUCCESS_RESPONSE["access_token"]
        assert client.refresh_token == AUTH_SUCCESS_RESPONSE["refresh_token"]
        
        # Verify the request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "authorization_code"
        assert call_args[1]["data"]["code"] == "auth_code_123"
        assert call_args[1]["data"]["redirect_uri"] == "http://localhost:5001/callback"
    
    @patch('requests.post')
    def test_refresh_access_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = AUTH_SUCCESS_RESPONSE
        mock_post.return_value = mock_response
        
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.refresh_token = "old_refresh_token"
        
        result = client.refresh_access_token()
        
        assert result == AUTH_SUCCESS_RESPONSE
        assert client.access_token == AUTH_SUCCESS_RESPONSE["access_token"]
        assert client.refresh_token == AUTH_SUCCESS_RESPONSE["refresh_token"]
        
        # Verify the request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "refresh_token"
        assert call_args[1]["data"]["refresh_token"] == "old_refresh_token"
    
    def test_refresh_access_token_no_refresh_token(self):
        """Test token refresh without refresh token."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.refresh_access_token()
        
        assert "No refresh token available" in str(exc_info.value)
    
    def test_is_token_valid_no_token(self):
        """Test token validity check with no token."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        
        assert client.is_token_valid() is False
    
    def test_is_token_valid_no_expiry(self):
        """Test token validity with no expiry time."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.access_token = "test_token"
        client.token_expires_at = None
        
        assert client.is_token_valid() is True
    
    def test_is_token_valid_not_expired(self):
        """Test token validity with valid expiry."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.access_token = "test_token"
        client.token_expires_at = datetime.now() + timedelta(hours=1)
        
        assert client.is_token_valid() is True
    
    def test_is_token_valid_expired(self):
        """Test token validity with expired token."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.access_token = "test_token"
        client.token_expires_at = datetime.now() - timedelta(hours=1)
        
        assert client.is_token_valid() is False
    
    def test_get_authorization_header_with_token(self):
        """Test authorization header generation with token."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.access_token = "test_token_123"
        client.token_expires_at = datetime.now() + timedelta(hours=1)
        
        headers = client.get_authorization_header()
        
        assert headers == {"Authorization": "Bearer test_token_123"}
    
    def test_get_authorization_header_no_token(self):
        """Test authorization header without token."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.get_authorization_header()
        
        assert "No valid access token" in str(exc_info.value)
    
    def test_get_token_info(self):
        """Test getting token information."""
        client = OAuth2Client(
            client_id="test_id",
            client_secret="test_secret",
            base_url="https://test.sellerlegend.com"
        )
        client.access_token = "test_token"
        client.refresh_token = "refresh_token"
        client.token_expires_at = datetime(2024, 1, 1, 12, 0, 0)
        
        info = client.get_token_info()
        
        assert info["has_access_token"] is True
        assert info["has_refresh_token"] is True
        assert info["is_valid"] is not None  # Will be True or False based on current time
        assert info["expires_at"] == "2024-01-01T12:00:00"