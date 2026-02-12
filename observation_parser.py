from typing import Any, Dict, Optional


class ObservationParser:
    """
    Parses raw observation data from iNaturalist API.
    """

    @staticmethod
    def parse_observation(observation: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse a single observation into a structured format.

        Args:
            observation: Raw observation data from API

        Returns:
            Parsed observation with standardized fields, or None if coordinates are missing
        """
        coordinates = ObservationParser.extract_coordinates(observation)
        if not coordinates:
            return None

        return {
            "lat": coordinates[0],
            "lon": coordinates[1],
            "species": ObservationParser.extract_species(observation),
            "date": observation.get("observed_on", "N/A"),
            "photo_url": ObservationParser.extract_photo_url(observation),
            "wikipedia_url": ObservationParser.extract_wikipedia_url(observation),
            "author_url": ObservationParser.extract_author_url(observation),
            "location": observation.get("place_guess", "N/A"),
            "observation_url": observation.get("uri", "N/A"),
        }

    @staticmethod
    def extract_coordinates(observation: Dict) -> Optional[tuple[float, float]]:
        """Extract latitude and longitude from observation."""
        geojson = observation.get("geojson")
        if not geojson:
            return None

        coordinates = geojson.get("coordinates", [])
        if len(coordinates) < 2:
            return None

        lon, lat = coordinates[0], coordinates[1]
        if lat is None or lon is None:
            return None

        return (lat, lon)

    @staticmethod
    def extract_species(observation: Dict) -> str:
        """Extract species name from observation."""
        taxon = observation.get("taxon")
        if taxon:
            return taxon.get("name", "Unknown")
        return "Unknown"

    @staticmethod
    def extract_photo_url(observation: Dict) -> str:
        """Extract photo URL from observation."""
        observation_photos = observation.get("observation_photos", [])

        for photo_entry in observation_photos:
            if "photo" in photo_entry:
                url = photo_entry["photo"].get("url")
                if url:
                    return url.replace("square", "original")

        return "N/A"

    @staticmethod
    def extract_wikipedia_url(observation: Dict) -> str:
        """Extract Wikipedia URL from observation taxon."""
        taxon = observation.get("taxon", {})
        return taxon.get("wikipedia_url", "N/A")

    @staticmethod
    def extract_author_url(observation: Dict) -> str:
        """Extract author profile URL from observation."""
        user = observation.get("user", {})
        login = user.get("login", "N/A")

        if login != "N/A":
            return f"https://www.inaturalist.org/people/{login}"

        return "N/A"
