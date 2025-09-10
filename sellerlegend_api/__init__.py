"""
SellerLegend API Python SDK

This package provides a comprehensive Python interface to the SellerLegend API,
enabling developers to integrate SellerLegend functionality into their applications.

Example:
    from sellerlegend_api import SellerLegendClient
    
    client = SellerLegendClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        base_url="https://your-instance.sellerlegend.com"
    )
    
    # Authenticate with client credentials
    client.authenticate_client_credentials()
    
    # Get user info
    user_info = client.user.get_me()
"""

from .client import SellerLegendClient
from .exceptions import (
    SellerLegendAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError
)

__version__ = "1.0.0"
__author__ = "SellerLegend"
__email__ = "support@sellerlegend.com"

__all__ = [
    "SellerLegendClient",
    "SellerLegendAPIError",
    "AuthenticationError", 
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError"
]