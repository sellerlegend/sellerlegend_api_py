"""
SellerLegend API Main Client

Main client class that provides access to all API resources.
"""

from typing import Optional, Dict, Any, Union
from .auth import OAuth2Client
from .base import BaseClient
from .resources.user import UserClient
from .resources.sales import SalesClient
from .resources.reports import ReportsClient
from .resources.inventory import InventoryClient
from .resources.costs import CostsClient
from .resources.connections import ConnectionsClient
from .resources.supply_chain import SupplyChainClient
from .resources.warehouse import WarehouseClient
from .resources.notifications import NotificationsClient


class SellerLegendClient:
    """
    Main SellerLegend API client.
    
    This is the primary interface for interacting with the SellerLegend API.
    It handles authentication and provides access to all API resources.
    
    Example:
        # Initialize client
        client = SellerLegendClient(
            client_id="your_oauth_client_id",
            client_secret="your_oauth_client_secret", 
            base_url="https://your-instance.sellerlegend.com"
        )
        
        # Authenticate with client credentials
        client.authenticate_client_credentials()
        
        # Or use authorization code flow
        auth_url, state = client.get_authorization_url()
        # ... redirect user to auth_url ...
        # ... user authorizes and you get a code ...
        client.authenticate_with_code(code)
        
        # Use API resources
        user_info = client.user.get_me()
        accounts = client.user.get_accounts()
        orders = client.sales.get_orders(per_page=500)
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = None,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """
        Initialize the SellerLegend API client.
        
        Args:
            client_id: OAuth2 client ID from SellerLegend (optional if using access_token)
            client_secret: OAuth2 client secret from SellerLegend (optional if using access_token)
            base_url: Base URL of your SellerLegend instance (e.g., "https://app.sellerlegend.com")
            redirect_uri: Redirect URI for OAuth2 flow (optional, for authorization code flow)
            access_token: Existing access token to use (optional, bypasses OAuth2 flow)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_factor: Backoff factor for retries (default: 0.3)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip('/') if base_url else None
        self.access_token = access_token
        
        # Initialize OAuth2 client if credentials provided
        if client_id and client_secret and base_url:
            self._oauth_client = OAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
                base_url=self.base_url,
                redirect_uri=redirect_uri
            )
        else:
            # Create a minimal OAuth2 client with just the access token
            self._oauth_client = OAuth2Client(
                client_id='',
                client_secret='',
                base_url=self.base_url or 'https://api.sellerlegend.com'
            )

        # Set the access token directly if provided
        if access_token:
            self._oauth_client.access_token = access_token
            self._oauth_client.token_expires_at = None  # No expiry info for external tokens

        if refresh_token:
            self._oauth_client.refresh_token = refresh_token
        
        # Initialize base API client
        self._base_client = BaseClient(
            auth_client=self._oauth_client,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )
        
        # Initialize resource clients
        self.user = UserClient(self._base_client)
        self.sales = SalesClient(self._base_client)
        self.reports = ReportsClient(self._base_client)
        self.inventory = InventoryClient(self._base_client)
        self.costs = CostsClient(self._base_client)
        self.connections = ConnectionsClient(self._base_client)
        self.supply_chain = SupplyChainClient(self._base_client)
        self.warehouse = WarehouseClient(self._base_client)
        self.notifications = NotificationsClient(self._base_client)
    
    
    def authenticate_client_credentials(self) -> Dict[str, Any]:
        """
        Authenticate using client credentials (Client Credentials Grant).
        
        This method is useful for server-to-server authentication where
        no user interaction is required.
        
        Returns:
            Dict containing token information
            
        Raises:
            AuthenticationError: If authentication fails
        """
        return self._oauth_client.authenticate_with_client_credentials()
    
    def get_authorization_url(self, state: Optional[str] = None, scope: str = "*") -> tuple[str, str]:
        """
        Get the authorization URL for OAuth2 Authorization Code flow.
        
        This returns the URL where you should redirect users to authenticate
        and authorize your application.
        
        Args:
            state: Optional state parameter for CSRF protection
            scope: OAuth2 scopes to request (default: "*" for all scopes)
            
        Returns:
            Tuple of (authorization_url, state)
            
        Example:
            auth_url, state = client.get_authorization_url()
            # Redirect user to auth_url
            # Save state for validation when handling callback
        """
        return self._oauth_client.get_authorization_url(state, scope)
    
    def authenticate_with_code(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        This should be called after the user is redirected back to your application
        from the authorization server with an authorization code.
        
        Args:
            code: Authorization code received from the callback URL
            state: State parameter from the callback (for CSRF validation)
            
        Returns:
            Dict containing token information
            
        Raises:
            AuthenticationError: If authentication fails or state mismatch
            
        Example:
            # In your callback handler:
            code = request.args.get('code')
            state = request.args.get('state')
            token_info = client.authenticate_with_code(code, state)
        """
        return self._oauth_client.authenticate_with_authorization_code(code, state)
    
    def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh the current access token using the refresh token.
        
        Returns:
            Dict containing new token information
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        return self._oauth_client.refresh_access_token()
    
    def set_access_token(self, access_token: str, expires_in: Optional[int] = None) -> None:
        """
        Set an access token directly (useful when token is obtained externally).
        
        Args:
            access_token: The access token to use
            expires_in: Optional token expiry time in seconds
        """
        from datetime import datetime, timedelta
        self._oauth_client.access_token = access_token
        if expires_in:
            self._oauth_client.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        else:
            self._oauth_client.token_expires_at = None
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current authentication token.
        
        Returns:
            Dict containing token status and expiry information
        """
        return self._oauth_client.get_token_info()
    
    def is_authenticated(self) -> bool:
        """
        Check if the client is currently authenticated with a valid token.
        
        Returns:
            True if authenticated with a valid token, False otherwise
        """
        return self._oauth_client.is_token_valid()
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Check the API service status.
        
        Returns:
            Service status information
        """
        return self._base_client.get_service_status()
    
    # Convenience methods for common operations
    
    def get_user_accounts(self) -> Dict[str, Any]:
        """
        Convenience method to get user accounts.
        
        Returns:
            User accounts information
        """
        return self.user.get_accounts()
    
    def get_recent_orders(
        self, 
        days: int = 30,
        per_page: int = 500
    ) -> Dict[str, Any]:
        """
        Convenience method to get recent orders.
        
        Args:
            days: Number of days to look back (default: 30)
            per_page: Number of records per page (default: 500)
            
        Returns:
            Recent orders data
        """
        from datetime import datetime, timedelta
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        return self.sales.get_orders(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            per_page=per_page
        )
    
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup if needed."""
        # Close session if needed
        if hasattr(self._base_client, 'session'):
            self._base_client.session.close()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        auth_status = "authenticated" if self.is_authenticated() else "not authenticated"
        return f"SellerLegendClient(base_url='{self.base_url}', {auth_status})"