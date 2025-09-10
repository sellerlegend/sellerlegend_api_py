"""
SellerLegend API Parameter Validators

Provides validation utilities for API parameters.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date
from sellerlegend_api.exceptions import ValidationError


def validate_date(value: Any, param_name: str = "date") -> Optional[str]:
    """
    Validate and format date parameter.
    
    Args:
        value: Date value (string, date, or datetime)
        param_name: Parameter name for error messages
        
    Returns:
        Formatted date string (YYYY-MM-DD) or None
        
    Raises:
        ValidationError: If date format is invalid
    """
    if value is None:
        return None
        
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, str):
        try:
            # Try to parse the date string
            dt = datetime.strptime(value, '%Y-%m-%d')
            return value
        except ValueError:
            raise ValidationError(f"Invalid date format for {param_name}. Expected YYYY-MM-DD")
    else:
        raise ValidationError(f"Invalid date: {param_name} must be a date string, datetime, or date object")


def validate_date_range(
    start_date: Any, 
    end_date: Any
) -> Tuple[Optional[str], Optional[str]]:
    """
    Validate a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of (start_date, end_date) as strings
        
    Raises:
        ValidationError: If dates are invalid or end < start
    """
    start = validate_date(start_date, "start_date")
    end = validate_date(end_date, "end_date")
    
    if start and end:
        if start > end:
            raise ValidationError("End date must be after or equal to start date")
    
    return start, end


def validate_pagination(
    page: Optional[int] = None,
    per_page: Optional[int] = None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        Tuple of (page, per_page)
        
    Raises:
        ValidationError: If values are invalid
    """
    if page is not None:
        if not isinstance(page, int) or page < 1:
            raise ValidationError("Page must be greater than 0")
    
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1 or per_page > 1000:
            raise ValidationError("Per page must be between 1 and 1000")
    
    return page, per_page


def validate_enum(
    value: Any,
    allowed_values: List[Any],
    field_name: Optional[str] = None
) -> Any:
    """
    Validate enum parameter.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Field name for error messages
        
    Returns:
        The validated value
        
    Raises:
        ValidationError: If value is not in allowed values
    """
    if value is None:
        return None
        
    if value not in allowed_values:
        field = field_name or "Value"
        allowed_str = ", ".join(str(v) for v in allowed_values)
        raise ValidationError(f"{field} must be one of: {allowed_str}")
    
    return value


def validate_positive_integer(
    value: Any,
    field_name: Optional[str] = None
) -> Optional[int]:
    """
    Validate positive integer parameter.
    
    Args:
        value: Value to validate
        field_name: Field name for error messages
        
    Returns:
        The validated integer or None
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    if value is None:
        return None
    
    field = field_name or "Value"
    
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field} must be a positive integer")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field} must be a positive integer")


def validate_account_params(**kwargs) -> Dict[str, Any]:
    """
    Validate account selection parameters.
    
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    result = {}
    
    if 'account_id' in kwargs:
        account_id = validate_positive_integer(kwargs['account_id'], 'account_id')
        if account_id is not None:
            result['account_id'] = account_id
    
    if 'marketplace_id' in kwargs:
        marketplace_id = kwargs['marketplace_id']
        if marketplace_id is not None and marketplace_id == "":
            raise ValidationError("marketplace_id cannot be empty")
        if marketplace_id is not None:
            result['marketplace_id'] = marketplace_id
    
    return result


