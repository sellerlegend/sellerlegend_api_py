# Changelog

All notable changes to the SellerLegend Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-10

### Added
- Initial release of the SellerLegend Python SDK
- OAuth2 authentication support (Authorization Code and Client Credentials flows)
- Comprehensive API coverage for all major endpoints:
  - User and account management
  - Sales data and statistics
  - Inventory management
  - Cost management (COGS)
  - Report generation and download
  - Warehouse and shipment data
  - Supply chain suggestions
  - Connections status
  - Notifications
- Automatic token refresh functionality
- Comprehensive error handling with specific exception types
- Full type hints for better IDE support
- Pagination support for list endpoints
- Request retry logic with exponential backoff
- API version header (v2) automatically included
- Context manager support for proper resource cleanup
- Comprehensive test suite (unit and integration tests)
- Example scripts for common use cases

### Security
- Secure OAuth2 implementation
- Token expiry handling with automatic refresh
- CSRF protection in Authorization Code flow

### Documentation
- Complete README with usage examples
- API reference documentation
- Example scripts for common scenarios
- Integration test setup guide

## [Unreleased]

### To Do
- Add async/await support for concurrent requests
- Add webhook support for real-time notifications
- Add CLI tool for common operations
- Add data export utilities (CSV, Excel)
- Add batch operation support
- Add request/response logging options
- Add metrics and telemetry support

---

For more information about changes, see the [commit history](https://github.com/sellerlegend/python-sdk/commits/main).