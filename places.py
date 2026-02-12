from typing import Optional

import requests

from .constants import API_DEFAULT_TIMEOUT, API_PLACES_BASE_URL
from .exceptions import PlacesFetchError


class Places:
    def get_place_id(self, country_name: str) -> Optional[int]:
        """
        Get the place ID for a country by name.

        Args:
            country_name: Name of the country to search for

        Returns:
            Place ID if found, None otherwise

        Raises:
            PlacesFetchError: If the API request fails
        """
        url = f"{API_PLACES_BASE_URL}?q={country_name}"

        try:
            response = requests.get(url, timeout=API_DEFAULT_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            raise PlacesFetchError(
                f"Failed to fetch place ID for '{country_name}': {e}"
            )

        data = response.json().get("results", [])

        # Find first valid country-level place (admin_level=0)
        for place in data:
            if place.get("admin_level") == 0:  # Countries have admin_level = 0
                return place["id"]

        return None
