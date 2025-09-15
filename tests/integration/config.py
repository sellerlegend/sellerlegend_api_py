"""
Configuration for integration tests

Set up your test credentials via .env file or environment variables.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class TestConfig:
    """Configuration for integration tests."""
    
    def __init__(self):
        """Initialize test configuration from .env file or environment variables."""
        # Load .env file from SDK root
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        # Initialize all configuration values
        self.base_url = None
        self.client_id = None
        self.client_secret = None
        self.access_token = None  # For direct token testing
        self.refresh_token = None  # For token refresh
        self.test_authorization_code = None  # For testing auth code exchange
        self.test_account_id = None
        self.test_marketplace_id = None
        self.test_seller_id = None
        self.test_sku = None
        self.test_asin = None
        
        # Load from environment (will include .env values)
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Support both old long names and new short names for backward compatibility
        self.base_url = os.getenv('SELLERLEGEND_BASE_URL') or os.getenv('SELLERLEGEND_TEST_BASE_URL') or 'https://app.sellerlegend.com'
        self.client_id = os.getenv('SELLERLEGEND_CLIENT_ID') or os.getenv('SELLERLEGEND_TEST_CLIENT_ID')
        self.client_secret = os.getenv('SELLERLEGEND_CLIENT_SECRET') or os.getenv('SELLERLEGEND_TEST_CLIENT_SECRET')
        self.access_token = os.getenv('SELLERLEGEND_ACCESS_TOKEN') or os.getenv('SELLERLEGEND_TEST_ACCESS_TOKEN')
        self.refresh_token = os.getenv('SELLERLEGEND_REFRESH_TOKEN') or os.getenv('SELLERLEGEND_TEST_REFRESH_TOKEN')
        self.test_authorization_code = os.getenv('SELLERLEGEND_AUTH_CODE') or os.getenv('SELLERLEGEND_TEST_AUTH_CODE')
        self.test_account_id = os.getenv('SELLERLEGEND_ACCOUNT_ID') or os.getenv('SELLERLEGEND_TEST_ACCOUNT_ID')
        self.test_marketplace_id = os.getenv('SELLERLEGEND_MARKETPLACE_ID') or os.getenv('SELLERLEGEND_TEST_MARKETPLACE_ID') or 'ATVPDKIKX0DER'
        self.test_seller_id = os.getenv('SELLERLEGEND_SELLER_ID') or os.getenv('SELLERLEGEND_TEST_SELLER_ID')
        self.test_sku = os.getenv('SELLERLEGEND_SKU') or os.getenv('SELLERLEGEND_TEST_SKU')
        self.test_asin = os.getenv('SELLERLEGEND_ASIN') or os.getenv('SELLERLEGEND_TEST_ASIN')
    
    
    def is_configured(self) -> bool:
        """Check if minimum required configuration is present."""
        # Need at least base_url and one of:
        # 1. Client ID + Secret for OAuth flows
        # 2. Access token for direct token use
        return bool(
            self.base_url and 
            (
                (self.client_id and self.client_secret) or
                self.access_token
            )
        )
    
    def get_auth_config(self) -> Dict[str, str]:
        """Get authentication configuration."""
        config = {'base_url': self.base_url}
        
        if self.client_id and self.client_secret:
            config['client_id'] = self.client_id
            config['client_secret'] = self.client_secret
        
        if self.access_token:
            config['access_token'] = self.access_token
            
        return config
    
    def get_authenticated_client(self):
        """Get an authenticated client using available credentials."""
        from sellerlegend_api import SellerLegendClient
        from sellerlegend_api.exceptions import AuthenticationError
        
        # If we have a direct access token, use it (preferred)
        if self.access_token:
            client = SellerLegendClient(
                access_token=self.access_token,
                base_url=self.base_url
            )
            
            # If we also have refresh token, set it for automatic refresh
            if hasattr(self, 'refresh_token') and self.refresh_token:
                client._oauth_client.refresh_token = self.refresh_token
                # Also set client credentials for refresh to work
                if self.client_id and self.client_secret:
                    client._oauth_client.client_id = self.client_id
                    client._oauth_client.client_secret = self.client_secret
            
            return client
        
        # Otherwise, try OAuth flows
        if not (self.client_id and self.client_secret):
            raise ValueError("No authentication method available")
        
        client = SellerLegendClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            base_url=self.base_url
        )
        
        # Try client credentials grant
        try:
            client.authenticate_client_credentials()
            return client
        except AuthenticationError:
            pass
        
        raise ValueError(
            "Could not authenticate with available credentials. "
            "Client credentials grant failed. "
            "Consider using authorization code flow or providing a valid access token."
        )
    
    def ensure_configured(self):
        """Ensure configuration exists and tokens are valid."""
        # If not configured, provide helpful message
        if not self.is_configured():
            import pytest
            pytest.skip(
                "Integration tests not configured. "
                "Run 'python setup_test_config.py' to create .env file and setup OAuth."
            )
        
        # Configuration exists, but let's verify tokens are still valid
        from sellerlegend_api import SellerLegendClient
        from sellerlegend_api.exceptions import AuthenticationError
        
        if self.access_token:
            try:
                client = SellerLegendClient(
                    access_token=self.access_token,
                    base_url=self.base_url
                )
                # Quick test to see if token is valid
                client.user.get_me()
            except AuthenticationError:
                # Token is expired, need manual refresh
                print("\nWarning: Access token may be expired. Tests might fail.")
                print("Please run 'python setup_test_config.py' to refresh tokens")
    
    def skip_if_not_configured(self):
        """Skip test if not properly configured."""
        import pytest
        if not self.is_configured():
            pytest.skip(
                "Integration tests not configured. "
                "Set environment variables or create test_config.json. "
                "See tests/integration/test_config.json.example for format."
            )


# Global test configuration instance
test_config = TestConfig()