def validate_product_params(**kwargs) -> Dict[str, Any]:
    """
    Validate product selection parameters.
    
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    result = {}
    
    if 'sku' in kwargs:
        sku = kwargs['sku']
        if sku is not None:
            if sku == "":
                raise ValidationError("sku cannot be empty")
            result['sku'] = sku
    
    if 'asin' in kwargs:
        asin = kwargs['asin']
        if asin is not None:
            if len(asin) != 10:
                raise ValidationError("asin must be 10 characters")
            if not asin.startswith('B'):
                raise ValidationError("asin must start with B")
            result['asin'] = asin
    
    return result


def validate_report_params(**kwargs) -> Dict[str, Any]:
    """
    Validate report parameters.
    
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    result = {}
    
    if 'product_sku' in kwargs and kwargs['product_sku'] is not None:
        result['product_sku'] = kwargs['product_sku']
    
    if 'dps_date' in kwargs:
        dps_date = validate_date(kwargs['dps_date'], 'dps_date')
        if dps_date is not None:
            result['dps_date'] = dps_date
    
    if 'last_updated_date' in kwargs:
        last_updated = validate_date(kwargs['last_updated_date'], 'last_updated_date')
        if last_updated is not None:
            result['last_updated_date'] = last_updated
    
    return result


def validate_inventory_params(**kwargs) -> Dict[str, Any]:
    """
    Validate inventory parameters.
    
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    result = {}
    
    if 'sku' in kwargs and kwargs['sku'] is not None:
        result['sku'] = kwargs['sku']
    
    if 'warehouse_id' in kwargs:
        warehouse_id = validate_positive_integer(kwargs['warehouse_id'], 'warehouse_id')
        if warehouse_id is not None:
            result['warehouse_id'] = warehouse_id
    
    if 'quantity' in kwargs:
        quantity = kwargs['quantity']
        if quantity is not None:
            if not isinstance(quantity, (int, float)) or quantity < 0:
                raise ValidationError("quantity cannot be negative")
            result['quantity'] = quantity
    
    if 'location' in kwargs and kwargs['location'] is not None:
        result['location'] = kwargs['location']
    
    return result


def validate_cost_params(**kwargs) -> Dict[str, Any]:
    """
    Validate cost parameters.
    
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    result = {}
    
    if 'product_cost' in kwargs:
        cost = kwargs['product_cost']
        if cost is not None:
            if not isinstance(cost, (int, float)) or cost < 0:
                raise ValidationError("product_cost cannot be negative")
            result['product_cost'] = cost
    
    if 'shipping_cost' in kwargs:
        cost = kwargs['shipping_cost']
        if cost is not None:
            if not isinstance(cost, (int, float)) or cost < 0:
                raise ValidationError("shipping_cost cannot be negative")
            result['shipping_cost'] = cost
    
    if 'currency' in kwargs:
        currency = kwargs['currency']
        if currency is not None:
            if len(currency) != 3:
                raise ValidationError("currency must be a 3-letter code")
            if currency != currency.upper():
                raise ValidationError("currency must be uppercase")
            result['currency'] = currency
    
    return result


def validate_per_page(value: int) -> int:
    """
    Validate per_page parameter.
    
    Args:
        value: Number of items per page
        
    Returns:
        Validated per_page value
        
    Raises:
        ValidationError: If value is not valid
    """
    if value is None:
        raise ValidationError("per_page is required")
        
    allowed_values = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    return validate_enum(value, allowed_values, "per_page")


def validate_filter_by(value: str) -> str:
    """
    Validate filter_by parameter.
    
    Args:
        value: Filter field name
        
    Returns:
        Validated filter_by value
        
    Raises:
        ValidationError: If value is not valid
    """
    allowed_values = ['sku', 'asin', 'parent_asin']
    return validate_enum(value, allowed_values, "filter_by")


def validate_currency(value: str) -> str:
    """
    Validate currency code.
    
    Args:
        value: Currency code
        
    Returns:
        Validated currency code
        
    Raises:
        ValidationError: If currency code is invalid
    """
    if value is None:
        return None
        
    # Common currency codes
    allowed_currencies = [
        'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'INR', 'CNY',
        'MXN', 'BRL', 'SEK', 'SGD', 'AED', 'TRY', 'PLN', 'SAR'
    ]
    
    value = value.upper()
    return validate_enum(value, allowed_currencies, "currency")


def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values from parameters dictionary.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Cleaned parameters dictionary
    """
    return {k: v for k, v in params.items() if v is not None}