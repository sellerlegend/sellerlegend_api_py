"""
SellerLegend API Supply Chain Resource Client

Handles supply chain and restock suggestion endpoints.
"""

from typing import Dict, Any, Optional
from ..base import BaseClient
from ..validators import (
    validate_currency, validate_account_params,
    clean_params, ValidationError
)


class SupplyChainClient:
    """Client for supply chain management endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize supply chain client."""
        self.client = base_client
    
    def get_restock_suggestions(
        self,
        per_page: int = 500,
        currency: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get restock suggestions for products.
        
        Args:
            per_page: Number of items per page (500, 1000, 2000)
            currency: Currency code for values
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Restock suggestions data
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate currency
        currency = validate_currency(currency)
        
        params = {
            "per_page": per_page,
            "currency": currency,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("supply-chain/restock-suggestions", params=params)
