from dataclasses import dataclass

from exceptions import MovieValidationError


@dataclass
class Movie:
    """Represents a single movie entity."""

    id: int
    title: str
    genre: str
    synopsis: str
    year: int
    rating: float

    def __post_init__(self) -> None:
        """Validate all fields after dataclass initialisation."""
        if not self.title.strip():
            raise MovieValidationError("title cannot be empty")
        if not self.genre.strip():
            raise MovieValidationError("genre cannot be empty")
        if not self.synopsis.strip():
            raise MovieValidationError("synopsis cannot be empty")
        if not (1888 <= self.year <= 2100):
            raise MovieValidationError(
                f"year must be between 1888 and 2100, got {self.year}"
            )
        if not (0.0 <= self.rating <= 10.0):
            raise MovieValidationError(
                f"rating must be between 0.0 and 10.0, got {self.rating}"
            )
