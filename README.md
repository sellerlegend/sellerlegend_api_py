# SellerLegend Python SDK

The official Python SDK for the SellerLegend API, providing a comprehensive interface to integrate SellerLegend's Amazon seller analytics and management capabilities into your Python applications.

## Features

- **OAuth2 Authentication**: Full support for Laravel Passport OAuth2 authentication
- **Comprehensive API Coverage**: Access to all major SellerLegend API endpoints
- **Type Hints**: Full type annotations for better IDE support and code reliability
- **Error Handling**: Comprehensive exception hierarchy for different error types
- **Automatic Token Refresh**: Handles token expiration and refresh automatically
- **Request Retry Logic**: Built-in retry mechanism for resilient API communication
- **Async Report Downloads**: Support for asynchronous report generation and download

## Installation

```bash
pip install sellerlegend-api
```

Or install from source:

```bash
git clone <repository_url>
cd python-sdk
pip install -e .
```

## Quick Start

### OAuth2 Client Credentials Flow (Recommended for Server-to-Server)

```python
from sellerlegend_api import SellerLegendClient

# Initialize the client for OAuth2 Client Credentials flow
client = SellerLegendClient(
    client_id="your_oauth_client_id",
    client_secret="your_oauth_client_secret",
    base_url="https://your-instance.sellerlegend.com"
)

# Authenticate using client credentials
token_info = client.authenticate_client_credentials()
print(f"Access token obtained, expires in: {token_info['expires_in']} seconds")

# Now you can access API resources
user_info = client.user.get_me()
print(f"API Client: {user_info['user']['name']}")

# Get accounts accessible to this OAuth client
accounts = client.user.get_accounts()
for account in accounts['accounts']:
    print(f"Account: {account['account_title']} - {account['country_code']}")
```

### OAuth2 Authorization Code Flow (For User-Specific Access)

```python
from sellerlegend_api import SellerLegendClient

# Initialize the client
client = SellerLegendClient(
    client_id="your_oauth_client_id",
    client_secret="your_oauth_client_secret",
    base_url="https://your-instance.sellerlegend.com"
)

# Get authorization URL and redirect user to authorize
auth_url, state = client.get_authorization_url()
# ... redirect user to auth_url ...
# ... user authorizes and you get a code ...

# Exchange code for token
token_info = client.authenticate_with_code(code, state)
print(f"Authenticated as user, token expires in: {token_info['expires_in']} seconds")

# Access user-specific data
user_info = client.user.get_me()
print(f"Logged in as: {user_info['user']['name']}")
```

## Authentication

The SDK supports OAuth2 authentication with Laravel Passport. Choose the appropriate flow for your use case:

### 1. Authorization Code Flow (Recommended for Web Apps)

Best for web applications where users need to explicitly grant permissions:

```python
# Step 1: Get authorization URL
auth_url, state = client.get_authorization_url()

# Step 2: Redirect user to auth_url
# User logs in to SellerLegend and approves your app

# Step 3: Handle callback with authorization code
code = request.args.get('code')  # From callback URL
state = request.args.get('state')  # For CSRF validation

# Step 4: Exchange code for access token
token_info = client.authenticate_with_code(code, state)
print(f"Access token obtained, expires in: {token_info['expires_in']} seconds")
```

**When to use:**
- Web applications (SaaS, dashboards)
- Applications requiring user consent
- Third-party integrations
- When you need user consent without handling credentials

### 2. Client Credentials Grant (Recommended for Automation)

Best for automated scripts, background jobs, and server-to-server integrations:

```python
# No user credentials needed - uses only OAuth client ID and secret
token_info = client.authenticate_client_credentials()

# The client now has access based on the OAuth client's configured permissions
print(f"Access token obtained, expires in: {token_info['expires_in']} seconds")
```

**When to use:** 
- Automated reporting scripts
- Data synchronization services
- Background processing jobs
- API integrations that don't need user context

### 3. Direct Access Token (When Available)

If you already have an access token from another authentication method:

```python
client = SellerLegendClient(
    base_url="https://your-instance.sellerlegend.com",
    access_token="existing_bearer_token_here"
)

# No need to authenticate - ready to use
user_info = client.user.get_me()
```

**When to use:**
- When you have a token from another authentication system
- For testing with pre-generated tokens
- When tokens are managed externally

### Token Management

```python
# Check authentication status
if client.is_authenticated():
    print("Client is authenticated")

# Get current token information
token_info = client.get_token_info()
print(f"Token expires at: {token_info['expires_at']}")
print(f"Access token: {token_info['access_token'][:20]}...")  # First 20 chars only

# Token is automatically refreshed when expired
# You can also manually refresh if needed
new_token = client.refresh_token()
print(f"Token refreshed, new expiry: {new_token['expires_in']} seconds")
```

### Using Existing Tokens

If you already have an access token from another source:

```python
from sellerlegend_api import SellerLegendClient

# Initialize with existing token
client = SellerLegendClient(
    base_url="https://your-instance.sellerlegend.com",
    access_token="existing_bearer_token_here"
)

# No need to call authenticate - ready to use immediately
user_info = client.user.get_me()
```

### Environment Variables

For security, store credentials in environment variables:

```python
import os
from sellerlegend_api import SellerLegendClient

client = SellerLegendClient(
    client_id=os.getenv('SELLERLEGEND_CLIENT_ID'),
    client_secret=os.getenv('SELLERLEGEND_CLIENT_SECRET'),
    base_url=os.getenv('SELLERLEGEND_API_URL', 'https://api.sellerlegend.com')
)

# Use client credentials flow for automated scripts
client.authenticate_client_credentials()
```

## API Usage Examples

### Sales Data

