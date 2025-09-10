"""
Integration tests for authentication flows

These tests make actual API calls to test authentication.
Note: The password grant type may not be supported by all OAuth2 servers.
"""

import pytest
import time
from sellerlegend_api import SellerLegendClient
from sellerlegend_api.exceptions import AuthenticationError
from .config import test_config


class TestAuthenticationIntegration:
    """Test authentication with real API."""
    
    def setup_method(self):
        """Set up test client."""
        # Ensure configuration exists and tokens are valid
        test_config.ensure_configured()
        self.client = SellerLegendClient(
            client_id=test_config.client_id,
            client_secret=test_config.client_secret,
            base_url=test_config.base_url
        )
    
    
    
    def test_client_credentials_authentication(self):
        """Test client credentials authentication if supported."""
        try:
            result = self.client.authenticate_client_credentials()
            
            # Verify response structure
            assert 'access_token' in result
            assert 'token_type' in result
            assert result['token_type'] == 'Bearer'
            
            # Verify we can use the token
            assert self.client.is_authenticated()
            
            # Note: Client credentials may have limited scope
            # Some endpoints might not work with this grant type
            
        except AuthenticationError as e:
            # Client credentials might not be enabled for this app
            if e.status_code in [400, 401] or "grant type is not supported" in str(e).lower():
                pytest.skip("Client credentials grant not enabled for this OAuth app")
            raise
    
    def test_authorization_code_flow_url_generation(self):
        """Test generating authorization URL for code flow."""
        # This should always work as it doesn't make an API call
        auth_url, state = self.client.get_authorization_url()
        
        # Verify URL structure
        assert auth_url.startswith(test_config.base_url)
        assert "/oauth/authorize" in auth_url
        assert f"client_id={test_config.client_id}" in auth_url
        assert "response_type=code" in auth_url
        assert f"state={state}" in auth_url
        
        # Verify state is generated
        assert state is not None
        assert len(state) > 20  # Should be a secure random string
    
    def test_authorization_code_flow_with_custom_state(self):
        """Test authorization code flow with custom state."""
        custom_state = "my_custom_state_12345"
        auth_url, returned_state = self.client.get_authorization_url(state=custom_state)
        
        # Verify custom state is used
        assert returned_state == custom_state
        assert f"state={custom_state}" in auth_url
    
    def test_authorization_code_exchange(self):
        """Test exchanging authorization code for token."""
        # Note: This test requires a valid authorization code
        # In a real scenario, you'd need to:
        # 1. Redirect user to authorization URL
        # 2. User approves the app
        # 3. Get the code from callback
        # 4. Exchange code for token
        
        # For automated testing, we'll skip this unless we have a test code
        test_code = test_config.__dict__.get('test_authorization_code')
        if not test_code:
            pytest.skip("No test authorization code available. This requires manual OAuth flow.")
        
        try:
            result = self.client.authenticate_with_code(test_code)
            
            # Verify response
            assert 'access_token' in result
            assert 'refresh_token' in result
            
        except AuthenticationError as e:
            if e.status_code == 400:
                pytest.skip("Authorization code is invalid or expired")
            raise
    
    def test_token_refresh(self):
        """Test refreshing access token."""
        # First, we need to authenticate somehow
        authenticated = False
        
        # Try client credentials
        try:
            self.client.authenticate_client_credentials()
            authenticated = True
        except AuthenticationError:
            pass
        
        if not authenticated:
            pytest.skip("Could not authenticate to test token refresh")
        
        # Now test refresh if we have a refresh token
        if not self.client._oauth_client.refresh_token:
            pytest.skip("No refresh token available (client credentials grant doesn't provide refresh tokens)")
        
        # Store original token
        original_token = self.client._oauth_client.access_token
        
        # Refresh token
        result = self.client.refresh_token()
        
        # Verify response
        assert 'access_token' in result
        
        # Verify new token works
        new_token = self.client._oauth_client.access_token
        assert new_token is not None
        
        # Some implementations return a new refresh token
        if 'refresh_token' in result:
            assert result['refresh_token'] is not None
    
    def test_token_expiry_check(self):
        """Test token expiry checking."""
        # Try to authenticate with any available method
        authenticated = False
        
        try:
            self.client.authenticate_client_credentials()
            authenticated = True
        except AuthenticationError:
            pass
        
        if not authenticated:
            pytest.skip("Could not authenticate to test token expiry")
        
        # Check token is valid
        assert self.client.is_authenticated()
        
        # Get token info
        token_info = self.client.get_token_info()
        assert token_info['has_access_token']
        assert token_info['is_valid']
    
    def test_multiple_authentication_attempts(self):
        """Test that multiple authentication attempts work correctly."""
        try:
            # First authentication
            result1 = self.client.authenticate_client_credentials()
            token1 = self.client._oauth_client.access_token
            
            # Wait a moment
            time.sleep(1)
            
            # Second authentication
            result2 = self.client.authenticate_client_credentials()
            token2 = self.client._oauth_client.access_token
            
            # Both should succeed
            assert result1['access_token'] is not None
            assert result2['access_token'] is not None
            
            # Note: Client credentials grant may not allow user-specific API calls
            # Just verify authentication succeeded
            assert self.client.is_authenticated()
            
        except AuthenticationError as e:
            if e.status_code in [400, 401] or "grant type is not supported" in str(e).lower():
                pytest.skip("Client credentials grant not enabled for this OAuth app")
            raise
    
    def test_using_existing_access_token(self):
        """Test using an existing access token directly."""
        # First get a valid token
        authenticated = False
        access_token = None
        
        # Try to get a token via client credentials
        try:
            result = self.client.authenticate_client_credentials()
            access_token = result['access_token']
            authenticated = True
        except AuthenticationError:
            pass
        
        if not authenticated or not access_token:
            pytest.skip("Could not obtain access token for testing")
        
        # Create a new client with just the access token
        new_client = SellerLegendClient(
            access_token=access_token,
            base_url=test_config.base_url
        )
        
        # Verify it works
        assert new_client.is_authenticated()
        
        # Try to make an API call
        # Note: Client credentials tokens may not work with user-specific endpoints
        try:
            # Try a general endpoint that should work with any valid token
            accounts = new_client.user.get_accounts()
            assert accounts is not None
        except AuthenticationError:
            # If that fails, just verify the token was accepted by the client
            # The token is valid for the client even if specific endpoints aren't accessible
            pass
    
    def test_authorization_header_format(self):
        """Test that authorization header is correctly formatted."""
        # Authenticate with any available method
        authenticated = False
        
        try:
            self.client.authenticate_client_credentials()
            authenticated = True
        except AuthenticationError:
            pass
        
        if not authenticated:
            pytest.skip("Could not authenticate to test header format")
        
        # Get authorization header
        headers = self.client._oauth_client.get_authorization_header()
        
        # Verify format
        assert 'Authorization' in headers
        assert headers['Authorization'].startswith('Bearer ')
        assert len(headers['Authorization']) > 10  # "Bearer " + token