"""
Configuration for integration tests

Set up your test credentials here or via environment variables.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class TestConfig:
    """Configuration for integration tests."""
    
    def __init__(self):
        """Initialize test configuration from environment or config file."""
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
        
        # Try to load from environment variables first
        # self._load_from_env()
        
        # If not found in env, try to load from config file
        if not self.is_configured():
            self._load_from_file()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.base_url = os.getenv('SELLERLEGEND_TEST_BASE_URL', 'https://app.sellerlegend.com')
        self.client_id = os.getenv('SELLERLEGEND_TEST_CLIENT_ID')
        self.client_secret = os.getenv('SELLERLEGEND_TEST_CLIENT_SECRET')
        self.access_token = os.getenv('SELLERLEGEND_TEST_ACCESS_TOKEN')
        self.refresh_token = os.getenv('SELLERLEGEND_TEST_REFRESH_TOKEN')
        self.test_authorization_code = os.getenv('SELLERLEGEND_TEST_AUTH_CODE')
        self.test_account_id = os.getenv('SELLERLEGEND_TEST_ACCOUNT_ID')
        self.test_marketplace_id = os.getenv('SELLERLEGEND_TEST_MARKETPLACE_ID', 'ATVPDKIKX0DER')
        self.test_seller_id = os.getenv('SELLERLEGEND_TEST_SELLER_ID')
        self.test_sku = os.getenv('SELLERLEGEND_TEST_SKU')
        self.test_asin = os.getenv('SELLERLEGEND_TEST_ASIN')
    
    def _load_from_file(self):
        """Load configuration from test_config.json file."""
        config_file = Path(__file__).parent / 'test_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.base_url = config.get('base_url', self.base_url)
                self.client_id = config.get('client_id', self.client_id)
                self.client_secret = config.get('client_secret', self.client_secret)
                self.access_token = config.get('access_token', self.access_token)
                self.refresh_token = config.get('refresh_token', self.refresh_token)
                self.test_authorization_code = config.get('test_authorization_code', self.test_authorization_code)
                self.test_account_id = config.get('test_account_id', self.test_account_id)
                self.test_marketplace_id = config.get('test_marketplace_id', self.test_marketplace_id)
                self.test_seller_id = config.get('test_seller_id', self.test_seller_id)
                self.test_sku = config.get('test_sku', self.test_sku)
                self.test_asin = config.get('test_asin', self.test_asin)
    
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
        """Ensure configuration exists and tokens are valid, creating/refreshing as needed."""
        from .setup_config_improved import setup_or_refresh_config
        
        # If not configured, run setup
        if not self.is_configured():
            print("\nConfiguration not found or incomplete. Starting setup...")
            config = setup_or_refresh_config()
            
            # Update our config with the new values
            self.base_url = config.get('base_url', self.base_url)
            self.client_id = config.get('client_id', self.client_id)
            self.client_secret = config.get('client_secret', self.client_secret)
            self.access_token = config.get('access_token', self.access_token)
            self.refresh_token = config.get('refresh_token', self.refresh_token)
            self.test_authorization_code = config.get('test_authorization_code', self.test_authorization_code)
            self.test_account_id = config.get('test_account_id', self.test_account_id)
            self.test_marketplace_id = config.get('test_marketplace_id', self.test_marketplace_id)
            self.test_seller_id = config.get('test_seller_id', self.test_seller_id)
            self.test_sku = config.get('test_sku', self.test_sku)
            self.test_asin = config.get('test_asin', self.test_asin)
        else:
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
                    # Token is expired, try to refresh or re-authenticate
                    print("\nAccess token expired. Refreshing...")
                    config = setup_or_refresh_config()
                    
                    # Update tokens
                    self.access_token = config.get('access_token', self.access_token)
                    self.refresh_token = config.get('refresh_token', self.refresh_token)
    
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
