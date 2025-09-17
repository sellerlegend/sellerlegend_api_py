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

### Step 1: Obtain API Credentials

Before using the API, you need to register your application in SellerLegend:

1. Log in to your SellerLegend account
2. Navigate to **Admin → Developers**
3. Click on **"Create New Client"**
4. Fill in your application details:
   - **Name:** Your application name
   - **Redirect URL:** Your OAuth callback URL (e.g., `https://yourapp.com/callback`)
5. Click **"Create"** to generate your credentials

**Important:** Save your **Client ID** and **Client Secret** immediately. The Client Secret will only be shown once for security reasons.

### Step 2: OAuth2 Authorization Code Flow (The ONLY Method for Full API Access)

```python
from sellerlegend_api import SellerLegendClient
import time

# Initialize the client with credentials from Step 1
client = SellerLegendClient(
    client_id="your_oauth_client_id",      # From Admin → Developers
    client_secret="your_oauth_client_secret",  # From Admin → Developers
    base_url="https://app.sellerlegend.com"
)

# Step 1: Get authorization URL
auth_url, state = client.get_authorization_url()
print(f"Please visit: {auth_url}")
print(f"State (save for verification): {state}")

# Step 2: User authorizes and you receive a code at your callback URL
code = input("Enter the authorization code: ")

# Step 3: Exchange code for tokens
token_info = client.authenticate_with_code(code, state)

# Step 4: CRITICAL - Store BOTH tokens in your database
store_in_database(
    access_token=token_info['access_token'],
    refresh_token=token_info['refresh_token'],  # MUST store this!
    expires_at=time.time() + token_info['expires_in']
)

print(f"Authentication successful! Token expires in {token_info['expires_in']} seconds")
```

## Authentication

⚠️ **CRITICAL INFORMATION**:
- **Only the OAuth 2.0 Authorization Code flow provides full API access**
- Personal Access Tokens are **NOT** supported
- Direct access tokens are **NOT** supported
- Password Grant is **NOT** supported
- Client Credentials Grant only provides access to service status endpoint

### 1. OAuth 2.0 Authorization Code Flow - Complete Implementation

This is the **ONLY** way to get full API access. You MUST:
1. Implement the complete OAuth flow
2. Store tokens securely in a database
3. Handle token refresh properly
4. **Update refresh tokens after each refresh** (old ones become invalid)

#### Step-by-Step Implementation:

