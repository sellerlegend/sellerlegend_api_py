"""
Tests for parameter validation
"""

import pytest
from datetime import date, datetime
from sellerlegend_api.validators import (
    validate_date,
    validate_date_range,
    validate_pagination,
    validate_enum,
    validate_positive_integer,
    validate_account_params,
    validate_product_params,
    validate_report_params,
    validate_inventory_params,
    validate_cost_params
)
from sellerlegend_api.exceptions import ValidationError


class TestDateValidation:
    """Test date validation functions."""
    
    def test_validate_date_valid_string(self):
        """Test valid date string."""
        result = validate_date("2023-12-01")
        assert result == "2023-12-01"
    
    def test_validate_date_valid_date_object(self):
        """Test valid date object."""
        d = date(2023, 12, 1)
        result = validate_date(d)
        assert result == "2023-12-01"
    
    def test_validate_date_valid_datetime_object(self):
        """Test valid datetime object."""
        dt = datetime(2023, 12, 1, 10, 30, 45)
        result = validate_date(dt)
        assert result == "2023-12-01"
    
    def test_validate_date_none(self):
        """Test None date (optional)."""
        result = validate_date(None)
        assert result is None
    
    def test_validate_date_invalid_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date("12/01/2023")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_validate_date_invalid_date(self):
        """Test invalid date values."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date("2023-13-01")  # Invalid month
        assert "Invalid date" in str(exc_info.value)
    
    def test_validate_date_range_valid(self):
        """Test valid date range."""
        start, end = validate_date_range("2023-12-01", "2023-12-31")
        assert start == "2023-12-01"
        assert end == "2023-12-31"
    
    def test_validate_date_range_end_before_start(self):
        """Test date range with end before start."""
        with pytest.raises(ValidationError) as exc_info:
            validate_date_range("2023-12-31", "2023-12-01")
        assert "End date must be after or equal to start date" in str(exc_info.value)
    
    def test_validate_date_range_optional(self):
        """Test optional date range."""
        start, end = validate_date_range(None, None)
        assert start is None
        assert end is None
    
    def test_validate_date_range_partial(self):
        """Test partial date range."""
        start, end = validate_date_range("2023-12-01", None)
        assert start == "2023-12-01"
        assert end is None


class TestPaginationValidation:
    """Test pagination validation."""
    
    def test_validate_pagination_valid(self):
        """Test valid pagination parameters."""
        page, per_page = validate_pagination(2, 50)
        assert page == 2
        assert per_page == 50
    
    def test_validate_pagination_defaults(self):
        """Test pagination with None values."""
        page, per_page = validate_pagination(None, None)
        assert page is None
        assert per_page is None
    
    def test_validate_pagination_invalid_page(self):
        """Test invalid page number."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination(0, 50)
        assert "Page must be greater than 0" in str(exc_info.value)
    
    def test_validate_pagination_invalid_per_page_low(self):
        """Test per_page too low."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination(1, 0)
        assert "Per page must be between 1 and 1000" in str(exc_info.value)
    
    def test_validate_pagination_invalid_per_page_high(self):
        """Test per_page too high."""
        with pytest.raises(ValidationError) as exc_info:
            validate_pagination(1, 1001)
        assert "Per page must be between 1 and 1000" in str(exc_info.value)


class TestEnumValidation:
    """Test enum validation."""
    
    def test_validate_enum_valid(self):
        """Test valid enum value."""
        result = validate_enum("active", ["active", "inactive", "pending"])
        assert result == "active"
    
    def test_validate_enum_none(self):
        """Test None enum value."""
        result = validate_enum(None, ["active", "inactive"])
        assert result is None
    
    def test_validate_enum_invalid(self):
        """Test invalid enum value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum("invalid", ["active", "inactive"])
        assert "must be one of: active, inactive" in str(exc_info.value)
    
    def test_validate_enum_with_field_name(self):
        """Test enum validation with field name."""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum("invalid", ["active", "inactive"], "status")
        assert "status must be one of: active, inactive" in str(exc_info.value)


