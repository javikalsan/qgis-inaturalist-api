from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class FormData:
    username: Optional[str]
    species: Optional[str]
    date_from: Optional[date]
    date_to: Optional[date]
    country_id: Optional[int]
    bbox: Optional[Dict[str, float]]

    def build(self) -> Dict[str, Any]:
        """Build API parameters from form data, filtering out empty values."""
        api_params: Dict[str, Any] = {
            "d1": self.date_from,
            "d2": self.date_to,
        }
        if self.username != "":
            api_params.update({"user_id": self.username})
        if self.species != "":
            api_params.update({"taxon_name": self.species})
        if self.country_id:
            api_params.update({"place_id": self.country_id})
        if self.bbox is not None:
            api_params.update(self.bbox)

        return {key: value for key, value in api_params.items() if value is not None}
