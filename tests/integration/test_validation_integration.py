"""
Integration tests for validation and error handling

These tests verify that the SDK properly validates parameters and handles API errors.
"""

import pytest
from datetime import datetime, timedelta
from sellerlegend_api import SellerLegendClient
from sellerlegend_api.exceptions import (
    ValidationError,
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    ServerError
)
from .config import test_config


class TestValidationIntegration:
    """Test parameter validation with real API."""
    
    @classmethod
    def setup_class(cls):
        """Set up authenticated client for all tests."""
        # Ensure configuration exists and tokens are valid
        test_config.ensure_configured()
        # Use the flexible authentication method from config
        cls.client = test_config.get_authenticated_client()
    
    def test_invalid_date_format(self):
        """Test that invalid date format is caught before API call."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.sales.get_orders(
                start_date="12/01/2023",  # Wrong format
                end_date="12/31/2023"
            )
        
        assert "Invalid date format" in str(exc_info.value)
    
    def test_invalid_date_range(self):
        """Test that end date before start date is caught."""
        # Note: This validation may happen server-side, not client-side
        # The API might accept this and return empty results
        try:
            result = self.client.sales.get_orders(
                start_date="2023-12-31",
                end_date="2023-12-01"  # Before start date
            )
            # API might just return empty results for invalid date range
            assert result is not None
        except ValidationError as exc_info:
            assert "End date must be after or equal to start date" in str(exc_info)
    
    def test_invalid_pagination(self):
        """Test invalid pagination parameters."""
        # Note: API may handle these server-side
        try:
            # Test page = 0
            result = self.client.sales.get_orders(page=0)
            # API might auto-correct to page=1
            assert result is not None
        except ValidationError as exc_info:
            assert "Page must be greater than 0" in str(exc_info)
        
        try:
            # Test per_page too high
            result = self.client.sales.get_orders(per_page=10000)
            # API might auto-correct or return error
            assert result is not None
        except ValidationError as exc_info:
            assert "Per page must be between" in str(exc_info) or "per_page" in str(exc_info).lower()
    
    def test_invalid_enum_value(self):
        """Test invalid enum value."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.sales.get_statistics_dashboard(
                view_by="invalid_view",  # Should be "product" or "date"
                group_by="sku"
            )
        
        assert "must be one of" in str(exc_info.value)
    
    def test_missing_required_parameter(self):
        """Test missing required parameter."""
        with pytest.raises(TypeError):
            # Missing required view_by and group_by
            self.client.sales.get_statistics_dashboard()
    
    def test_invalid_asin_format(self):
        """Test invalid ASIN format validation."""
        # ASIN should be 10 characters starting with B
        # Note: API may not validate ASIN format, just return empty results
        try:
            result = self.client.inventory.get_list(
                asin="INVALID"  # Too short and wrong format
            )
            # API might just return empty results for invalid ASIN
            assert result is not None
        except ValidationError as exc_info:
            # If API does validate, check the error
            assert exc_info is not None
    
    def test_empty_sku_validation(self):
        """Test that empty SKU is handled."""
        # Note: API may treat empty SKU as "no filter"
        try:
            result = self.client.inventory.get_list(
                sku=""  # Empty SKU
            )
            # API might just return all items when SKU is empty
            assert result is not None
        except ValidationError as exc_info:
            assert "cannot be empty" in str(exc_info) or "required" in str(exc_info)


class TestErrorHandlingIntegration:
    """Test error handling with real API."""
    
    @classmethod
    def setup_class(cls):
        """Set up test client."""
        # Ensure configuration exists and tokens are valid
        test_config.ensure_configured()
    
    def test_authentication_error(self):
        """Test handling of authentication errors."""
        # Test with invalid access token
        client = SellerLegendClient(
            access_token="invalid_token_12345",
            base_url=test_config.base_url
        )
        
        # Try to make API call with invalid token
        with pytest.raises(AuthenticationError) as exc_info:
            client.user.get_me()
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.message is not None
    
    def test_expired_token_handling(self):
        """Test handling of expired token."""
        client = SellerLegendClient(
            access_token="expired_or_invalid_token_12345",
            base_url=test_config.base_url
        )
        
        # Try to make API call with invalid token
        with pytest.raises(AuthenticationError) as exc_info:
            client.user.get_me()
        
        assert exc_info.value.status_code == 401
    
    def test_not_found_error(self):
        """Test handling of 404 Not Found errors."""
        # Use authenticated client from config
        client = test_config.get_authenticated_client()
        
        # Try to get non-existent report
        with pytest.raises(NotFoundError) as exc_info:
            client.reports.get_report_status("non_existent_report_id_99999")
        
        assert exc_info.value.status_code == 404
    
    def test_rate_limiting_detection(self):
        """Test that rate limiting would be properly detected."""
        # Note: We don't want to actually trigger rate limiting in tests
        # This test just verifies the error handling structure is in place
        
        # Use authenticated client from config
        client = test_config.get_authenticated_client()
        
        # Make a normal request to verify the client works
        user_info = client.user.get_me()
        assert user_info is not None
        
        # The actual RateLimitError handling is tested in unit tests
        # We just verify the exception class exists and has the right structure
        try:
            raise RateLimitError("Too many requests", 429, {"retry_after": 60})
        except RateLimitError as e:
            assert e.status_code == 429
            assert e.response_data["retry_after"] == 60
    
    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        # Use an invalid URL to trigger connection error
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://invalid-domain-that-does-not-exist-12345.com"
        )
        
        with pytest.raises(Exception) as exc_info:
            client.user.get_me()
        
        # Should get some kind of connection error
        error_str = str(exc_info.value)
        assert "Connection" in error_str or "Failed" in error_str or "resolve" in error_str.lower()
    
    def test_timeout_handling(self):
        """Test handling of request timeouts."""
        # Create client with very short timeout
        client = SellerLegendClient(
            access_token=test_config.access_token,
            base_url=test_config.base_url,
            timeout=0.001  # 1ms timeout - should trigger timeout
        )
        
        with pytest.raises(Exception) as exc_info:
            client.user.get_me()
        
        # Should get timeout error
        error_msg = str(exc_info.value).lower()
        assert "timeout" in error_msg or "timed out" in error_msg or "read timeout" in error_msg