```python
import time
import sqlite3
from sellerlegend_api import SellerLegendClient

class SellerLegendTokenManager:
    """Complete token management with database storage."""

    def __init__(self, client_id, client_secret, db_path="tokens.db"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://app.sellerlegend.com"
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create tokens table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token TEXT NOT NULL UNIQUE,
                refresh_token TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def complete_oauth_flow(self, redirect_uri="http://localhost:5001/callback"):
        """Complete OAuth authorization flow."""
        # Initialize client
        client = SellerLegendClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            base_url=self.base_url
        )

        # Step 1: Get authorization URL
        auth_url, state = client.get_authorization_url(redirect_uri)

        print("=== OAuth Authorization Required ===")
        print(f"1. Visit this URL: {auth_url}")
        print(f"2. Log in and authorize the application")
        print(f"3. You'll be redirected to: {redirect_uri}?code=AUTH_CODE&state={state}")
        print("")

        # Step 2: Get authorization code from user
        code = input("Enter the authorization code from the redirect URL: ")

        # Step 3: Exchange code for tokens
        try:
            token_info = client.authenticate_with_code(code, state)

            # Step 4: Store tokens in database
            self.store_tokens(token_info)

            print("✅ Authentication successful!")
            print(f"Access token expires in: {token_info['expires_in']} seconds")
            print(f"Refresh token expires in: 30 days")

            return token_info

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            raise

    def store_tokens(self, token_info):
        """
        Store tokens in database.
        CRITICAL: Must store BOTH access and refresh tokens!
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        expires_at = int(time.time() + token_info['expires_in'])
        created_at = int(time.time())

        # Delete old tokens (optional, for single-user apps)
        cursor.execute("DELETE FROM oauth_tokens")

        # Insert new tokens
        cursor.execute("""
            INSERT INTO oauth_tokens
            (access_token, refresh_token, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            token_info['access_token'],
            token_info['refresh_token'],  # CRITICAL: Must store refresh token!
            expires_at,
            created_at
        ))

        conn.commit()
        conn.close()

        print("✅ Tokens stored securely in database")

    def get_valid_client(self):
        """
        Get an authenticated client, refreshing token if needed.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get most recent tokens
        cursor.execute("""
            SELECT * FROM oauth_tokens
            ORDER BY created_at DESC
            LIMIT 1
        """)

        tokens = cursor.fetchone()
        conn.close()

        if not tokens:
            print("❌ No tokens found. Please run complete_oauth_flow() first.")
            raise Exception("Not authenticated")

        current_time = int(time.time())

        # Check if token needs refresh (5 minute buffer)
        if tokens['expires_at'] <= current_time + 300:
            print("⚠️ Token expired or expiring soon, refreshing...")
            return self.refresh_and_get_client(tokens['refresh_token'])

        # Return client with valid token
        return SellerLegendClient(
            base_url=self.base_url,
            access_token=tokens['access_token']
        )

    def refresh_and_get_client(self, refresh_token):
        """
        Refresh tokens and return authenticated client.

        ⚠️ CRITICAL: When refreshing, you get a NEW refresh token!
        The old refresh token becomes INVALID immediately!
        """
        client = SellerLegendClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            base_url=self.base_url
        )

        try:
            # Get new tokens
            new_tokens = client.refresh_access_token(refresh_token)

            # CRITICAL: Store the NEW tokens (including refresh token!)
            self.store_tokens(new_tokens)

            print("✅ Tokens refreshed successfully")
            print("⚠️ WARNING: Old refresh token is now INVALID!")

            # Return client with new access token
            return SellerLegendClient(
                base_url=self.base_url,
                access_token=new_tokens['access_token']
            )

        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            print("User must re-authenticate with OAuth flow")
            raise

# Usage Example
if __name__ == "__main__":
    # Initialize token manager
    manager = SellerLegendTokenManager(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET"
    )

    # First time: Complete OAuth flow
    # Uncomment this line for initial setup:
    # manager.complete_oauth_flow()

    # Subsequent uses: Get authenticated client
    try:
        client = manager.get_valid_client()

        # Now you can make API calls
        user = client.user.get_me()
        print(f"Authenticated as: {user['user']['name']}")

        # Get accounts
        accounts = client.user.get_accounts()
        for account in accounts['accounts']:
            print(f"Account: {account['account_title']}")

        # Get sales data
        orders = client.sales.get_orders(
            per_page=500,
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        print(f"Found {len(orders.get('data', []))} orders")

    except Exception as e:
        print(f"Error: {e}")
        print("Please run complete_oauth_flow() to authenticate")
```

### 2. Token Refresh - Critical Information

⚠️ **CRITICAL POINTS ABOUT TOKEN REFRESH**:

1. **NEW Refresh Token**: When you refresh an access token, you receive a NEW refresh token
2. **Old Token Invalid**: The old refresh token becomes invalid IMMEDIATELY
3. **Must Update Storage**: You MUST update your stored refresh token every time
4. **Atomic Updates**: Use database transactions to prevent token loss
5. **Handle Failures**: If refresh fails, user must re-authenticate

```python
def refresh_tokens_safely(old_refresh_token, client_id, client_secret):
    """
    Safe token refresh with proper error handling.
    """
    client = SellerLegendClient(
        client_id=client_id,
        client_secret=client_secret,
        base_url="https://app.sellerlegend.com"
    )

    try:
        # Refresh tokens
        new_tokens = client.refresh_access_token(old_refresh_token)

        # CRITICAL: You now have NEW tokens
        # The old refresh token is INVALID!

        # Store BOTH new tokens immediately
        with database.transaction():  # Use transaction for safety
            database.execute("""
                UPDATE oauth_tokens SET
                    access_token = ?,
                    refresh_token = ?,  # NEW refresh token!
                    expires_at = ?,
                    updated_at = ?
                WHERE refresh_token = ?
            """, [
                new_tokens['access_token'],
                new_tokens['refresh_token'],  # Must store the NEW one!
                time.time() + new_tokens['expires_in'],
                time.time(),
                old_refresh_token  # Match on old token
            ])

        print("✅ Tokens refreshed and stored")
        print("⚠️ Old refresh token is now invalid!")

        return new_tokens

    except Exception as e:
        # Refresh failed - tokens may be invalid
        print(f"❌ Token refresh failed: {e}")

        # Mark tokens as invalid in database
        database.execute(
            "UPDATE oauth_tokens SET expires_at = 0 WHERE refresh_token = ?",
            [old_refresh_token]
        )

        # User must re-authenticate
        raise Exception("Token refresh failed. User must re-authenticate.")
```

