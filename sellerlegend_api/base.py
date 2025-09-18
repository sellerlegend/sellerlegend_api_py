"""
SellerLegend API Base Client

Provides base functionality for API communication including request handling,
error processing, and response parsing.
"""

import json
import time
from typing import Optional, Dict, Any, Union, List
from urllib.parse import urljoin, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import OAuth2Client
from .exceptions import (
    SellerLegendAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    AccessDeniedError
)


class BaseClient:
    """Base client for SellerLegend API communication."""
    
    def __init__(
        self,
        auth_client: OAuth2Client,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """
        Initialize the base client.
        
        Args:
            auth_client: OAuth2 authentication client
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
        """
        self.auth_client = auth_client
        self.timeout = timeout
        self.base_url = auth_client.base_url
        self.api_base_url = urljoin(f"{self.base_url}/", "api/")
        
        # Configure session with retry strategy
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=backoff_factor,
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "SellerLegend-Python-SDK/1.0.0",
            "SellerLegend-Api-Version": "v2"
        })
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for API endpoint."""
        return urljoin(self.api_base_url, endpoint.lstrip('/'))
    
    def _prepare_params(self, params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Prepare query parameters, removing None values."""
        if not params:
            return None
        
        # Remove None values and convert non-string values to strings
        clean_params = {}
        for key, value in params.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    clean_params[key] = ",".join(str(v) for v in value)
                else:
                    clean_params[key] = str(value)
        
        return clean_params if clean_params else None
    
    def _prepare_data(self, data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Prepare request data as JSON."""
        if not data:
            return None
        return json.dumps(data)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and extract data.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response data
            
        Raises:
            Various SellerLegendAPIError subclasses based on response status
        """
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"message": response.text or "Unknown error"}
        
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            return response_data
        
        # Extract error message
        error_message = response_data.get("message", "Unknown error")
        
        # Map status codes to appropriate exceptions
        if status_code == 401:
            raise AuthenticationError(error_message, status_code, response_data)
        elif status_code == 403:
            raise AccessDeniedError(error_message, status_code, response_data)
        elif status_code == 404:
            raise NotFoundError(error_message, status_code, response_data)
        elif status_code == 422:
            raise ValidationError(error_message, status_code, response_data)
        elif status_code == 429:
            raise RateLimitError(error_message, status_code, response_data)
        elif 500 <= status_code < 600:
            raise ServerError(error_message, status_code, response_data)
        else:
            raise SellerLegendAPIError(error_message, status_code, response_data)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Additional headers
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Parsed response data
        """
        url = self._build_url(endpoint)
        
        # Prepare headers with authentication
        request_headers = {'SellerLegend-Api-Version': 'v2'}
        if headers:
            request_headers.update(headers)
        
        try:
            # Get authentication headers
            auth_headers = self.auth_client.get_authorization_header()
            request_headers.update(auth_headers)
        except AuthenticationError as e:
            # Re-raise authentication errors
            raise e
        
        # Prepare parameters and data
        clean_params = self._prepare_params(params)
        json_data = self._prepare_data(data) if method.upper() in ['POST', 'PUT', 'PATCH'] else None
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=clean_params,
                data=json_data,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )
            
            return self._handle_response(response)
            
        except requests.Timeout:
            raise SellerLegendAPIError(f"Request timed out after {self.timeout} seconds")
        except requests.ConnectionError as e:
            raise SellerLegendAPIError(f"Connection error: {str(e)}")
        except requests.RequestException as e:
            raise SellerLegendAPIError(f"Request failed: {str(e)}")
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, params=params, data=data, **kwargs)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, params=params, data=data, **kwargs)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._make_request("PATCH", endpoint, params=params, data=data, **kwargs)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, params=params, **kwargs)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Check API service status.
        
        Returns:
            Service status information
        """
        return self.get("service-status")