```python
# Get recent orders
orders = client.sales.get_orders(
    per_page=500,
    start_date="2023-12-01",
    end_date="2023-12-31"
)

# Get sales statistics by product
stats = client.sales.get_statistics_dashboard(
    view_by="product",
    group_by="sku",
    per_page=1000,
    start_date="2023-12-01",
    end_date="2023-12-31",
    currency="USD"
)

# Get daily sales per product
daily_sales = client.sales.get_per_day_per_product(
    per_page=500,
    start_date="2023-12-01",
    end_date="2023-12-31"
)

# Get transaction data
transactions = client.sales.get_transactions(
    per_page=1000,
    start_date="2023-12-01",
    end_date="2023-12-31"
)
```

### Reports

```python
# Create and download a report (async)
report_data = client.reports.create_and_download_report(
    product_sku="YOUR-SKU-123",
    timeout=300  # Wait up to 5 minutes
)

# Save the report to file
with open("report.csv.gz", "wb") as f:
    f.write(report_data)

# Or handle the process manually
# 1. Create report request
create_response = client.reports.create_report_request(
    product_sku="YOUR-SKU-123"
)
report_id = create_response["report_id"]

# 2. Check status periodically
status = client.reports.get_report_status(report_id)
print(f"Report status: {status['status']}")

# 3. Download when ready
if status['status'] == 'done':
    report_data = client.reports.download_report(report_id)
```

### Inventory Management

```python
# Get inventory list
inventory = client.inventory.get_list(
    per_page=500,
    velocity_start_date="2023-11-01",
    velocity_end_date="2023-12-31"
)

# Filter by specific SKU
inventory_filtered = client.inventory.get_list(
    per_page=100,
    filter_by="sku",
    filter_value="YOUR-SKU-123"
)
```

### Cost Management (COGS)

```python
# Get cost periods for a product
cost_periods = client.costs.get_cost_periods(sku="YOUR-SKU-123")

# Update cost periods
cost_data = [
    {
        "dates": {
            "from_date": "2023-01-01",
            "to_date": "2023-12-31"
        },
        "cost_elements": [
            {
                "cost_element": "Product Cost",
                "provider": "Supplier Name",
                "notes": "Updated cost",
                "total_amount": 15.50,
                "currency": "USD",
                "conversion_rate": "1.00",
                "units": 1,
                "amount": 15.50
            }
        ]
    }
]

result = client.costs.update_cost_periods(
    sku="YOUR-SKU-123",
    data=cost_data
)
```

### Supply Chain

```python
# Get restock suggestions
suggestions = client.supply_chain.get_restock_suggestions(
    per_page=500,
    currency="USD"
)

for suggestion in suggestions['data']:
    print(f"SKU: {suggestion['sku']}, Suggested Reorder: {suggestion['suggested_quantity']}")
```

### Connections Status

```python
# Check Amazon connection status
connections = client.connections.get_list()

for conn in connections['connections']:
    print(f"Account: {conn['account_title']}")
    print(f"SP API Status: {conn['sp']['status']}")
    print(f"PPC Status: {conn['ppc']['status']}")
```

## Account Filtering

Most endpoints support filtering by specific accounts or account groups:

```python
# Filter by account title
orders = client.sales.get_orders(
    account_title="My Store",
    per_page=500
)

# Filter by seller ID and marketplace
orders = client.sales.get_orders(
    seller_id="A1SELLER123",
    marketplace_id="ATVPDKIKX0DER",
    per_page=500
)

# Filter by account group
stats = client.sales.get_statistics_dashboard(
    view_by="product",
    group_by="sku",
    group_title="US Stores",
    per_page=1000
)
```

## Error Handling

```python
from sellerlegend_api import (
    SellerLegendClient,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError
)

client = SellerLegendClient(client_id="...", client_secret="...", base_url="...")

try:
    client.authenticate_client_credentials()
    orders = client.sales.get_orders(per_page=500)
    
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Response data: {e.response_data}")
    
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    
except ServerError as e:
    print(f"Server error: {e.message}")
```

## Context Manager Usage

```python
# Use as context manager for automatic cleanup
with SellerLegendClient(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    base_url="https://your-instance.sellerlegend.com"
) as client:
    
    client.authenticate_client_credentials()
    
    # Your API calls here
    user_info = client.user.get_me()
    orders = client.sales.get_orders(per_page=500)
    
# Session is automatically closed when exiting the context
```

## Configuration

### Timeout and Retry Settings

```python
client = SellerLegendClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    base_url="https://your-instance.sellerlegend.com",
    timeout=60,          # 60 second timeout
    max_retries=5,       # Retry up to 5 times
    backoff_factor=0.5   # Backoff factor for retries
)
```

### Custom Headers

```python
# Service status check with custom headers
status = client._base_client._make_request(
    method="GET",
    endpoint="service-status",
    headers={"X-Custom-Header": "value"}
)
```

## Available Resources

The SDK provides access to the following SellerLegend API resources:

- **`client.user`**: User information and account management
- **`client.sales`**: Orders, statistics, and transaction data
- **`client.reports`**: Report generation and download
- **`client.inventory`**: Inventory levels and management
- **`client.costs`**: Cost of goods sold (COGS) management
- **`client.connections`**: Amazon connection status
- **`client.supply_chain`**: Restock suggestions
- **`client.warehouse`**: Warehouse and inbound shipment data
- **`client.notifications`**: Notification management

## Rate Limiting

The SDK includes built-in retry logic for rate-limited requests. When a rate limit is encountered (HTTP 429), the client will automatically retry with exponential backoff.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For support, please contact [support@sellerlegend.com](mailto:support@sellerlegend.com) or visit our [documentation](https://docs.sellerlegend.com/api).

## License

This SDK is licensed under the MIT License. See LICENSE file for details.