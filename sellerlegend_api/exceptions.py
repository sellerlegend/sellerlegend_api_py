"""
SellerLegend API Exception Classes

This module defines custom exceptions for the SellerLegend API client.
"""

from typing import Optional, Dict, Any


class SellerLegendAPIError(Exception):
    """Base exception class for all SellerLegend API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            status_code: HTTP status code if available
            response_data: Full response data from the API if available
        """
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(SellerLegendAPIError):
    """Raised when authentication fails or token is invalid."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        """
        Initialize the authentication exception.

        Args:
            message: Error message
            status_code: HTTP status code if available
            response_data: Full response data from the API if available
            error_code: Specific error code (e.g., 'TOKEN_EXPIRED', 'TOKEN_EXPIRED_NO_REFRESH')
        """
        super().__init__(message, status_code, response_data)
        self.error_code = error_code


class ValidationError(SellerLegendAPIError):
    """Raised when request validation fails."""
    pass


class NotFoundError(SellerLegendAPIError):
    """Raised when a resource is not found (404)."""
    pass


class RateLimitError(SellerLegendAPIError):
    """Raised when rate limit is exceeded."""
    pass


class ServerError(SellerLegendAPIError):
    """Raised when server returns 5xx error."""
    pass


class AccessDeniedError(SellerLegendAPIError):
    """Raised when access is denied (403)."""
    pass