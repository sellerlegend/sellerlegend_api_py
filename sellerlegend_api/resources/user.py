"""
SellerLegend API User Resource Client

Handles user-related API endpoints including user information and account management.
"""

from typing import Dict, Any, List
from ..base import BaseClient


class UserClient:
    """Client for user-related API endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """
        Initialize user client.
        
        Args:
            base_client: Base API client instance
        """
        self.client = base_client
    
    def get_me(self) -> Dict[str, Any]:
        """
        Get current user information.
        
        Returns:
            Dict containing user information including id, name, email, status, and active status
        
        Example:
            {
                "status": "Success",
                "code": 200,
                "message": "User",
                "path": "api/user",
                "user": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "status": "active",
                    "active": true
                }
            }
        """
        return self.client.get("user/me")
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        Get list of accounts associated with the current user.
        
        Returns:
            Dict containing accounts list with marketplace and seller information
        
        Example:
            {
                "status": "Success",
                "code": 200,
                "message": "Accounts List",
                "path": "api/user/accounts",
                "accounts": [
                    {
                        "id": 456,
                        "account_title": "My Store",
                        "country_code": "US",
                        "currency_code": "USD",
                        "timezone": "America/New_York",
                        "marketplace": "ATVPDKIKX0DER",
                        "seller_id": "A1SELLER123"
                    }
                ]
            }
        """
        return self.client.get("user/accounts")