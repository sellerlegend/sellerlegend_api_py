# SellerLegend Python SDK Tests

This directory contains both unit tests (with mocks) and integration tests (with real API calls) for the SellerLegend Python SDK.

## Test Structure

```
tests/
├── fixtures/           # Test data and mock responses
│   └── responses.py    # Sample API responses for unit tests
├── integration/        # Integration tests (real API calls)
│   ├── config.py       # Configuration loader for integration tests
│   ├── test_auth_integration.py        # Authentication flow tests
│   ├── test_resources_integration.py   # Resource endpoint tests
│   └── test_validation_integration.py  # Validation and error handling tests
├── test_auth.py        # Unit tests for authentication
├── test_resources.py   # Unit tests for resource endpoints
├── test_validation.py  # Unit tests for validators
└── test_response_handling.py  # Unit tests for response/error handling
```

## Running Tests

### Unit Tests (No API calls - Safe to run anytime)

Unit tests use mocks and don't make actual API calls:

```bash
# Run all unit tests
./venv/bin/python -m pytest tests/ --ignore=tests/integration/

# Run specific test files
./venv/bin/python -m pytest tests/test_auth.py
./venv/bin/python -m pytest tests/test_resources.py
./venv/bin/python -m pytest tests/test_validation.py

# Run with coverage
./venv/bin/python -m pytest tests/ --ignore=tests/integration/ --cov=sellerlegend_api
```

### Integration Tests (Real API calls - Requires credentials)

Integration tests make actual API calls and require valid credentials.

#### Configuration

You need to provide API credentials via a `.env` file in the SDK root directory.

**Option 1: Interactive Setup (Recommended)**
```bash
# Run from the SDK root directory
python setup_test_config.py
```

This will:
1. Prompt you for OAuth Client ID and Secret
2. Open your browser for OAuth authorization
3. Automatically capture the authorization code
4. Exchange it for access and refresh tokens
5. Save everything to `.env` file

**Option 2: Manual Configuration**
```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
vim .env
```

Example `.env` file:
```env
SELLERLEGEND_BASE_URL=https://app.sellerlegend.com
SELLERLEGEND_CLIENT_ID=your_oauth_client_id
SELLERLEGEND_CLIENT_SECRET=your_oauth_client_secret
SELLERLEGEND_ACCESS_TOKEN=your_access_token
SELLERLEGEND_REFRESH_TOKEN=your_refresh_token
```

**Option 3: Environment Variables**
You can also set these as system environment variables if you prefer not to use a `.env` file.

#### Running Integration Tests

```bash
# Run all integration tests
./run_integration_tests.py

# Or use pytest directly
./venv/bin/python -m pytest tests/integration/ -v

# Run specific integration test
./venv/bin/python -m pytest tests/integration/test_auth_integration.py -v

# Run a specific test method
./venv/bin/python -m pytest tests/integration/test_auth_integration.py::TestAuthenticationIntegration::test_password_authentication -v
```

## Test Categories

### Unit Tests

**Authentication Tests (`test_auth.py`)**
- OAuth2 client initialization
- Authorization URL generation
- Token management (refresh, expiry, validation)
- All authentication grant types

**Resource Tests (`test_resources.py`)**
- All resource endpoints (User, Sales, Reports, Inventory, etc.)
- Request parameter handling
- Response parsing
- Pagination support

**Validation Tests (`test_validation.py`)**
- Date validation and formatting
- Pagination parameter validation
- Enum value validation
- Product/account parameter validation
- Cost and inventory parameter validation

**Response Handling Tests (`test_response_handling.py`)**
- HTTP error handling (401, 403, 404, 422, 429, 500)
- Response parsing (JSON, paginated, empty responses)
- Header validation (API version, Authorization)
- Connection error handling

### Integration Tests

**Authentication Integration (`test_auth_integration.py`)**
- Client credentials authentication
- Authorization code flow URL generation
- Token refresh flow
- Multiple authentication attempts
- Direct access token usage

**Resources Integration (`test_resources_integration.py`)**
- User endpoints (get_me, get_accounts)
- Sales endpoints (orders, statistics, transactions)
- Inventory management
- Cost tracking
- Connections and warehouses
- Notifications
- Report generation and status

**Validation Integration (`test_validation_integration.py`)**
- Parameter validation with real API
- Error response handling
- Rate limiting detection
- Connection and timeout errors

## Important Notes

### For Unit Tests
- ✅ Safe to run frequently
- ✅ No API credentials needed
- ✅ Fast execution
- ✅ No side effects

### For Integration Tests
- ⚠️ Requires valid API credentials
- ⚠️ Makes real API calls (may affect rate limits)
- ⚠️ May create/modify data in test account
- ⚠️ Slower execution
- ⚠️ Should be run in a test/staging environment

## Continuous Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: |
    pip install -r requirements.txt
    pip install -r test_requirements.txt
    pytest tests/ --ignore=tests/integration/ --cov=sellerlegend_api

- name: Run Integration Tests
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  env:
    SELLERLEGEND_TEST_CLIENT_ID: ${{ secrets.SELLERLEGEND_TEST_CLIENT_ID }}
    SELLERLEGEND_TEST_CLIENT_SECRET: ${{ secrets.SELLERLEGEND_TEST_CLIENT_SECRET }}
    SELLERLEGEND_TEST_USERNAME: ${{ secrets.SELLERLEGEND_TEST_USERNAME }}
    SELLERLEGEND_TEST_PASSWORD: ${{ secrets.SELLERLEGEND_TEST_PASSWORD }}
  run: |
    pytest tests/integration/ -v
```

## Troubleshooting

### Common Issues

1. **"Integration tests not configured"**
   - Set environment variables or create test_config.json
   - Ensure credentials are valid

2. **Authentication errors in integration tests**
   - Verify OAuth client ID and secret are correct
   - Check that the user credentials are valid
   - Ensure the OAuth app has proper permissions

3. **Rate limiting errors**
   - Reduce the frequency of test runs
   - Use a dedicated test account
   - Implement delays between tests if needed

4. **Import errors**
   - Install test requirements: `pip install -r test_requirements.txt`
   - Ensure the SDK is installed: `pip install -e .`

## Contributing

When adding new tests:

1. **Unit tests** should use mocks and not make real API calls
2. **Integration tests** should be idempotent when possible
3. Use meaningful test names that describe what is being tested
4. Add appropriate skip conditions for optional features
5. Document any special setup requirements