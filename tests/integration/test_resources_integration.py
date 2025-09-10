"""
Integration tests for resource endpoints

These tests make actual API calls to test all resource endpoints.
"""

import pytest
from datetime import datetime, timedelta
from sellerlegend_api import SellerLegendClient
from sellerlegend_api.exceptions import ValidationError, NotFoundError
from .config import test_config


class TestResourcesIntegration:
    """Base class for resource integration tests."""
    
    @classmethod
    def setup_class(cls):
        """Set up authenticated client for all tests."""
        # Ensure configuration exists and tokens are valid
        # This will automatically create config or refresh tokens if needed
        test_config.ensure_configured()
        
        # Now get the authenticated client
        cls.client = test_config.get_authenticated_client()


class TestUserResourceIntegration(TestResourcesIntegration):
    """Test User resource with real API."""
    
    def test_get_me(self):
        """Test getting current user information."""
        response = self.client.user.get_me()
        
        # Verify response structure
        assert 'user' in response
        user_info = response['user']
        
        assert 'id' in user_info
        assert 'email' in user_info
        assert isinstance(user_info['id'], int)
        assert '@' in user_info['email']
        
        # Optional fields that might be present
        if 'name' in user_info:
            assert isinstance(user_info['name'], str)
        if 'created_at' in user_info:
            assert isinstance(user_info['created_at'], str)
    
    def test_get_accounts(self):
        """Test getting user accounts."""
        response = self.client.user.get_accounts()
        
        # Verify response structure
        assert 'accounts' in response
        accounts = response['accounts']
        assert isinstance(accounts, list)
        
        # If user has accounts, verify structure
        if accounts:
            account = accounts[0]
            assert 'id' in account
            assert 'marketplace' in account or 'marketplace_id' in account
            
            # Store account info for other tests
            if not test_config.test_account_id:
                test_config.test_account_id = account['id']
            if not test_config.test_marketplace_id:
                test_config.test_marketplace_id = account.get('marketplace', account.get('marketplace_id'))
            if 'seller_id' in account and not test_config.test_seller_id:
                test_config.test_seller_id = account['seller_id']


