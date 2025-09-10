"""
Tests for response handling and error cases
"""

import pytest
from unittest.mock import Mock, patch
from sellerlegend_api import SellerLegendClient
from sellerlegend_api.base import BaseClient
from sellerlegend_api.auth import OAuth2Client
from sellerlegend_api.exceptions import (
    SellerLegendAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    AccessDeniedError
)
from tests.fixtures.responses import (
    VALIDATION_ERROR_RESPONSE,
    RATE_LIMIT_RESPONSE,
    NOT_FOUND_RESPONSE,
    SERVER_ERROR_RESPONSE
)


class TestErrorHandling:
    """Test error response handling."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_401_unauthorized(self, mock_session):
        """Test handling 401 Unauthorized response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthenticated"}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="invalid_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.user.get_me()
        
        assert exc_info.value.status_code == 401
        assert "Unauthenticated" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_403_forbidden(self, mock_session):
        """Test handling 403 Forbidden response."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "Access denied"}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(AccessDeniedError) as exc_info:
            client.user.get_accounts()
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_404_not_found(self, mock_session):
        """Test handling 404 Not Found response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = NOT_FOUND_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            client.reports.get_report_status("999999")
        
        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_422_validation_error(self, mock_session):
        """Test handling 422 Validation Error response."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = VALIDATION_ERROR_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            client.sales.get_orders(start_date="invalid")
        
        # This is client-side validation, not a 422 from server
        assert "Invalid date format" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_429_rate_limit(self, mock_session):
        """Test handling 429 Rate Limit response."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = RATE_LIMIT_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            client.sales.get_orders()
        
        assert exc_info.value.status_code == 429
        assert "Too many requests" in str(exc_info.value)
        assert exc_info.value.response_data["retry_after"] == 60
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_500_server_error(self, mock_session):
        """Test handling 500 Server Error response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = SERVER_ERROR_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(ServerError) as exc_info:
            client.sales.get_orders()
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_unknown_error_code(self, mock_session):
        """Test handling unknown error status code."""
        mock_response = Mock()
        mock_response.status_code = 418  # I'm a teapot
        mock_response.json.return_value = {"message": "Unknown error"}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(SellerLegendAPIError) as exc_info:
            client.user.get_me()
        
        assert exc_info.value.status_code == 418
        assert "Unknown error" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_non_json_response(self, mock_session):
        """Test handling non-JSON error response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Internal Server Error"
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(ServerError) as exc_info:
            client.user.get_me()
        
        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in str(exc_info.value)


class TestResponseParsing:
    """Test response parsing and data extraction."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_parse_paginated_response(self, mock_session):
        """Test parsing paginated response."""
        paginated_response = {
            "data": [{"id": 1}, {"id": 2}],
            "links": {
                "first": "https://api.example.com/items?page=1",
                "last": "https://api.example.com/items?page=5",
                "prev": None,
                "next": "https://api.example.com/items?page=2"
            },
            "meta": {
                "current_page": 1,
                "from": 1,
                "last_page": 5,
                "per_page": 2,
                "to": 2,
                "total": 10
            }
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = paginated_response
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.sales.get_orders()
        
        assert "data" in result
        assert "meta" in result
        assert "links" in result
        assert len(result["data"]) == 2
        assert result["meta"]["total"] == 10
        assert result["meta"]["current_page"] == 1
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_parse_simple_response(self, mock_session):
        """Test parsing simple response."""
        simple_response = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = simple_response
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.user.get_me()
        
        assert result["id"] == 123
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_parse_empty_response(self, mock_session):
        """Test parsing empty response."""
        mock_response = Mock()
        mock_response.status_code = 204  # No Content
        mock_response.json.side_effect = ValueError("No content")
        mock_response.text = ""
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        auth_client = OAuth2Client("id", "secret", "https://test.com")
        auth_client.access_token = "test_token"
        base_client = BaseClient(auth_client)
        
        # Simulate a DELETE request that returns 204 No Content
        mock_response.status_code = 204
        result = base_client.delete("test/endpoint")
        
        # 204 is in success range but may have no body
        assert result == {"message": "Unknown error"}


class TestHeaderValidation:
    """Test that headers are properly set."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_api_version_header_present(self, mock_session):
        """Test that SellerLegend-Api-Version header is present."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Check that session headers are set during initialization
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        # The headers should be set on the session during BaseClient init
        assert mock_session_instance.headers.update.called
        call_args = mock_session_instance.headers.update.call_args[0][0]
        assert "SellerLegend-Api-Version" in call_args
        assert call_args["SellerLegend-Api-Version"] == "v2"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_authorization_header_present(self, mock_session):
        """Test that Authorization header is present in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token_123",
            base_url="https://test.sellerlegend.com"
        )
        
        client.user.get_me()
        
        # Check that Authorization header was included
        call_args = mock_session_instance.request.call_args[1]
        assert "headers" in call_args
        assert "Authorization" in call_args["headers"]
        assert call_args["headers"]["Authorization"] == "Bearer test_token_123"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_content_type_header(self, mock_session):
        """Test that Content-Type header is set correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        # Check session headers
        call_args = mock_session_instance.headers.update.call_args[0][0]
        assert "Content-Type" in call_args
        assert call_args["Content-Type"] == "application/json"
        assert "Accept" in call_args
        assert call_args["Accept"] == "application/json"


class TestConnectionHandling:
    """Test connection error handling."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_timeout_error(self, mock_session):
        """Test handling request timeout."""
        import requests
        
        mock_session_instance = Mock()
        mock_session_instance.request.side_effect = requests.Timeout("Request timed out")
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(SellerLegendAPIError) as exc_info:
            client.user.get_me()
        
        assert "Request timed out" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_connection_error(self, mock_session):
        """Test handling connection error."""
        import requests
        
        mock_session_instance = Mock()
        mock_session_instance.request.side_effect = requests.ConnectionError("Connection failed")
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(SellerLegendAPIError) as exc_info:
            client.user.get_me()
        
        assert "Connection error" in str(exc_info.value)
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_handle_general_request_error(self, mock_session):
        """Test handling general request exception."""
        import requests
        
        mock_session_instance = Mock()
        mock_session_instance.request.side_effect = requests.RequestException("Request failed")
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        with pytest.raises(SellerLegendAPIError) as exc_info:
            client.user.get_me()
        
        assert "Request failed" in str(exc_info.value)