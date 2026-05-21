import tkinter as tk
from tkinter import ttk

from database import DatabaseManager
from database.seed import seed
from models import Movie
from gui.movie_card import MovieCard

BG = "#1a1a2e"
HEADER_BG = "#16213e"
ACCENT = "#e94560"
TEXT = "#eaeaea"
ENTRY_BG = "#0f3460"

_DEBOUNCE_MS = 300


class App(tk.Tk):
    """Root window: owns the header, the scrollable movie grid, and the database."""

    def __init__(self) -> None:
        """Initialise the window, open the database, seed data, and render the grid."""
        super().__init__()
        self.title("Watchlist")
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.configure(bg=BG)

        self._db = DatabaseManager("movies.db")
        seed(self._db)

        self._search_var = tk.StringVar()
        self._genre_var = tk.StringVar(value="All")
        self._debounce_id: str | None = None

        self._build_header()
        self._build_footer()
        self._build_grid()
        self._render_movies(self._db.get_all_movies())

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self) -> None:
        """Build the top bar with the app title, search field, and genre dropdown."""
        header = tk.Frame(self, bg=HEADER_BG, pady=14, padx=24)
        header.pack(fill=tk.X)

        tk.Label(
            header, text="Watchlist", font=("Helvetica", 22, "bold"),
            bg=HEADER_BG, fg=ACCENT,
        ).pack(side=tk.LEFT)

        genre_frame = tk.Frame(header, bg=HEADER_BG)
        genre_frame.pack(side=tk.RIGHT)

        tk.Label(
            genre_frame, text="Genre", font=("Helvetica", 10),
            bg=HEADER_BG, fg=TEXT,
        ).pack(side=tk.LEFT, padx=(0, 6))

        genres = ["All"] + self._db.get_genres()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=ENTRY_BG, background=ENTRY_BG,
            foreground=TEXT, selectbackground=ENTRY_BG,
            selectforeground=TEXT, arrowcolor=ACCENT,
        )
        self._genre_combo = ttk.Combobox(
            genre_frame, textvariable=self._genre_var,
            values=genres, state="readonly", width=14,
            font=("Helvetica", 11), style="Dark.TCombobox",
        )
        self._genre_combo.pack(side=tk.LEFT)
        self._genre_combo.bind("<<ComboboxSelected>>", lambda _: self._on_genre_change())

        search_frame = tk.Frame(header, bg=HEADER_BG)
        search_frame.pack(side=tk.RIGHT, padx=24)

        tk.Label(
            search_frame, text="Search", font=("Helvetica", 10),
            bg=HEADER_BG, fg=TEXT,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Entry(
            search_frame, textvariable=self._search_var,
            font=("Helvetica", 12), bg=ENTRY_BG, fg=TEXT,
            insertbackground=TEXT, relief=tk.FLAT, width=28,
        ).pack(side=tk.LEFT, ipady=5, ipadx=8)

        self._search_var.trace_add("write", lambda *_: self._on_search())

    def _build_footer(self) -> None:
        """Build the bottom bar with the Add Movie button."""
        footer = tk.Frame(self, bg=HEADER_BG, pady=12, padx=24)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(
            footer, text="+ Add Movie",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg=ACCENT, activebackground="#c73652",
            activeforeground="#ffffff", relief=tk.FLAT,
            borderwidth=0, highlightthickness=0,
            padx=24, pady=10, cursor="hand2",
            command=self._on_add_click,
        ).pack(side=tk.RIGHT)

    def _build_grid(self) -> None:
        """Build the scrollable canvas that hosts the movie card grid."""
        container = tk.Frame(self, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self._canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL,
                                 command=self._canvas.yview)

        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=BG)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw",
        )

        self._grid_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)

    # --- event handlers ---

    def _on_frame_configure(self, _event) -> None:
        """Update the canvas scroll region when the inner grid resizes."""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        """Stretch the inner grid frame to always match the canvas width."""
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        """Scroll the grid vertically with the mouse wheel."""
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_search(self) -> None:
        """Debounce keystrokes: wait 300 ms of inactivity before filtering."""
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(_DEBOUNCE_MS, self._apply_filter)

    def _on_genre_change(self) -> None:
        """Apply filter immediately when the user picks a genre."""
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
            self._debounce_id = None
        self._apply_filter()

    def _on_card_click(self, movie: Movie) -> None:
        """Open the detail popup for the clicked movie."""
        from gui.detail_window import MovieDetailWindow
        MovieDetailWindow(self, movie, on_delete=self._on_movie_deleted)

    def _on_add_click(self) -> None:
        """Open the Add Movie form."""
        from gui.add_movie_window import AddMovieWindow
        AddMovieWindow(self, genres=self._db.get_genres(), on_add=self._on_movie_added)

    def _on_movie_added(self, movie: Movie) -> None:
        """Insert the new movie and refresh the grid."""
        self._db.insert_movie(movie)
        self._apply_filter()

    def _on_movie_deleted(self, movie_id: int) -> None:
        """Delete the movie and refresh the grid."""
        self._db.delete_movie(movie_id)
        self._apply_filter()

    def _on_close(self) -> None:
        """Close the database connection before destroying the window."""
        self._db.close()
        self.destroy()

    # --- rendering ---

    def _apply_filter(self) -> None:
        """Query the database with the current search text and genre, then re-render."""
        self._debounce_id = None
        movies = self._db.filter(
            genre=self._genre_var.get(),
            query=self._search_var.get().strip(),
        )
        self._render_movies(movies)

    def _render_movies(self, movies: list[Movie]) -> None:
        """Clear the grid and repopulate it with one MovieCard per movie."""
        for widget in self._grid_frame.winfo_children():
            widget.destroy()

        cols = 5
        for col in range(cols):
            self._grid_frame.columnconfigure(col, weight=1)
        for i, movie in enumerate(movies):
            card = MovieCard(self._grid_frame, movie, self._on_card_click)
            card.grid(row=i // cols, column=i % cols, padx=12, pady=12, sticky="ew")
