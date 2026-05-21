class MovieValidationError(ValueError):
    """Raised when a Movie field fails validation."""


class DatabaseError(Exception):
    """Raised when a database operation fails unexpectedly."""
