import unittest
from datetime import date

from form_data import FormData


class TestFormData(unittest.TestCase):
    """Test cases for FormData.build() method."""

    def test_build_with_all_fields(self):
        """Test building API parameters with all fields populated."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=123,
            bbox={"swlat": 37.0, "swlng": -122.5, "nelat": 38.0, "nelng": -121.5},
        )

        result = form_data.build()

        self.assertEqual(result["user_id"], "johndoe")
        self.assertEqual(result["taxon_name"], "Canis lupus")
        self.assertEqual(result["d1"], date(2024, 1, 1))
        self.assertEqual(result["d2"], date(2024, 12, 31))
        self.assertEqual(result["place_id"], 123)
        self.assertEqual(result["swlat"], 37.0)
        self.assertEqual(result["swlng"], -122.5)
        self.assertEqual(result["nelat"], 38.0)
        self.assertEqual(result["nelng"], -121.5)

    def test_build_with_empty_username(self):
        """Test that empty username is excluded from parameters."""
        form_data = FormData(
            username="",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertNotIn("user_id", result)
        self.assertIn("taxon_name", result)

    def test_build_with_empty_species(self):
        """Test that empty species is excluded from parameters."""
        form_data = FormData(
            username="johndoe",
            species="",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertIn("user_id", result)
        self.assertNotIn("taxon_name", result)

    def test_build_with_none_country_id(self):
        """Test that None country_id is excluded from parameters."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertNotIn("place_id", result)

    def test_build_with_country_id(self):
        """Test that country_id is included when present."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=456,
            bbox=None,
        )

        result = form_data.build()

        self.assertEqual(result["place_id"], 456)

    def test_build_with_none_bbox(self):
        """Test that None bbox is excluded from parameters."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=123,
            bbox=None,
        )

        result = form_data.build()

        self.assertNotIn("swlat", result)
        self.assertNotIn("swlng", result)
        self.assertNotIn("nelat", result)
        self.assertNotIn("nelng", result)

    def test_build_with_bbox(self):
        """Test that bbox coordinates are included when present."""
        bbox = {"swlat": 37.0, "swlng": -122.5, "nelat": 38.0, "nelng": -121.5}
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=bbox,
        )

        result = form_data.build()

        self.assertEqual(result["swlat"], 37.0)
        self.assertEqual(result["swlng"], -122.5)
        self.assertEqual(result["nelat"], 38.0)
        self.assertEqual(result["nelng"], -121.5)

    def test_build_filters_none_values(self):
        """Test that None date values are filtered out."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=None,
            date_to=None,
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertNotIn("d1", result)
        self.assertNotIn("d2", result)
        self.assertIn("user_id", result)
        self.assertIn("taxon_name", result)

    def test_build_with_minimal_data(self):
        """Test building with only required fields."""
        form_data = FormData(
            username="",
            species="",
            date_from=None,
            date_to=None,
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        # Should return empty dict or only non-None values
        self.assertIsInstance(result, dict)
        self.assertNotIn("user_id", result)
        self.assertNotIn("taxon_name", result)
        self.assertNotIn("d1", result)
        self.assertNotIn("d2", result)
        self.assertNotIn("place_id", result)

    def test_build_with_dates_only(self):
        """Test building with only date range."""
        form_data = FormData(
            username="",
            species="",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertEqual(result["d1"], date(2024, 1, 1))
        self.assertEqual(result["d2"], date(2024, 12, 31))
        self.assertNotIn("user_id", result)
        self.assertNotIn("taxon_name", result)

    def test_build_preserves_original_data(self):
        """Test that build() doesn't mutate the FormData instance."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=123,
            bbox={"swlat": 37.0, "swlng": -122.5, "nelat": 38.0, "nelng": -121.5},
        )

        result1 = form_data.build()
        result2 = form_data.build()

        self.assertEqual(result1, result2)
        self.assertEqual(form_data.username, "johndoe")
        self.assertEqual(form_data.species, "Canis lupus")

    def test_build_with_zero_country_id(self):
        """Test that country_id of 0 is excluded (falsy but valid)."""
        form_data = FormData(
            username="johndoe",
            species="Canis lupus",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=0,
            bbox=None,
        )

        result = form_data.build()

        # 0 is falsy, so it won't be included (current implementation)
        self.assertNotIn("place_id", result)

    def test_build_with_unicode_characters(self):
        """Test building with unicode characters in strings."""
        form_data = FormData(
            username="墨菲斯",
            species="amanita muscaria",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        self.assertEqual(result["user_id"], "墨菲斯")
        self.assertEqual(result["taxon_name"], "amanita muscaria")

    def test_build_with_whitespace_only_strings(self):
        """Test that whitespace-only strings are treated as non-empty."""
        form_data = FormData(
            username="   ",
            species="  \t  ",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            country_id=None,
            bbox=None,
        )

        result = form_data.build()

        # Current implementation checks != "", so whitespace passes
        self.assertIn("user_id", result)
        self.assertIn("taxon_name", result)
        self.assertEqual(result["user_id"], "   ")
        self.assertEqual(result["taxon_name"], "  \t  ")


if __name__ == "__main__":
    unittest.main()
