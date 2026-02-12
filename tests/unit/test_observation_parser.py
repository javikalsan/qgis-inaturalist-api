import json
import os
import unittest

from observation_parser import ObservationParser


class TestObservationParser(unittest.TestCase):
    """Test cases for ObservationParser methods."""

    @classmethod
    def setUpClass(cls):
        """Load test data from JSON file once for all tests."""
        test_data_path = os.path.join(
            os.path.dirname(__file__), "../data/observation_with_coordinates.json"
        )
        with open(test_data_path, "r", encoding="utf-8") as test_data_file:
            data = json.load(test_data_file)
            cls.real_observation = data["results"][0]

    def test_parse_observation_missing_coordinates(self):
        """Test that parsing returns None when coordinates are missing."""
        observation = self.real_observation.copy()
        observation.pop("geojson", None)

        result = ObservationParser.parse_observation(observation)

        self.assertIsNone(result)

    def test_parse_observation_with_null_coordinates(self):
        """Test handling of null coordinates."""
        observation = self.real_observation.copy()
        observation["geojson"] = {"coordinates": [None, None]}

        result = ObservationParser.parse_observation(observation)

        self.assertIsNone(result)

    def test_parse_observation_missing_taxon(self):
        """Test parsing observation without taxon information."""
        observation = self.real_observation.copy()
        observation.pop("taxon", None)

        result = ObservationParser.parse_observation(observation)

        self.assertIsNotNone(result)
        self.assertEqual(result["species"], "Unknown")

    def test_parse_observation_missing_optional_fields(self):
        """Test parsing observation with minimal required data."""
        observation = {
            "geojson": self.real_observation.get("geojson"),
        }

        result = ObservationParser.parse_observation(observation)

        self.assertIsNotNone(result)
        coords = self.real_observation["geojson"]["coordinates"]
        self.assertEqual(result["lat"], coords[1])
        self.assertEqual(result["lon"], coords[0])
        self.assertEqual(result["species"], "Unknown")
        self.assertEqual(result["date"], "N/A")
        self.assertEqual(result["photo_url"], "N/A")
        self.assertEqual(result["wikipedia_url"], "N/A")
        self.assertEqual(result["author_url"], "N/A")
        self.assertEqual(result["location"], "N/A")
        self.assertEqual(result["observation_url"], "N/A")

    def test_extract_coordinates_valid(self):
        """Test extracting valid coordinates."""
        observation = {"geojson": self.real_observation.get("geojson")}

        coords = ObservationParser.extract_coordinates(observation)

        self.assertIsNotNone(coords)
        real_coords = self.real_observation["geojson"]["coordinates"]
        self.assertEqual(coords, (real_coords[1], real_coords[0]))

    def test_extract_coordinates_no_geojson(self):
        """Test extracting coordinates when geojson is missing."""
        observation = {}

        coords = ObservationParser.extract_coordinates(observation)

        self.assertIsNone(coords)

    def test_extract_coordinates_empty_list(self):
        """Test extracting coordinates with empty coordinate list."""
        observation = {"geojson": {"coordinates": []}}

        coords = ObservationParser.extract_coordinates(observation)

        self.assertIsNone(coords)

    def test_extract_coordinates_partial_list(self):
        """Test extracting coordinates with only one coordinate."""
        observation = self.real_observation.copy()
        real_coords = self.real_observation["geojson"]["coordinates"]
        observation["geojson"] = {"coordinates": [real_coords[0]]}

        coords = ObservationParser.extract_coordinates(observation)

        self.assertIsNone(coords)

    def test_extract_species_with_taxon(self):
        """Test extracting species name when taxon is present."""
        observation = {"taxon": self.real_observation.get("taxon")}

        species = ObservationParser.extract_species(observation)

        self.assertEqual(species, self.real_observation["taxon"]["name"])

    def test_extract_species_with_taxon_no_name(self):
        """Test extracting species when taxon exists but has no name."""
        observation = {"taxon": {}}

        species = ObservationParser.extract_species(observation)

        self.assertEqual(species, "Unknown")

    def test_extract_species_no_taxon(self):
        """Test extracting species when taxon is missing."""
        observation = {}

        species = ObservationParser.extract_species(observation)

        self.assertEqual(species, "Unknown")

    def test_extract_photo_url_with_photos(self):
        """Test extracting photo URL when photos exist."""
        observation = {
            "observation_photos": self.real_observation.get("observation_photos", [])
        }

        photo_url = ObservationParser.extract_photo_url(observation)

        if self.real_observation.get("observation_photos"):
            self.assertIn("original", photo_url)
            self.assertNotIn("square", photo_url)

    def test_extract_photo_url_multiple_photos(self):
        """Test extracting photo URL when multiple photos exist - should return first."""
        photos = self.real_observation.get("observation_photos", [])

        # Skip if no photos in test data
        if not photos:
            self.skipTest("No photos in test data to duplicate")

        # Create observation with duplicated photos to ensure multiple exist
        observation = self.real_observation.copy()
        observation["observation_photos"] = photos + photos

        photo_url = ObservationParser.extract_photo_url(observation)

        self.assertIn("original", photo_url)
        self.assertNotIn("square", photo_url)

    def test_extract_photo_url_no_photos(self):
        """Test extracting photo URL when no photos exist."""
        observation = {"observation_photos": []}

        photo_url = ObservationParser.extract_photo_url(observation)

        self.assertEqual(photo_url, "N/A")

    def test_extract_photo_url_missing_photo_field(self):
        """Test extracting photo URL when photo field is missing."""
        observation = {"observation_photos": [{"other_field": "value"}]}

        photo_url = ObservationParser.extract_photo_url(observation)

        self.assertEqual(photo_url, "N/A")

    def test_extract_photo_url_photo_without_url(self):
        """Test extracting photo URL when photo has no URL."""
        observation = {"observation_photos": [{"photo": {}}]}

        photo_url = ObservationParser.extract_photo_url(observation)

        self.assertEqual(photo_url, "N/A")

    def test_extract_wikipedia_url_with_taxon(self):
        """Test extracting Wikipedia URL when present."""
        observation = {"taxon": self.real_observation.get("taxon", {})}

        wikipedia_url = ObservationParser.extract_wikipedia_url(observation)

        expected = self.real_observation.get("taxon", {}).get("wikipedia_url", "N/A")
        self.assertEqual(wikipedia_url, expected)

    def test_extract_wikipedia_url_no_url(self):
        """Test extracting Wikipedia URL when not present."""
        observation = {"taxon": {}}

        wikipedia_url = ObservationParser.extract_wikipedia_url(observation)

        self.assertEqual(wikipedia_url, "N/A")

    def test_extract_wikipedia_url_no_taxon(self):
        """Test extracting Wikipedia URL when taxon is missing."""
        observation = {}

        wikipedia_url = ObservationParser.extract_wikipedia_url(observation)

        self.assertEqual(wikipedia_url, "N/A")

    def test_extract_author_url_with_user(self):
        """Test extracting author URL when user is present."""
        observation = {"user": self.real_observation.get("user", {})}

        author_url = ObservationParser.extract_author_url(observation)

        expected_login = self.real_observation.get("user", {}).get("login")
        self.assertEqual(
            author_url, f"https://www.inaturalist.org/people/{expected_login}"
        )

    def test_extract_author_url_no_login(self):
        """Test extracting author URL when login is missing."""
        observation = {"user": {}}

        author_url = ObservationParser.extract_author_url(observation)

        self.assertEqual(author_url, "N/A")

    def test_extract_author_url_no_user(self):
        """Test extracting author URL when user is missing."""
        observation = {}

        author_url = ObservationParser.extract_author_url(observation)

        self.assertEqual(author_url, "N/A")

    def test_parse_observation_with_special_characters(self):
        """Test parsing observation with special characters in fields."""
        observation = self.real_observation.copy()
        # Modify with special characters to test handling
        observation["geojson"] = {"coordinates": [0.0, 0.0]}
        observation["taxon"] = {"name": "Tāne's flax"}
        observation["user"] = {"login": "user-with_special.chars123"}
        observation["place_guess"] = "Taumarunui, Ruapehu District, Manawatū-Whanganui"

        result = ObservationParser.parse_observation(observation)

        self.assertIsNotNone(result)
        self.assertEqual(result["species"], "Tāne's flax")
        self.assertEqual(
            result["author_url"],
            "https://www.inaturalist.org/people/user-with_special.chars123",
        )
        self.assertEqual(
            result["location"], "Taumarunui, Ruapehu District, Manawatū-Whanganui"
        )


if __name__ == "__main__":
    unittest.main()
