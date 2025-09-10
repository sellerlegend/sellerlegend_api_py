"""
SellerLegend API Sales Resource Client

Handles sales-related API endpoints including orders, statistics, and transactions.
"""

from typing import Dict, Any, Optional, Literal, Union
from datetime import datetime, date
from ..base import BaseClient
from ..validators import (
    validate_date, validate_enum, validate_per_page,
    validate_filter_by, validate_currency, validate_account_params,
    clean_params, ValidationError
)


class SalesClient:
    """Client for sales-related API endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """
        Initialize sales client.
        
        Args:
            base_client: Base API client instance
        """
        self.client = base_client
    
    def get_orders(
        self,
        per_page: int = 500,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        sales_channel: Optional[Literal["amazon", "non-amazon"]] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get orders data with pagination.
        
        Args:
            per_page: Number of records per page (500, 1000, 2000)
            start_date: Start date (defaults to 7 days ago)
            end_date: End date (defaults to today)
            sales_channel: Filter by sales channel ("amazon" or "non-amazon")
            account_title: Specific account title to filter by
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            **kwargs: Additional parameters
            
        Returns:
            Paginated orders data
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000 for orders")
        
        # Validate dates
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
        
        # Validate sales channel
        if sales_channel:
            validate_enum(sales_channel, ["amazon", "non-amazon"], "sales_channel")
        
        params = {
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "sales_channel": sales_channel,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        # Validate account params
        validate_account_params(**params)
        
        # Clean and send request
        params = clean_params(params)
        return self.client.get("sales/orders", params=params)
    
    def get_statistics_dashboard(
        self,
        view_by: Literal["product", "date"],
        group_by: str,
        per_page: int = 500,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        currency: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get sales statistics dashboard data.
        
        Args:
            view_by: View mode - "product" or "date" (required)
            group_by: Grouping option (required, depends on view_by)
            per_page: Number of records per page (500, 1000, 2000)
            start_date: Start date (defaults to 7 days ago)
            end_date: End date (defaults to today)
            currency: Currency code for data
            account_title: Specific account title to filter by
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            **kwargs: Additional parameters
            
        Returns:
            Sales statistics dashboard data
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate required params
        validate_enum(view_by, ["product", "date"], "view_by")
        
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate dates
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
        
        # Validate currency
        currency = validate_currency(currency)
        
        params = {
            "view_by": view_by,
            "group_by": group_by,
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        # Validate account params
        validate_account_params(**params)
        
        # Clean and send request
        params = clean_params(params)
        return self.client.get("sales/statistics-dashboard", params=params)
    
    def get_per_day_per_product(
        self,
        per_page: int = 500,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        sales_channel: Optional[Literal["amazon", "non-amazon"]] = None,
        currency: Optional[str] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get per-day per-product sales data.
        
        Args:
            per_page: Number of records per page (500, 1000, 2000)
            start_date: Start date (defaults to 7 days ago)
            end_date: End date (defaults to today)
            sales_channel: Filter by sales channel
            currency: Currency code for data
            account_title: Specific account title to filter by
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            **kwargs: Additional parameters
            
        Returns:
            Per-day per-product sales data
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate dates
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
        
        # Validate sales channel
        if sales_channel:
            validate_enum(sales_channel, ["amazon", "non-amazon"], "sales_channel")
        
        # Validate currency
        currency = validate_currency(currency)
        
        params = {
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "sales_channel": sales_channel,
            "currency": currency,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        # Validate account params
        validate_account_params(**params)
        
        # Clean and send request
        params = clean_params(params)
        return self.client.get("sales/per-day-per-product", params=params)
    
    def get_transactions(
        self,
        per_page: int = 500,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get financial transactions data.
        
        Args:
            per_page: Number of records per page (500, 1000, 2000)
            start_date: Start date (defaults to 7 days ago)
            end_date: End date (defaults to today)
            account_title: Specific account title to filter by
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            **kwargs: Additional parameters
            
        Returns:
            Financial transactions data
            
        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate per_page
        if per_page not in [500, 1000, 2000]:
            raise ValidationError("per_page must be 500, 1000, or 2000")
        
        # Validate dates
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
        
        params = {
            "per_page": per_page,
            "start_date": start_date,
            "end_date": end_date,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        # Validate account params
        validate_account_params(**params)
        
        # Clean and send request
        params = clean_params(params)
        return self.client.get("sales/transactions", params=params)