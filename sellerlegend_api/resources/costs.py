"""
SellerLegend API Costs (COGS) Resource Client

Handles cost/COGS management endpoints.
"""

from typing import Dict, Any, Optional, List
from ..base import BaseClient
from ..validators import (
    validate_account_params, validate_product_params,
    clean_params, ValidationError
)


class CostsClient:
    """Client for costs/COGS management endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize costs client."""
        self.client = base_client
    
    def get_cost_periods(
        self,
        sku: Optional[str] = None,
        asin: Optional[str] = None,
        parent_asin: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get cost periods for products.
        
        Args:
            sku: Product SKU (only one product identifier allowed)
            asin: Product ASIN (only one product identifier allowed)
            parent_asin: Parent ASIN (only one product identifier allowed)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Cost periods data
        """
        params = {
            "sku": sku,
            "asin": asin,
            "parent_asin": parent_asin,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_product_params(**params)
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("cogs/cost-periods", params=params)
    
    def update_cost_periods(
        self,
        data: List[Dict[str, Any]],
        sku: Optional[str] = None,
        asin: Optional[str] = None,
        parent_asin: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create or update cost periods.
        
        Args:
            data: Cost period data to update (required)
            sku: Product SKU (only one product identifier allowed)
            asin: Product ASIN (only one product identifier allowed)
            parent_asin: Parent ASIN (only one product identifier allowed)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Update result
        """
        if not data:
            raise ValidationError("data is required for updating cost periods")
            
        params = {
            "data": data,
            "sku": sku,
            "asin": asin,
            "parent_asin": parent_asin,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_product_params(**params)
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.post("cogs/cost-periods", json=params)
    
    def delete_cost_periods(
        self,
        sku: Optional[str] = None,
        asin: Optional[str] = None,
        parent_asin: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Delete cost periods.
        
        Args:
            sku: Product SKU (only one product identifier allowed)
            asin: Product ASIN (only one product identifier allowed)
            parent_asin: Parent ASIN (only one product identifier allowed)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Deletion result
        """
        params = {
            "sku": sku,
            "asin": asin,
            "parent_asin": parent_asin,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_product_params(**params)
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.delete("cogs/cost-periods", params=params)
