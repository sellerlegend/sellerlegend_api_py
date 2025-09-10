"""
SellerLegend API Connections Resource Client

Handles Amazon connection status endpoints.
"""

from typing import Dict, Any, Optional
from ..base import BaseClient
from ..validators import validate_account_params, clean_params


class ConnectionsClient:
    """Client for connection status endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize connections client."""
        self.client = base_client
    
    def get_list(
        self,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get Amazon connection status.
        
        Args:
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Connection status information
        """
        params = {
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("connections/list", params=params)
