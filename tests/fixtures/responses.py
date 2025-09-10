"""
Test fixtures for API responses
"""

# Authentication responses
AUTH_SUCCESS_RESPONSE = {
    "token_type": "Bearer",
    "expires_in": 31536000,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "refresh_token": "def50200a7e5b8c9f7..."
}

AUTH_ERROR_RESPONSE = {
    "error": "invalid_client",
    "error_description": "Client authentication failed",
    "message": "Client authentication failed"
}

# User responses
USER_ME_RESPONSE = {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2023-01-01T00:00:00.000000Z",
    "updated_at": "2023-01-01T00:00:00.000000Z"
}

USER_ACCOUNTS_RESPONSE = {
    "data": [
        {
            "id": 1,
            "user_id": 123,
            "marketplace_id": "ATVPDKIKX0DER",
            "seller_id": "A1234567890",
            "name": "US Account",
            "region": "us-east-1",
            "created_at": "2023-01-01T00:00:00.000000Z"
        }
    ],
    "links": {
        "first": "https://api.sellerlegend.com/api/user/accounts?page=1",
        "last": "https://api.sellerlegend.com/api/user/accounts?page=1",
        "prev": None,
        "next": None
    },
    "meta": {
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "https://api.sellerlegend.com/api/user/accounts",
        "per_page": 20,
        "to": 1,
        "total": 1
    }
}

# Sales responses
ORDERS_RESPONSE = {
    "data": [
        {
            "id": 1001,
            "order_id": "123-4567890-1234567",
            "purchase_date": "2023-12-01T10:00:00Z",
            "order_status": "Shipped",
            "fulfillment_channel": "AFN",
            "sales_channel": "Amazon.com",
            "order_total": {
                "currency_code": "USD",
                "amount": "99.99"
            },
            "number_of_items_shipped": 1,
            "number_of_items_unshipped": 0
        }
    ],
    "links": {
        "first": "https://api.sellerlegend.com/api/orders?page=1",
        "last": "https://api.sellerlegend.com/api/orders?page=1",
        "prev": None,
        "next": None
    },
    "meta": {
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "https://api.sellerlegend.com/api/orders",
        "per_page": 500,
        "to": 1,
        "total": 1
    }
}

PRODUCTS_RESPONSE = {
    "data": [
        {
            "id": 2001,
            "sku": "TEST-SKU-001",
            "asin": "B000TEST001",
            "product_name": "Test Product",
            "listing_id": "LIST123456",
            "price": 29.99,
            "quantity": 100,
            "status": "Active",
            "created_at": "2023-01-01T00:00:00.000000Z"
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 500,
        "total": 1
    }
}

# Reports responses
REPORT_CREATE_RESPONSE = {
    "id": "3001",
    "status": "pending",
    "created_at": "2023-12-01T10:00:00Z",
    "message": "Report generation started"
}

REPORT_STATUS_RESPONSE = {
    "id": "3001",
    "status": "completed",
    "created_at": "2023-12-01T10:00:00Z",
    "completed_at": "2023-12-01T10:05:00Z",
    "download_url": "https://api.sellerlegend.com/api/reports/3001/download"
}

# Inventory responses
INVENTORY_RESPONSE = {
    "data": [
        {
            "id": 4001,
            "sku": "TEST-SKU-001",
            "asin": "B000TEST001",
            "fnsku": "X000TEST001",
            "product_name": "Test Product",
            "condition": "new",
            "total_supply_quantity": 150,
            "in_stock_supply_quantity": 100,
            "inbound_quantity": 50,
            "reserved_quantity": 10
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 500,
        "total": 1
    }
}

# Cost responses
COSTS_RESPONSE = {
    "data": [
        {
            "id": 5001,
            "sku": "TEST-SKU-001",
            "product_cost": 10.50,
            "shipping_cost": 2.50,
            "total_cost": 13.00,
            "currency": "USD",
            "effective_date": "2023-12-01",
            "created_at": "2023-12-01T00:00:00.000000Z"
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 100,
        "total": 1
    }
}

# Connections responses
CONNECTIONS_RESPONSE = {
    "data": [
        {
            "id": 6001,
            "platform": "amazon",
            "marketplace_id": "ATVPDKIKX0DER",
            "seller_id": "A1234567890",
            "status": "active",
            "created_at": "2023-01-01T00:00:00.000000Z",
            "last_synced_at": "2023-12-01T10:00:00.000000Z"
        }
    ]
}

# Supply chain responses
SUPPLY_CHAIN_RESPONSE = {
    "data": [
        {
            "id": 7001,
            "sku": "TEST-SKU-001",
            "supplier_name": "Test Supplier",
            "lead_time_days": 30,
            "minimum_order_quantity": 100,
            "unit_cost": 8.50,
            "currency": "USD"
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 100,
        "total": 1
    }
}

# Warehouse responses
WAREHOUSE_RESPONSE = {
    "data": [
        {
            "id": 8001,
            "name": "Main Warehouse",
            "code": "WH001",
            "address": "123 Warehouse St",
            "city": "Seattle",
            "state": "WA",
            "country": "US",
            "postal_code": "98101",
            "total_capacity": 10000,
            "used_capacity": 5500,
            "available_capacity": 4500
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 20,
        "total": 1
    }
}

# Notifications responses
NOTIFICATIONS_RESPONSE = {
    "data": [
        {
            "id": 9001,
            "type": "info",
            "title": "System Update",
            "message": "New features have been added",
            "read": False,
            "created_at": "2023-12-01T10:00:00.000000Z"
        }
    ],
    "meta": {
        "current_page": 1,
        "per_page": 50,
        "total": 1,
        "unread_count": 1
    }
}

# Error responses
VALIDATION_ERROR_RESPONSE = {
    "message": "The given data was invalid.",
    "errors": {
        "sku": ["The sku field is required."],
        "start_date": ["The start_date must be a valid date."]
    }
}

RATE_LIMIT_RESPONSE = {
    "message": "Too many requests. Please wait before trying again.",
    "retry_after": 60
}

NOT_FOUND_RESPONSE = {
    "message": "Resource not found"
}

SERVER_ERROR_RESPONSE = {
    "message": "Internal server error"
}