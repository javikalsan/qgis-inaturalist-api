import unittest

import requests

from constants import API_DEFAULT_TIMEOUT, API_OBSERVATIONS_BASE_URL


class TestObservationsApiContract(unittest.TestCase):
    OBSERVATION_WITH_COORDINATES_ID = 73643333

    def setUp(self):
        self.api_url = API_OBSERVATIONS_BASE_URL
        self.observation_with_coordinates_id = self.OBSERVATION_WITH_COORDINATES_ID

    def fetch_observation_data(self, observation_id):
        params = {"id": observation_id}
        response = requests.get(
            self.api_url, params=params, timeout=API_DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    def validate_observation_structure(self, data):
        """Validate that API response contains all fields required by the application."""
        # Validate top-level structure
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)
        self.assertGreater(len(data["results"]), 0)

        observation = data["results"][0]

        # Validate geojson and coordinates structure (required by ObservationParser)
        self.assertIn("geojson", observation)
        geojson = observation["geojson"]
        self.assertIsInstance(geojson, dict)

        self.assertIn("coordinates", geojson)
        coordinates = geojson["coordinates"]
        self.assertIsInstance(coordinates, list)
        self.assertEqual(
            len(coordinates), 2, "Coordinates must have exactly 2 values [lon, lat]"
        )

        # Validate coordinates are numeric (can be int or float)
        lon, lat = coordinates[0], coordinates[1]
        self.assertIsInstance(lon, (int, float), "Longitude must be numeric")
        self.assertIsInstance(lat, (int, float), "Latitude must be numeric")

        # Validate taxon structure (required for species extraction)
        self.assertIn("taxon", observation)
        self.assertIsInstance(observation["taxon"], dict)
        self.assertIn("name", observation["taxon"])
        taxon_name = observation["taxon"]["name"]
        self.assertIsInstance(taxon_name, str)

        # Wikipedia URL should exist (can be None or string)
        self.assertIn("wikipedia_url", observation["taxon"])

        # Validate uri (required for observation_url)
        self.assertIn("uri", observation)
        self.assertIsInstance(observation["uri"], str)

        # Validate user structure (required for author_url)
        self.assertIn("user", observation)
        self.assertIsInstance(observation["user"], dict)
        self.assertIn("login", observation["user"])
        self.assertIsInstance(observation["user"]["login"], str)

        # Validate place_guess (required for location)
        self.assertIn("place_guess", observation)

        # Validate observed_on (required for date)
        self.assertIn("observed_on", observation)

        # Validate observation_photos structure (required for photo_url extraction)
        self.assertIn("observation_photos", observation)
        self.assertIsInstance(observation["observation_photos"], list)

        # If photos exist, validate the structure we need to extract URLs
        if observation["observation_photos"]:
            first_photo = observation["observation_photos"][0]
            self.assertIsInstance(first_photo, dict)
            if "photo" in first_photo:
                self.assertIsInstance(first_photo["photo"], dict)
                if "url" in first_photo["photo"]:
                    self.assertIsInstance(first_photo["photo"]["url"], str)

    def test_observations_api_contract__observations_has_coordinates(self):
        data = self.fetch_observation_data(self.observation_with_coordinates_id)
        self.validate_observation_structure(data)


if __name__ == "__main__":
    unittest.main()
