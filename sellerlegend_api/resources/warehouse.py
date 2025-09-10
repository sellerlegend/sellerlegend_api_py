"""
SellerLegend API Warehouse Resource Client

Handles warehouse and shipment endpoints.
"""

from typing import Dict, Any, Optional, Literal
from ..base import BaseClient
from ..validators import (
    validate_filter_by, validate_account_params,
    clean_params, ValidationError
)


class WarehouseClient:
    """Client for warehouse management endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize warehouse client."""
        self.client = base_client
    
    def get_list(
        self,
        per_page: int = 500,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get warehouse inventory data.
        
        Args:
            per_page: Number of items per page (500, 1000, 2000)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Warehouse inventory data
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        params = {
            "per_page": per_page,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("warehouse/list", params=params)
    
    def get_inbound_shipments(
        self,
        per_page: int = 500,
        filter_by: Optional[Literal["sku", "asin", "parent_asin"]] = None,
        filter_value: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get inbound shipments data.
        
        Args:
            per_page: Number of items per page (500, 1000, 2000)
            filter_by: Filter field ("sku", "asin", "parent_asin")
            filter_value: Value to filter by
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Inbound shipments data
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate filter
        filter_by = validate_filter_by(filter_by)
        if filter_by and not filter_value:
            raise ValidationError("filter_value is required when filter_by is specified")
        
        params = {
            "per_page": per_page,
            "filter_by": filter_by,
            "filter_value": filter_value,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("warehouse/inbound-shipments", params=params)
