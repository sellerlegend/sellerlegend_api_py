"""
Tests for API resource endpoints
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sellerlegend_api import SellerLegendClient
from sellerlegend_api.exceptions import ValidationError, NotFoundError
from tests.fixtures.responses import (
    USER_ME_RESPONSE,
    USER_ACCOUNTS_RESPONSE,
    ORDERS_RESPONSE,
    REPORT_CREATE_RESPONSE,
    REPORT_STATUS_RESPONSE,
    INVENTORY_RESPONSE,
    COSTS_RESPONSE,
    CONNECTIONS_RESPONSE,
    SUPPLY_CHAIN_RESPONSE,
    WAREHOUSE_RESPONSE,
    NOTIFICATIONS_RESPONSE
)


class TestUserResource:
    """Test User resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_me(self, mock_session):
        """Test getting current user info."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = USER_ME_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.user.get_me()
        
        assert result == USER_ME_RESPONSE
        assert result["email"] == "john@example.com"
        
        # Verify API call
        mock_session_instance.request.assert_called_once()
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["url"].endswith("/api/user/me")
        assert call_args[1]["method"] == "GET"
        assert "Authorization" in call_args[1]["headers"]
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_accounts(self, mock_session):
        """Test getting user accounts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = USER_ACCOUNTS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.user.get_accounts()
        
        assert result == USER_ACCOUNTS_RESPONSE
        assert len(result["data"]) == 1
        assert result["data"][0]["marketplace_id"] == "ATVPDKIKX0DER"


class TestSalesResource:
    """Test Sales resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_orders(self, mock_session):
        """Test getting orders."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ORDERS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.sales.get_orders(
            start_date="2023-12-01",
            end_date="2023-12-31",
            per_page=500
        )
        
        assert result == ORDERS_RESPONSE
        assert len(result["data"]) == 1
        assert result["data"][0]["order_id"] == "123-4567890-1234567"
        
        # Verify API call parameters
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["params"]["start_date"] == "2023-12-01"
        assert call_args[1]["params"]["end_date"] == "2023-12-31"
        assert call_args[1]["params"]["per_page"] == "500"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_statistics_dashboard(self, mock_session):
        """Test getting statistics dashboard."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"revenue": 10000}}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.sales.get_statistics_dashboard(view_by="product", group_by="sku")
        
        assert result["data"]["revenue"] == 10000


class TestReportsResource:
    """Test Reports resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_create_report_request(self, mock_session):
        """Test creating a report request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = REPORT_CREATE_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.reports.create_report_request(
            product_sku="TEST-SKU-001",
            dps_date="2023-12-01"
        )
        
        assert result == REPORT_CREATE_RESPONSE
        assert result["status"] == "pending"
        
        # Verify POST request
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["method"] == "POST"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_report_request_status(self, mock_session):
        """Test getting report status."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = REPORT_STATUS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.reports.get_report_status("3001")
        
        assert result == REPORT_STATUS_RESPONSE
        assert result["status"] == "completed"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_download_report_request(self, mock_session):
        """Test downloading a report."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Since download_report uses client.get which parses JSON, return JSON data
        mock_response.json.return_value = {"data": "report data here", "status": "completed"}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.reports.download_report("3001")
        
        assert result["data"] == "report data here"
        assert result["status"] == "completed"


class TestInventoryResource:
    """Test Inventory resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_list(self, mock_session):
        """Test getting inventory list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = INVENTORY_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.inventory.get_list(
            sku="TEST-SKU-001",
            per_page=500
        )
        
        assert result == INVENTORY_RESPONSE
        assert result["data"][0]["fnsku"] == "X000TEST001"
        
        # Verify parameters
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["params"]["sku"] == "TEST-SKU-001"
        assert call_args[1]["params"]["per_page"] == "500"


class TestCostsResource:
    """Test Costs resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_cost_periods(self, mock_session):
        """Test getting cost periods."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = COSTS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.costs.get_cost_periods(
            sku="TEST-SKU-001"
        )
        
        assert result == COSTS_RESPONSE
        assert result["data"][0]["total_cost"] == 13.00
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_update_cost_periods(self, mock_session):
        """Test updating cost periods."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Costs updated"}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.costs.update_cost_periods(
            data=[{"period": "2023-12", "cost": 15.00}],
            sku="TEST-SKU-001"
        )
        
        assert result["success"] is True
        
        # Verify POST request
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["method"] == "POST"


class TestConnectionsResource:
    """Test Connections resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_list(self, mock_session):
        """Test getting connections list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = CONNECTIONS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.connections.get_list()
        
        assert result == CONNECTIONS_RESPONSE
        assert result["data"][0]["platform"] == "amazon"


class TestSupplyChainResource:
    """Test Supply Chain resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_restock_suggestions(self, mock_session):
        """Test getting restock suggestions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = SUPPLY_CHAIN_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.supply_chain.get_restock_suggestions(sku="TEST-SKU-001")
        
        assert result == SUPPLY_CHAIN_RESPONSE
        assert result["data"][0]["supplier_name"] == "Test Supplier"


class TestWarehouseResource:
    """Test Warehouse resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_list(self, mock_session):
        """Test getting warehouses list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = WAREHOUSE_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.warehouse.get_list()
        
        assert result == WAREHOUSE_RESPONSE
        assert result["data"][0]["code"] == "WH001"
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_inbound_shipments(self, mock_session):
        """Test getting inbound shipments."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"shipment_id": "FBA123"}]}
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        result = client.warehouse.get_inbound_shipments()
        
        assert result["data"][0]["shipment_id"] == "FBA123"


class TestNotificationsResource:
    """Test Notifications resource endpoints."""
    
    @patch('sellerlegend_api.base.requests.Session')
    def test_get_list(self, mock_session):
        """Test getting notifications list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = NOTIFICATIONS_RESPONSE
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session_instance.headers = Mock()
        mock_session_instance.headers.update = Mock()
        mock_session.return_value = mock_session_instance
        
        client = SellerLegendClient(
            access_token="test_token",
            base_url="https://test.sellerlegend.com"
        )
        
        # Note: get_list requires notification_type parameter
        result = client.notifications.get_list(notification_type="info")
        
        assert result == NOTIFICATIONS_RESPONSE
        assert result["data"][0]["read"] is False
        
        # Verify the notification_type parameter
        call_args = mock_session_instance.request.call_args
        assert call_args[1]["params"]["notification_type"] == "info"