#!/usr/bin/env python3
"""
SellerLegend API SDK - Basic Usage Example

This example demonstrates basic usage of the SellerLegend Python SDK.
"""

import os
from datetime import datetime, timedelta
from sellerlegend_api import SellerLegendClient, AuthenticationError

def main():
    # Configuration - in production, use environment variables
    CLIENT_ID = os.getenv("SELLERLEGEND_CLIENT_ID", "your_client_id")
    CLIENT_SECRET = os.getenv("SELLERLEGEND_CLIENT_SECRET", "your_client_secret")
    BASE_URL = os.getenv("SELLERLEGEND_BASE_URL", "https://your-instance.sellerlegend.com")
    
    # Initialize client
    client = SellerLegendClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL
    )
    
    try:
        # Authenticate using OAuth2 Client Credentials flow
        # This is recommended for server-to-server integrations
        print("Authenticating with OAuth2 Client Credentials...")
        auth_result = client.authenticate_client_credentials()
        print(f"Authentication successful! Token expires in {auth_result.get('expires_in', 'N/A')} seconds")
        
        # Alternative: Use authorization code flow for user authentication
        # auth_url, state = client.get_authorization_url()
        # # Redirect user to auth_url...
        # # After user authorizes, exchange code for token:
        # # auth_result = client.authenticate_with_code(code)
        
        # Check service status
        print("\nChecking service status...")
        status = client.get_service_status()
        print(f"Service status: {status['status']}")
        
        # Get user information
        print("\nGetting user information...")
        user_info = client.user.get_me()
        print(f"Hello, {user_info['user']['name']} ({user_info['user']['email']})")
        
        # Get user accounts
        print("\nGetting accounts...")
        accounts = client.user.get_accounts()
        print(f"Found {len(accounts['accounts'])} accounts:")
        for account in accounts['accounts']:
            print(f"  - {account['account_title']} ({account['country_code']}) - Seller ID: {account['seller_id']}")
        
        # Get recent orders (last 7 days)
        print("\nGetting recent orders...")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        orders = client.sales.get_orders(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            per_page=100
        )
        
        print(f"Found {orders.get('total', 0)} orders in the last 7 days")
        if 'data' in orders and orders['data']:
            print("Recent orders:")
            for order in orders['data'][:5]:  # Show first 5 orders
                print(f"  - Order ID: {order.get('amazon_order_id', 'N/A')}, "
                      f"Date: {order.get('purchase_date', 'N/A')}, "
                      f"Total: {order.get('order_total', 'N/A')}")
        
        # Get inventory list
        print("\nGetting inventory...")
        inventory = client.inventory.get_list(per_page=50)
        print(f"Found {inventory.get('total', 0)} products in inventory")
        
        # Get connection status
        print("\nGetting connection status...")
        connections = client.connections.get_list()
        if 'connections' in connections:
            print("Connection status:")
            for conn in connections['connections']:
                print(f"  - {conn['account_title']}: SP={conn['sp'].get('status', 'N/A')}, "
                      f"PPC={conn['ppc'].get('status', 'N/A')}")
        
        print("\nAll operations completed successfully!")
        
    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        return 1
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())