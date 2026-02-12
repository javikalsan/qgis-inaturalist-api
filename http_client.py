from typing import Any, Dict, Optional

import requests

from .constants import API_DEFAULT_TIMEOUT
from .exceptions import InaturalistAPIError


class HTTPClient:
    """Handles HTTP requests with consistent error handling and timeout configuration."""

    def __init__(self, timeout: int = API_DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session: Optional[requests.Session] = None

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the specified URL.

        Args:
            url: The URL to request
            params: Optional query parameters

        Returns:
            JSON response as a dictionary

        Raises:
            InaturalistAPIError: If the request fails
        """
        try:
            session = self.session or requests
            response = session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise InaturalistAPIError(f"API request failed: {e}")
