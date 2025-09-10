"""
SellerLegend API Inventory Resource Client

Handles inventory-related API endpoints.
"""

from typing import Dict, Any, Optional, Union, Literal
from datetime import datetime, date
from ..base import BaseClient
from ..validators import (
    validate_date, validate_filter_by, validate_account_params,
    clean_params, ValidationError
)


class InventoryClient:
    """Client for inventory-related API endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize inventory client."""
        self.client = base_client
    
    def get_list(
        self,
        per_page: int = 500,
        velocity_start_date: Optional[Union[str, date, datetime]] = None,
        velocity_end_date: Optional[Union[str, date, datetime]] = None,
        filter_by: Optional[Literal["sku", "asin", "parent_asin"]] = None,
        filter_value: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get inventory list with velocity calculations.
        
        Args:
            per_page: Number of items per page (500, 1000, 2000)
            velocity_start_date: Start date for velocity calculation
            velocity_end_date: End date for velocity calculation
            filter_by: Filter field ("sku", "asin", "parent_asin")
            filter_value: Value to filter by
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Inventory data with velocity metrics
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate dates
        velocity_start_date = validate_date(velocity_start_date, "velocity_start_date")
        velocity_end_date = validate_date(velocity_end_date, "velocity_end_date")
        
        # Validate filter
        filter_by = validate_filter_by(filter_by)
        if filter_by and not filter_value:
            raise ValidationError("filter_value is required when filter_by is specified")
        
        params = {
            "per_page": per_page,
            "velocity_start_date": velocity_start_date,
            "velocity_end_date": velocity_end_date,
            "filter_by": filter_by,
            "filter_value": filter_value,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("inventory/list", params=params)
