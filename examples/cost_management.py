#!/usr/bin/env python3
"""
SellerLegend API SDK - Cost Management Example

This example demonstrates how to manage product costs using the SellerLegend SDK.
"""

import os
from datetime import datetime, timedelta
from sellerlegend_api import SellerLegendClient

def main():
    # Configuration
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
        # Authenticate with client credentials
        print("Authenticating...")
        client.authenticate_client_credentials()
        print("Authentication successful!")
        
        # Example SKU to work with
        example_sku = "YOUR-PRODUCT-SKU"  # Replace with actual SKU
        
        # Example 1: Get existing cost periods for a product
        print(f"\n=== Getting cost periods for SKU: {example_sku} ===")
        
        try:
            cost_periods = client.costs.get_cost_periods(sku=example_sku)
            
            if cost_periods:
                for product in cost_periods:
                    print(f"Product: {product['product_sku']} - {product['title']}")
                    print(f"ASIN: {product['asin']}, Parent ASIN: {product['parent_asin']}")
                    
                    if 'data' in product and product['data']:
                        print("Cost Periods:")
                        for period in product['data']:
                            dates = period['dates']
                            print(f"  Period: {dates['from_date']} to {dates['to_date']}")
                            
                            for cost_element in period['cost_elements']:
                                print(f"    - {cost_element['cost_element']}: "
                                      f"{cost_element['amount']} {cost_element['currency']}")
                                if cost_element['provider']:
                                    print(f"      Provider: {cost_element['provider']}")
                                if cost_element['notes']:
                                    print(f"      Notes: {cost_element['notes']}")
                    else:
                        print("  No cost periods found")
                    print()
            else:
                print("No cost data found for this SKU")
                
        except Exception as e:
            print(f"Error retrieving cost periods: {str(e)}")
        
        # Example 2: Update cost periods for a product
        print(f"\n=== Updating cost periods for SKU: {example_sku} ===")
        
        # Define new cost data
        new_cost_data = [
            {
                "dates": {
                    "from_date": "2024-01-01",
                    "to_date": "2024-12-31"
                },
                "cost_elements": [
                    {
                        "cost_element": "Product Cost",
                        "provider": "Main Supplier",
                        "notes": "Updated cost for 2024",
                        "total_amount": 12.50,
                        "currency": "USD",
                        "conversion_rate": "1.00",
                        "units": 1,
                        "amount": 12.50
                    },
                    {
                        "cost_element": "Shipping Cost",
                        "provider": "Logistics Company",
                        "notes": "Shipping to Amazon warehouse",
                        "total_amount": 2.00,
                        "currency": "USD", 
                        "conversion_rate": "1.00",
                        "units": 1,
                        "amount": 2.00
                    }
                ]
            }
        ]
        
        try:
            print("Updating cost periods...")
            update_result = client.costs.update_cost_periods(
                sku=example_sku,
                data=new_cost_data
            )
            
            print(f"Update result: {update_result['message']}")
            
        except Exception as e:
            print(f"Error updating cost periods: {str(e)}")
        
        # Example 3: Bulk cost management using ASIN
        print(f"\n=== Bulk cost management using ASIN ===")
        
        example_asin = "B0EXAMPLE123"  # Replace with actual ASIN
        
        # Get all products with this ASIN
        try:
            products = client.costs.get_cost_periods(asin=example_asin)
            
            print(f"Found {len(products)} products with ASIN {example_asin}")
            
            for product in products:
                print(f"  SKU: {product['product_sku']}")
                
                # You could update costs for all these products here
                # This is useful for managing variations of the same product
                
        except Exception as e:
            print(f"Error retrieving products by ASIN: {str(e)}")
        
        # Example 4: Cost analysis across products  
        print(f"\n=== Cost Analysis ===")
        
        try:
            # Get inventory to analyze costs
            inventory = client.inventory.get_list(per_page=20)
            
            print("Sample cost analysis:")
            print(f"{'SKU':<15} {'Product':<30} {'Current Stock':<15}")
            print("-" * 60)
            
            if 'data' in inventory:
                for item in inventory['data'][:10]:  # First 10 items
                    sku = item.get('sku', 'N/A')
                    title = item.get('title', 'N/A')[:28]
                    stock = item.get('fulfillable_quantity', 'N/A')
                    
                    print(f"{sku:<15} {title:<30} {stock:<15}")
                    
                    # Get cost data for this SKU
                    try:
                        cost_data = client.costs.get_cost_periods(sku=sku)
                        
                        if cost_data and cost_data[0].get('data'):
                            latest_period = cost_data[0]['data'][0]  # Most recent period
                            total_cost = sum(
                                float(cost['amount']) 
                                for cost in latest_period['cost_elements']
                            )
                            print(f"                Current COGS: ${total_cost:.2f}")
                            
                    except Exception:
                        print(f"                Current COGS: Not available")
                        
                print("-" * 60)
                
        except Exception as e:
            print(f"Error in cost analysis: {str(e)}")
        
        print("\nCost management examples completed!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())