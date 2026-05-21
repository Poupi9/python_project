import sqlite3

from exceptions import DatabaseError
from models import Movie


class DatabaseManager:
    """Handles all SQLite persistence for Movie objects."""

    def __init__(self, db_path: str) -> None:
        """Open the database and ensure the movies table exists."""
        self.db_path = db_path
        try:
            self._conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            raise DatabaseError(f"Cannot open database '{db_path}': {e}") from e
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        """Create the movies table if it does not exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                title    TEXT    NOT NULL,
                genre    TEXT    NOT NULL,
                synopsis TEXT    NOT NULL,
                year     INTEGER NOT NULL,
                rating   REAL    NOT NULL
            )
        """)
        self._conn.commit()

    def _row_to_movie(self, row: sqlite3.Row) -> Movie:
        """Convert a raw SQLite row into a Movie dataclass instance."""
        return Movie(
            id=row["id"],
            title=row["title"],
            genre=row["genre"],
            synopsis=row["synopsis"],
            year=row["year"],
            rating=row["rating"],
        )

    def insert_movie(self, movie: Movie) -> None:
        """Insert a new movie; the database assigns its id."""
        try:
            self._conn.execute(
                "INSERT INTO movies (title, genre, synopsis, year, rating) VALUES (?, ?, ?, ?, ?)",
                (movie.title, movie.genre, movie.synopsis, movie.year, movie.rating),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"insert_movie failed: {e}") from e

    def get_all_movies(self) -> list[Movie]:
        """Return every movie ordered alphabetically by title."""
        rows = self._conn.execute("SELECT * FROM movies ORDER BY title").fetchall()
        return [self._row_to_movie(r) for r in rows]

    def get_by_genre(self, genre: str) -> list[Movie]:
        """Return all movies belonging to the given genre."""
        rows = self._conn.execute(
            "SELECT * FROM movies WHERE genre = ? ORDER BY title", (genre,)
        ).fetchall()
        return [self._row_to_movie(r) for r in rows]

    def search(self, query: str) -> list[Movie]:
        """Return movies whose title or synopsis contains query (case-insensitive)."""
        pattern = f"%{query}%"
        rows = self._conn.execute(
            "SELECT * FROM movies WHERE title LIKE ? OR synopsis LIKE ? ORDER BY title",
            (pattern, pattern),
        ).fetchall()
        return [self._row_to_movie(r) for r in rows]

    def filter(self, genre: str, query: str) -> list[Movie]:
        """Return movies matching both genre and search query; genre='All' skips genre filter."""
        pattern = f"%{query}%"
        if genre == "All":
            rows = self._conn.execute(
                "SELECT * FROM movies WHERE title LIKE ? OR synopsis LIKE ? ORDER BY title",
                (pattern, pattern),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM movies WHERE genre = ? AND (title LIKE ? OR synopsis LIKE ?) ORDER BY title",
                (genre, pattern, pattern),
            ).fetchall()
        return [self._row_to_movie(r) for r in rows]

    def update_movie(self, movie: Movie) -> None:
        """Overwrite all fields of an existing movie identified by its id."""
        try:
            self._conn.execute(
                "UPDATE movies SET title=?, genre=?, synopsis=?, year=?, rating=? WHERE id=?",
                (movie.title, movie.genre, movie.synopsis, movie.year, movie.rating, movie.id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"update_movie failed: {e}") from e

    def delete_movie(self, movie_id: int) -> None:
        """Delete the movie with the given id."""
        try:
            self._conn.execute("DELETE FROM movies WHERE id=?", (movie_id,))
            self._conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"delete_movie failed: {e}") from e

    def get_genres(self) -> list[str]:
        """Return a sorted list of all distinct genres in the database."""
        rows = self._conn.execute(
            "SELECT DISTINCT genre FROM movies ORDER BY genre"
        ).fetchall()
        return [r["genre"] for r in rows]

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
