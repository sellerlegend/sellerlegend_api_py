"""
SellerLegend API Authentication Module

Handles OAuth2 authentication with Laravel Passport.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth2Session

from .exceptions import AuthenticationError


class OAuth2Client:
    """OAuth2 client for Laravel Passport authentication."""
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        base_url: str,
        redirect_uri: Optional[str] = None
    ):
        """
        Initialize OAuth2 client.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret  
            base_url: Base URL of the SellerLegend instance
            redirect_uri: Redirect URI for OAuth2 Authorization Code flow
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip('/')
        self.redirect_uri = redirect_uri or 'http://localhost:5001/callback'
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.state: Optional[str] = None
        
        # Laravel Passport OAuth2 endpoints
        self.token_url = urljoin(f"{self.base_url}/", "oauth/token")
        self.auth_url = urljoin(f"{self.base_url}/", "oauth/authorize")
    
    
    def get_authorization_url(self, state: Optional[str] = None, scope: str = "*") -> tuple[str, str]:
        """
        Get the authorization URL for OAuth2 Authorization Code flow.
        
        This is the URL where you redirect users to authenticate and authorize your app.
        
        Args:
            state: Optional state parameter for CSRF protection
            scope: OAuth2 scopes to request (default: "*" for all scopes)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        import secrets
        from urllib.parse import urlencode
        
        # Generate state if not provided (for CSRF protection)
        if state is None:
            state = secrets.token_urlsafe(32)
        
        self.state = state
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state
        }
        
        authorization_url = f"{self.auth_url}?{urlencode(params)}"
        
        return authorization_url, state
    
    def authenticate_with_authorization_code(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        This should be called after the user is redirected back to your application
        with an authorization code.
        
        Args:
            code: Authorization code received from the callback
            state: State parameter from the callback (for CSRF validation)
            
        Returns:
            Dict containing token information
            
        Raises:
            AuthenticationError: If authentication fails or state mismatch
        """
        # Validate state if it was set
        if self.state and state != self.state:
            raise AuthenticationError("State parameter mismatch - possible CSRF attack")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            
            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                raise AuthenticationError(
                    f"Token exchange failed: {error_data.get('error_description', response.text)}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            token_data = response.json()
            self._store_token_data(token_data)
            
            return token_data
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Token exchange request failed: {str(e)}")
    
    def authenticate_with_client_credentials(self) -> Dict[str, Any]:
        """
        Authenticate using Client Credentials Grant.
        
        Returns:
            Dict containing token information
            
        Raises:
            AuthenticationError: If authentication fails
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "*",
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            
            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                raise AuthenticationError(
                    f"Client credentials authentication failed: {error_data.get('error_description', response.text)}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            token_data = response.json()
            self._store_token_data(token_data)
            
            return token_data
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Client credentials authentication request failed: {str(e)}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Dict containing new token information
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            
            if response.status_code != 200:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                # Clear stored tokens if refresh fails
                self._clear_tokens()
                
                raise AuthenticationError(
                    f"Token refresh failed: {error_data.get('error_description', response.text)}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            token_data = response.json()
            self._store_token_data(token_data)
            
            return token_data
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Token refresh request failed: {str(e)}")
    
    def is_token_valid(self) -> bool:
        """
        Check if the current access token is valid and not expired.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.access_token:
            return False
            
        if not self.token_expires_at:
            return True  # No expiry info, assume valid
            
        # Add a 30-second buffer to prevent using a token that's about to expire
        return datetime.now() < (self.token_expires_at - timedelta(seconds=30))
    
    def ensure_valid_token(self) -> None:
        """
        Ensure we have a valid access token, refreshing if necessary.
        
        Raises:
            AuthenticationError: If no valid token can be obtained
        """
        if not self.is_token_valid():
            if self.refresh_token:
                self.refresh_access_token()
            else:
                raise AuthenticationError("No valid access token and no refresh token available")
    
    def get_authorization_header(self) -> Dict[str, str]:
        """
        Get the authorization header for API requests.
        
        Returns:
            Dict containing the Authorization header
            
        Raises:
            AuthenticationError: If no valid token is available
        """
        self.ensure_valid_token()
        
        if not self.access_token:
            raise AuthenticationError("No access token available")
        
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _store_token_data(self, token_data: Dict[str, Any]) -> None:
        """Store token data from OAuth2 response."""
        self.access_token = token_data.get("access_token")
        
        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]
        
        if "expires_in" in token_data:
            expires_in_seconds = int(token_data["expires_in"])
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
    
    def _clear_tokens(self) -> None:
        """Clear all stored token data."""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get current token information.
        
        Returns:
            Dict containing token status and expiry information
        """
        return {
            "has_access_token": bool(self.access_token),
            "has_refresh_token": bool(self.refresh_token),
            "expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "is_valid": self.is_token_valid(),
            "expires_in_seconds": (
                int((self.token_expires_at - datetime.now()).total_seconds())
                if self.token_expires_at else None
            )
        }
