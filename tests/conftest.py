"""
Test configuration and fixtures for pytest
"""

import pytest
from unittest.mock import Mock, patch
from sellerlegend_api import SellerLegendClient
from tests.fixtures.responses import AUTH_SUCCESS_RESPONSE


@pytest.fixture
def base_url():
    """Test base URL."""
    return "https://test.sellerlegend.com"


@pytest.fixture
def client_credentials():
    """Test OAuth2 credentials."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret"
    }


@pytest.fixture
def access_token():
    """Test access token."""
    return "test_access_token_12345"


@pytest.fixture
def client(base_url, client_credentials):
    """Create a test client instance."""
    return SellerLegendClient(
        client_id=client_credentials["client_id"],
        client_secret=client_credentials["client_secret"],
        base_url=base_url
    )


@pytest.fixture
def authenticated_client(client, access_token):
    """Create an authenticated test client."""
    client.set_access_token(access_token, expires_in=3600)
    return client


@pytest.fixture
def mock_requests():
    """Mock requests library for API calls."""
    with patch('sellerlegend_api.base.requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.post.return_value = mock_response
        mock_session_instance.put.return_value = mock_response
        mock_session_instance.patch.return_value = mock_response
        mock_session_instance.delete.return_value = mock_response
        
        mock_session.return_value = mock_session_instance
        yield mock_session_instance


@pytest.fixture
def mock_auth_response():
    """Mock successful authentication response."""
    return AUTH_SUCCESS_RESPONSE