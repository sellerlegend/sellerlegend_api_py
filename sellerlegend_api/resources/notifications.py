"""
SellerLegend API Notifications Resource Client

Handles notification endpoints.
"""

from typing import Dict, Any, Optional
from ..base import BaseClient
from ..validators import clean_params, ValidationError


class NotificationsClient:
    """Client for notification endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize notifications client."""
        self.client = base_client
    
    def get_list(
        self,
        notification_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get notifications list.
        
        Args:
            notification_type: Type of notifications to retrieve (required)
            
        Returns:
            Notifications data
        """
        if not notification_type:
            raise ValidationError("notification_type is required")
            
        params = {
            "notification_type": notification_type,
        }
        params.update(kwargs)
        
        params = clean_params(params)
        
        return self.client.get("notifications/list", params=params)
