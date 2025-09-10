"""
SellerLegend API Reports Resource Client

Handles report generation, status checking, and download endpoints.
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime, date
from ..base import BaseClient
from ..validators import (
    validate_date, validate_account_params, clean_params, ValidationError
)


class ReportsClient:
    """Client for report-related API endpoints."""
    
    def __init__(self, base_client: BaseClient):
        """Initialize reports client."""
        self.client = base_client
    
    def create_report_request(
        self,
        product_sku: Optional[str] = None,
        dps_date: Optional[Union[str, date, datetime]] = None,
        last_updated_date: Optional[Union[str, date, datetime]] = None,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit a report generation request.
        
        Args:
            product_sku: Product SKU to generate report for
            dps_date: DPS date for report
            last_updated_date: Last updated date filter
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Report request response with report_id
        """
        # Validate dates
        dps_date = validate_date(dps_date, "dps_date")
        last_updated_date = validate_date(last_updated_date, "last_updated_date")
        
        params = {
            "product_sku": product_sku,
            "dps_date": dps_date,
            "last_updated_date": last_updated_date,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.post("reports/request", json=params)
    
    def get_report_status(
        self,
        report_id: str,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get the status of a report request.
        
        Args:
            report_id: Report ID to check status for (required)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Report status information
        """
        if not report_id:
            raise ValidationError("report_id is required")
            
        params = {
            "report_id": report_id,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("reports/status", params=params)
    
    def download_report(
        self,
        report_id: str,
        account_title: Optional[str] = None,
        seller_id: Optional[str] = None,
        marketplace_id: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Download a completed report.
        
        Args:
            report_id: Report ID to download (required)
            account_title: Account title filter
            seller_id: Amazon seller ID (requires marketplace_id)
            marketplace_id: Amazon marketplace ID (requires seller_id)
            
        Returns:
            Report data (format depends on report type)
        """
        if not report_id:
            raise ValidationError("report_id is required")
            
        params = {
            "report_id": report_id,
            "account_title": account_title,
            "seller_id": seller_id,
            "marketplace_id": marketplace_id,
        }
        params.update(kwargs)
        
        validate_account_params(**params)
        params = clean_params(params)
        
        return self.client.get("reports/download", params=params)
