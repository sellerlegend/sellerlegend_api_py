#!/usr/bin/env python3
"""
SellerLegend API SDK - Report Download Example

This example demonstrates how to create and download reports using the SellerLegend SDK.
It loads configuration from .env file in the SDK root directory.
"""

import os
import sys
import gzip
import time
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add parent directory to path to import SDK
sys.path.insert(0, str(Path(__file__).parent.parent))

from sellerlegend_api import SellerLegendClient, AuthenticationError

def main():
    # Load configuration from .env file
    load_dotenv('.env')
    
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
    client = SellerLegendClient(
        access_token=ACCESS_TOKEN,
        base_url=BASE_URL
    )
    
    try:
        # Example 1: Download report for a specific SKU
        print("\n=== Example 1: Download report for specific SKU ===")
        sku = os.getenv("SELLERLEGEND_SKU", "YOUR-PRODUCT-SKU")

        if sku == "YOUR-PRODUCT-SKU":
            print("Note: Using placeholder SKU. Set SELLERLEGEND_SKU in .env for real data.")

        try:
            # Step 1: Create report request for a specific SKU
            print(f"Creating report request for SKU: {sku}")
            create_response = client.reports.create_report_request(
                product_sku=sku
            )

            report_id = create_response["report_id"]
            print(f"Report request created with ID: {report_id}")

            # Step 2: Wait for report completion
            print("Waiting for report to complete...")
            max_wait_time = 300  # 5 minutes timeout
            poll_interval = 10   # Check every 10 seconds
            elapsed = 0

            while elapsed < max_wait_time:
                status_response = client.reports.get_report_status(report_id)
                status = status_response.get("status", "").lower()

                print(f"  Status: {status} (elapsed: {elapsed}s)")

                if status == "done":
                    print("Report completed successfully!")
                    break
                elif status == "failed":
                    print("Report generation failed!")
                    raise Exception("Report generation failed")

                time.sleep(poll_interval)
                elapsed += poll_interval
            else:
                raise Exception(f"Report did not complete within {max_wait_time} seconds")

            # Step 3: Download the completed report
            print("Downloading completed report...")
            report_data = client.reports.download_report(report_id)

            # Save the gzipped report
            filename = f"report_{sku}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv.gz"
            with open(filename, "wb") as f:
                f.write(report_data)

            print(f"Report saved as: {filename}")

            # Extract and preview the CSV content
            with gzip.open(filename, 'rt', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # First 10 lines
                print("Preview of report content:")
                for i, line in enumerate(lines, 1):
                    print(f"  {i}: {line.strip()}")

        except Exception as e:
            print(f"Error downloading report for SKU {sku}: {str(e)}")
        
        # Example 2: Manual report handling with status checking
        print("\n=== Example 2: Manual report handling ===")
        
        # Use a date for report generation
        report_date = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        try:
            # Step 1: Create report request
            print(f"Creating report request for date: {report_date}")
            create_response = client.reports.create_report_request(
                dps_date=report_date
            )
            
            report_id = create_response["report_id"]
            print(f"Report request created with ID: {report_id}")
            
            # Step 2: Wait for completion with custom polling
            print("Waiting for report to complete...")
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                status_response = client.reports.get_report_status(report_id)
                status = status_response.get("status", "").lower()
                
                print(f"  Attempt {attempt}: Status = {status}")
                
                if status == "done":
                    print("Report completed successfully!")
                    break
                elif status == "failed":
                    print("Report generation failed!")
                    break
                
                time.sleep(10)  # Wait 10 seconds between checks
            else:
                print("Report did not complete within expected time")
                return 1
            
            # Step 3: Download the completed report
            if status == "done":
                print("Downloading completed report...")
                report_data = client.reports.download_report(report_id)

                print(report_data)
                
                filename = f"report_date_{report_date}_{datetime.now().strftime('%H%M%S')}.csv.gz"
                with open(filename, "wb") as f:
                    f.write(report_data)
                
                print(f"Report saved as: {filename}")
                
        except Exception as e:
            print(f"Error in manual report handling: {str(e)}")
        
        print("\nReport download examples completed!")
        
    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        if "401" in str(e.message) or "expired" in str(e.message).lower():
            print("\nYour access token may have expired. Please run 'python setup_test_config.py' to refresh.")
        return 1
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())