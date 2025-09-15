#!/usr/bin/env python3
"""
SellerLegend API SDK - Basic Usage Example

This example demonstrates basic usage of the SellerLegend Python SDK.
It loads configuration from .env file in the SDK root directory.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to import SDK
sys.path.insert(0, str(Path(__file__).parent.parent))

from sellerlegend_api import SellerLegendClient, AuthenticationError

def main():
    # Load configuration from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get configuration from environment variables
    CLIENT_ID = os.getenv("SELLERLEGEND_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SELLERLEGEND_CLIENT_SECRET")
    BASE_URL = os.getenv("SELLERLEGEND_BASE_URL", "https://app.sellerlegend.com")
    ACCESS_TOKEN = os.getenv("SELLERLEGEND_ACCESS_TOKEN")
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing SELLERLEGEND_CLIENT_ID or SELLERLEGEND_CLIENT_SECRET")
        print("Please run 'python setup_test_config.py' to configure credentials")
        return 1
    
    # Initialize client - use access token if available, otherwise use OAuth
    if ACCESS_TOKEN:
        print("Using existing access token from .env")
        client = SellerLegendClient(
            access_token=ACCESS_TOKEN,
            base_url=BASE_URL
        )
    else:
        print("No access token found, will use OAuth2 Client Credentials flow")
        client = SellerLegendClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            base_url=BASE_URL
        )
    
    try:
        # Authenticate if we don't have an access token
        if not ACCESS_TOKEN:
            print("Authenticating with OAuth2 Client Credentials...")
            auth_result = client.authenticate_client_credentials()
            print(f"Authentication successful! Token expires in {auth_result.get('expires_in', 'N/A')} seconds")
        
        # Check if authenticated
        if not client.is_authenticated():
            print("Error: Not authenticated. Please check your credentials.")
            return 1
        
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