### 3. Common Pitfalls and Solutions

#### Pitfall 1: Not Storing Refresh Token
```python
# ❌ WRONG - Only storing access token
database.save(access_token=token_info['access_token'])

# ✅ CORRECT - Store both tokens
database.save(
    access_token=token_info['access_token'],
    refresh_token=token_info['refresh_token']
)
```

#### Pitfall 2: Not Updating Refresh Token After Refresh
```python
# ❌ WRONG - Not updating refresh token
new_tokens = client.refresh_access_token(old_refresh_token)
database.update(access_token=new_tokens['access_token'])  # Missing refresh token!

# ✅ CORRECT - Update both tokens
new_tokens = client.refresh_access_token(old_refresh_token)
database.update(
    access_token=new_tokens['access_token'],
    refresh_token=new_tokens['refresh_token']  # Must update this too!
)
```

#### Pitfall 3: Using Expired Refresh Token
```python
# ❌ WRONG - Using old refresh token after refresh
tokens1 = client.refresh_access_token(refresh_token)
# ... later ...
tokens2 = client.refresh_access_token(refresh_token)  # Will fail!

# ✅ CORRECT - Use the new refresh token
tokens1 = client.refresh_access_token(old_refresh_token)
# ... later ...
tokens2 = client.refresh_access_token(tokens1['refresh_token'])  # Use new token
```

## API Usage Examples

Once you have a valid authenticated client, you can access all API endpoints:

### Sales Data

```python
# Get authenticated client
client = token_manager.get_valid_client()

# Get recent orders
orders = client.sales.get_orders(
    per_page=500,
    start_date="2023-12-01",
    end_date="2023-12-31"
)

# Get sales statistics
stats = client.sales.get_statistics_dashboard(
    view_by="product",
    group_by="sku",
    per_page=1000,
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

try:
    # Get authenticated client
    client = token_manager.get_valid_client()

    # Make API calls
    orders = client.sales.get_orders(per_page=500)

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Token may be expired, try refresh or re-authenticate

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Response data: {e.response_data}")

except NotFoundError as e:
    print(f"Resource not found: {e.message}")

except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    # Implement backoff strategy

except ServerError as e:
    print(f"Server error: {e.message}")
```

## Configuration

### Timeout and Retry Settings

```python
client = SellerLegendClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    base_url="https://app.sellerlegend.com",
    timeout=60,          # 60 second timeout
    max_retries=5,       # Retry up to 5 times
    backoff_factor=0.5   # Backoff factor for retries
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

## Important Security Notes

1. **Never commit credentials**: Keep your `client_id` and `client_secret` secure
2. **Use environment variables**: Store sensitive data in `.env` files
3. **Secure token storage**: Always store tokens in a database, never in files or cookies
4. **Use HTTPS**: Always use HTTPS for callbacks and API calls
5. **Validate state parameter**: Always validate the state parameter to prevent CSRF attacks

## Database Schema Example

```sql
-- Recommended schema for token storage
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- Your application's user ID
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER,
    UNIQUE(access_token)
);

-- Index for faster lookups
CREATE INDEX idx_user_id ON oauth_tokens(user_id);
CREATE INDEX idx_expires_at ON oauth_tokens(expires_at);
```

## Troubleshooting

### "Unauthenticated" Error
- Token may be expired - check `expires_at` timestamp
- Try refreshing the token using the refresh token
- If refresh fails, user must re-authenticate

### "Access Denied" Error
- User may not have API access enabled
- Check account permissions in SellerLegend

### Token Refresh Fails
- Refresh token may be expired (30 days)
- Refresh token may have been used already (they're single-use)
- User must complete OAuth flow again

### Rate Limiting
- Implement exponential backoff
- Cache frequently accessed data
- Use batch endpoints where available

## Support

For support, please contact [support@sellerlegend.com](mailto:support@sellerlegend.com) or visit our [documentation](https://docs.sellerlegend.com/api).

## License

This SDK is licensed under the MIT License. See LICENSE file for details.