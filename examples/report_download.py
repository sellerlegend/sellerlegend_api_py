#!/usr/bin/env python3
"""
SellerLegend API SDK - Report Download Example

This example demonstrates how to create and download reports using the SellerLegend SDK.
"""

import os
import gzip
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
        
        # Example 1: Download report for a specific SKU
        print("\n=== Example 1: Download report for specific SKU ===")
        sku = "YOUR-PRODUCT-SKU"  # Replace with actual SKU
        
        try:
            print(f"Creating and downloading report for SKU: {sku}")
            report_data = client.create_and_download_report(
                product_sku=sku,
                timeout=300  # Wait up to 5 minutes
            )
            
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
            import time
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
                
                filename = f"report_date_{report_date}_{datetime.now().strftime('%H%M%S')}.csv.gz"
                with open(filename, "wb") as f:
                    f.write(report_data)
                
                print(f"Report saved as: {filename}")
                
        except Exception as e:
            print(f"Error in manual report handling: {str(e)}")
        
        print("\nReport download examples completed!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())