class TestPositiveIntegerValidation:
    """Test positive integer validation."""
    
    def test_validate_positive_integer_valid(self):
        """Test valid positive integer."""
        result = validate_positive_integer(42)
        assert result == 42
    
    def test_validate_positive_integer_none(self):
        """Test None value."""
        result = validate_positive_integer(None)
        assert result is None
    
    def test_validate_positive_integer_zero(self):
        """Test zero value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(0)
        assert "must be a positive integer" in str(exc_info.value)
    
    def test_validate_positive_integer_negative(self):
        """Test negative value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(-5)
        assert "must be a positive integer" in str(exc_info.value)
    
    def test_validate_positive_integer_with_field_name(self):
        """Test with field name."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(-5, "quantity")
        assert "quantity must be a positive integer" in str(exc_info.value)


class TestAccountParamsValidation:
    """Test account parameters validation."""
    
    def test_validate_account_params_valid(self):
        """Test valid account parameters."""
        result = validate_account_params(
            account_id=123,
            marketplace_id="ATVPDKIKX0DER"
        )
        assert result["account_id"] == 123
        assert result["marketplace_id"] == "ATVPDKIKX0DER"
    
    def test_validate_account_params_empty(self):
        """Test empty account parameters."""
        result = validate_account_params()
        assert result == {}
    
    def test_validate_account_params_invalid_account_id(self):
        """Test invalid account ID."""
        with pytest.raises(ValidationError) as exc_info:
            validate_account_params(account_id=0)
        assert "account_id must be a positive integer" in str(exc_info.value)
    
    def test_validate_account_params_invalid_marketplace(self):
        """Test empty marketplace ID."""
        with pytest.raises(ValidationError) as exc_info:
            validate_account_params(marketplace_id="")
        assert "marketplace_id cannot be empty" in str(exc_info.value)


class TestProductParamsValidation:
    """Test product parameters validation."""
    
    def test_validate_product_params_valid_sku(self):
        """Test valid SKU parameter."""
        result = validate_product_params(sku="TEST-SKU-001")
        assert result["sku"] == "TEST-SKU-001"
    
    def test_validate_product_params_valid_asin(self):
        """Test valid ASIN parameter."""
        result = validate_product_params(asin="B000TEST01")
        assert result["asin"] == "B000TEST01"
    
    def test_validate_product_params_both(self):
        """Test both SKU and ASIN."""
        result = validate_product_params(
            sku="TEST-SKU-001",
            asin="B000TEST01"
        )
        assert result["sku"] == "TEST-SKU-001"
        assert result["asin"] == "B000TEST01"
    
    def test_validate_product_params_empty_sku(self):
        """Test empty SKU."""
        with pytest.raises(ValidationError) as exc_info:
            validate_product_params(sku="")
        assert "sku cannot be empty" in str(exc_info.value)
    
    def test_validate_product_params_invalid_asin_length(self):
        """Test invalid ASIN length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_product_params(asin="B123")
        assert "asin must be 10 characters" in str(exc_info.value)
    
    def test_validate_product_params_invalid_asin_format(self):
        """Test invalid ASIN format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_product_params(asin="1234567890")
        assert "asin must start with B" in str(exc_info.value)


class TestReportParamsValidation:
    """Test report parameters validation."""
    
    def test_validate_report_params_valid(self):
        """Test valid report parameters."""
        result = validate_report_params(
            product_sku="TEST-SKU-001",
            dps_date="2023-12-01",
            last_updated_date="2023-12-31"
        )
        assert result["product_sku"] == "TEST-SKU-001"
        assert result["dps_date"] == "2023-12-01"
        assert result["last_updated_date"] == "2023-12-31"
    
    def test_validate_report_params_empty(self):
        """Test empty report parameters."""
        result = validate_report_params()
        assert result == {}
    
    def test_validate_report_params_invalid_date(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_report_params(dps_date="12/01/2023")
        assert "Invalid date format" in str(exc_info.value)


class TestInventoryParamsValidation:
    """Test inventory parameters validation."""
    
    def test_validate_inventory_params_valid(self):
        """Test valid inventory parameters."""
        result = validate_inventory_params(
            sku="TEST-SKU-001",
            warehouse_id=123,
            quantity=100,
            location="A1-B2-C3"
        )
        assert result["sku"] == "TEST-SKU-001"
        assert result["warehouse_id"] == 123
        assert result["quantity"] == 100
        assert result["location"] == "A1-B2-C3"
    
    def test_validate_inventory_params_invalid_quantity(self):
        """Test invalid quantity."""
        with pytest.raises(ValidationError) as exc_info:
            validate_inventory_params(quantity=-10)
        assert "quantity cannot be negative" in str(exc_info.value)
    
    def test_validate_inventory_params_invalid_warehouse(self):
        """Test invalid warehouse ID."""
        with pytest.raises(ValidationError) as exc_info:
            validate_inventory_params(warehouse_id=0)
        assert "warehouse_id must be a positive integer" in str(exc_info.value)


class TestCostParamsValidation:
    """Test cost parameters validation."""
    
    def test_validate_cost_params_valid(self):
        """Test valid cost parameters."""
        result = validate_cost_params(
            product_cost=10.50,
            shipping_cost=2.50,
            currency="USD"
        )
        assert result["product_cost"] == 10.50
        assert result["shipping_cost"] == 2.50
        assert result["currency"] == "USD"
    
    def test_validate_cost_params_negative_cost(self):
        """Test negative product cost."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cost_params(product_cost=-5.00)
        assert "product_cost cannot be negative" in str(exc_info.value)
    
    def test_validate_cost_params_invalid_currency(self):
        """Test invalid currency code."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cost_params(currency="US")
        assert "currency must be a 3-letter code" in str(exc_info.value)
    
    def test_validate_cost_params_non_uppercase_currency(self):
        """Test non-uppercase currency."""
        with pytest.raises(ValidationError) as exc_info:
            validate_cost_params(currency="usd")
        assert "currency must be uppercase" in str(exc_info.value)