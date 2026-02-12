class InaturalistAPIError(Exception):
    """Base exception for all iNaturalist API errors."""

    pass


class ObservationsFetchError(InaturalistAPIError):
    """Raised when fetching observations fails."""

    pass


class PlacesFetchError(InaturalistAPIError):
    """Raised when fetching places fails."""

    pass