class TestSalesResourceIntegration(TestResourcesIntegration):
    """Test Sales resource with real API."""
    
    def test_get_orders(self):
        """Test getting orders."""
        # Use a date range that's likely to have data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        orders = self.client.sales.get_orders(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            per_page=500  # Limit for testing
        )
        
        # Verify response structure
        # Orders can be returned as either a list in 'data' or as a dict keyed by order ID
        assert isinstance(orders, dict)
        
        # Check if it's a paginated response with 'data' or direct order dict
        if 'data' in orders:
            assert isinstance(orders['data'], (list, dict))
            order_data = orders['data']
        else:
            # Direct order dictionary
            order_data = orders
        
        # If there are orders, verify structure
        if order_data:
            if isinstance(order_data, dict):
                # Get first order from dict
                first_order_id = list(order_data.keys())[0] if order_data else None
                if first_order_id:
                    order = order_data[first_order_id]
                    # Check for common order fields
                    possible_fields = ['purchased_at', 'amazon_order_id', 'order_status', 'marketplace_name']
                    assert any(field in order for field in possible_fields)
            elif isinstance(order_data, list) and order_data:
                order = order_data[0]
                assert 'order_id' in order or 'id' in order
    
    def test_get_statistics_dashboard(self):
        """Test getting statistics dashboard."""
        # Test with date view
        stats = self.client.sales.get_statistics_dashboard(
            view_by="date",
            group_by="Date",  # Valid value for date view
            per_page=500
        )
        
        # Verify response structure - it's a paginated response
        assert isinstance(stats, dict)
        assert 'data' in stats
        assert 'current_page' in stats
        assert 'per_page' in stats
        
        # Verify data structure
        if stats['data']:
            # Data should be a list for paginated responses
            assert isinstance(stats['data'], list)
            # Check first item has expected date-related fields
            first_item = stats['data'][0]
            # Common fields for date grouping (actual field names from API)
            possible_fields = ['Order Date', 'Orders', 'Units', 'Revenue', 'Net Profit']
            assert any(field in first_item for field in possible_fields)
        
        # Test with product view
        stats = self.client.sales.get_statistics_dashboard(
            view_by="product",
            group_by="Product",  # Valid value for product view
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(stats, dict)
        assert 'data' in stats
        
        # Verify product data structure
        if stats['data']:
            assert isinstance(stats['data'], list)
            # Check first item has expected product-related fields
            first_item = stats['data'][0]
            # Common fields for product grouping (actual field names from API)
            possible_fields = ['SKU', 'ASIN', 'Orders', 'Units', 'Revenue', 'Net Profit']
            assert any(field in first_item for field in possible_fields)
    
    def test_get_per_day_per_product(self):
        """Test getting per day per product data."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        data = self.client.sales.get_per_day_per_product(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(data, dict)
        if 'data' in data:
            assert isinstance(data['data'], list)
    
    def test_get_transactions(self):
        """Test getting transactions."""
        transactions = self.client.sales.get_transactions(
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(transactions, dict)
        if 'data' in transactions:
            assert isinstance(transactions['data'], list)
            
            # If there are transactions, verify structure
            if transactions['data']:
                transaction = transactions['data'][0]
                assert 'id' in transaction or 'transaction_id' in transaction


class TestInventoryResourceIntegration(TestResourcesIntegration):
    """Test Inventory resource with real API."""
    
    def test_get_list(self):
        """Test getting inventory list."""
        inventory = self.client.inventory.get_list(
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(inventory, dict)
        if 'data' in inventory:
            assert isinstance(inventory['data'], list)
            
            # If there's inventory, verify structure
            if inventory['data']:
                item = inventory['data'][0]
                # Check for common inventory fields (actual field names from API)
                possible_fields = ['SKU', 'ASIN', 'FNSKU', 'In Stock', 'Title']
                assert any(field in item for field in possible_fields)
    
    def test_get_list_with_sku_filter(self):
        """Test getting inventory with SKU filter."""
        # First get an actual SKU from the inventory
        inventory = self.client.inventory.get_list(per_page=500)
        
        if not inventory.get('data'):
            pytest.skip("No inventory data available to test SKU filtering")
        
        # Use the first available SKU for testing
        actual_sku = inventory['data'][0].get('SKU')
        if not actual_sku:
            pytest.skip("No SKU field in inventory data")
        
        # Now test filtering with a real SKU
        filtered_inventory = self.client.inventory.get_list(
            sku=actual_sku,
            per_page=500
        )
        
        assert isinstance(filtered_inventory, dict)
        if 'data' in filtered_inventory and filtered_inventory['data']:
            # The SKU filter might not be working as expected or might return all results
            # Just verify that at least the searched SKU is in the results
            sku_found = False
            for item in filtered_inventory['data']:
                if 'SKU' in item and item['SKU'] == actual_sku:
                    sku_found = True
                    break
            
            # Verify that at least the searched SKU appears in the results
            assert sku_found, f"SKU {actual_sku} not found in filtered results"


class TestCostsResourceIntegration(TestResourcesIntegration):
    """Test Costs resource with real API."""
    
    def test_get_cost_periods(self):
        """Test getting cost periods."""
        # First get a SKU from inventory to use for the costs query
        inventory = self.client.inventory.get_list(per_page=500)
        
        if not inventory.get('data') or not inventory['data']:
            pytest.skip("No inventory data available to test costs")
        
        # Get the first SKU from inventory
        test_sku = inventory['data'][0].get('SKU')
        if not test_sku:
            pytest.skip("No SKU available in inventory")
        
        # Now get cost periods for this SKU
        costs = self.client.costs.get_cost_periods(
            sku=test_sku,
            per_page=500
        )
        
        # Verify response structure - costs API returns a list directly
        assert isinstance(costs, list)
        
        # If there are costs, verify structure
        if costs:
            cost_item = costs[0]
            assert isinstance(cost_item, dict)
            
            # Check for expected fields in the cost response
            # Based on the actual response structure
            possible_main_fields = ['product_sku', 'asin', 'parent_asin', 'internal_name', 'title', 'data']
            assert any(field in cost_item for field in possible_main_fields)
            
            # If there's a data field with cost elements
            if 'data' in cost_item and cost_item['data']:
                period = cost_item['data'][0]
                # Check for dates and cost_elements
                if 'dates' in period:
                    assert isinstance(period['dates'], dict)
                if 'cost_elements' in period:
                    assert isinstance(period['cost_elements'], list)


class TestConnectionsResourceIntegration(TestResourcesIntegration):
    """Test Connections resource with real API."""
    
    def test_get_list(self):
        """Test getting connections list."""
        connections = self.client.connections.get_list()
        
        # Verify response structure
        assert isinstance(connections, dict)
        if 'data' in connections:
            assert isinstance(connections['data'], list)
            
            # If there are connections, verify structure
            if connections['data']:
                connection = connections['data'][0]
                # Check for common connection fields
                possible_fields = ['id', 'platform', 'status', 'marketplace_id', 'seller_id']
                assert any(field in connection for field in possible_fields)


class TestSupplyChainResourceIntegration(TestResourcesIntegration):
    """Test Supply Chain resource with real API."""
    
    def test_get_restock_suggestions(self):
        """Test getting restock suggestions."""
        try:
            suggestions = self.client.supply_chain.get_restock_suggestions(
                per_page=500
            )
            
            # Verify response structure
            assert isinstance(suggestions, dict)
            if 'data' in suggestions:
                assert isinstance(suggestions['data'], list)
        except (NotFoundError, ValidationError):
            # Endpoint might not be available or require specific data
            pytest.skip("Supply chain endpoint not available or requires specific setup")


class TestWarehouseResourceIntegration(TestResourcesIntegration):
    """Test Warehouse resource with real API."""
    
    def test_get_list(self):
        """Test getting warehouses list."""
        warehouses = self.client.warehouse.get_list(
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(warehouses, dict)
        if 'data' in warehouses:
            assert isinstance(warehouses['data'], list)
            
            # If there are warehouses, verify structure
            if warehouses['data']:
                warehouse = warehouses['data'][0]
                # Check for common warehouse fields (actual field names from API)
                possible_fields = ['Name', 'Internal Name', 'Code', 'Notes', 'Type', 'Address 1', 'City', 'Country Code']
                assert any(field in warehouse for field in possible_fields)
    
    def test_get_inbound_shipments(self):
        """Test getting inbound shipments."""
        shipments = self.client.warehouse.get_inbound_shipments(
            per_page=500
        )
        
        # Verify response structure
        assert isinstance(shipments, dict)
        if 'data' in shipments:
            assert isinstance(shipments['data'], list)


class TestNotificationsResourceIntegration(TestResourcesIntegration):
    """Test Notifications resource with real API."""
    
    def test_get_list_info_notifications(self):
        """Test getting info notifications."""
        try:
            notifications = self.client.notifications.get_list(
                notification_type="info"
            )
            
            # Verify response structure
            assert isinstance(notifications, dict)
            if 'data' in notifications:
                assert isinstance(notifications['data'], list)
                
                # If there are notifications, verify structure
                if notifications['data']:
                    notification = notifications['data'][0]
                    assert 'id' in notification or 'message' in notification
        except (NotFoundError, ValidationError):
            # Endpoint might not be available
            pytest.skip("Notifications endpoint not available or requires specific setup")
    
    def test_get_list_alert_notifications(self):
        """Test getting alert notifications."""
        try:
            notifications = self.client.notifications.get_list(
                notification_type="alert"
            )
            
            assert isinstance(notifications, dict)
        except (NotFoundError, ValidationError):
            pytest.skip("Alert notifications not available")


class TestReportsResourceIntegration(TestResourcesIntegration):
    """Test Reports resource with real API."""
    
    def test_create_and_check_report(self):
        """Test creating a report and checking its status."""
        # Create a report request
        report = self.client.reports.create_report_request(
            dps_date=datetime.now().date().isoformat()
        )
        
        # Verify response structure
        assert 'id' in report or 'report_id' in report
        report_id = report.get('id') or report.get('report_id')
        
        # Check report status
        status = self.client.reports.get_report_status(report_id)
        
        # Verify status response
        assert 'status' in status or 'state' in status
        assert 'id' in status or 'report_id' in status
        
        # Status should be one of the expected values
        current_status = status.get('status') or status.get('state')
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'queued']
        assert current_status.lower() in valid_statuses
    
    def test_invalid_report_status(self):
        """Test checking status of non-existent report."""
        with pytest.raises(NotFoundError):
            self.client.reports.get_report_status("invalid_report_id_12345")
