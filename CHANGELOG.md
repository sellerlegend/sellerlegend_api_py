# Changelog

All notable changes to the SellerLegend Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-01-19

### Changed
- Updated all repository URLs to the correct GitHub repository (sellerlegend/sellerlegend_api_py)
- Fixed broken links in documentation and package metadata

## [1.0.2] - 2025-01-19

### Added
- Release automation script for streamlined package publishing
- Error code support in AuthenticationError for better error handling

### Fixed
- Removed automatic token refresh in `ensure_valid_token()` to allow proper token persistence
- Now applications can handle token refresh and storage appropriately
- Token expiration throws specific error codes: `TOKEN_EXPIRED` and `TOKEN_EXPIRED_NO_REFRESH`

### Changed
- Token validation now only checks validity without attempting automatic refresh
- This allows users to catch expiration, refresh tokens manually, and store new tokens in their database/files

## [1.0.1] - 2025-01-19

### Changed
- Updated documentation URLs to point to dashboard.sellerlegend.com/api-docs
- Minor documentation improvements

### Fixed
- Fixed report download example to use proper 3-step process (request, check status, download)
- Removed invalid `create_and_download_report` convenience method from client

## [1.0.0] - 2025-01-18

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

---

For more information about changes, see the [commit history](https://github.com/sellerlegend/sellerlegend_api_py/commits/main).