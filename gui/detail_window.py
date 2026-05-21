import tkinter as tk

from models import Movie

BG = "#1a1a2e"
HEADER_BG = "#16213e"
ACCENT = "#e94560"
TEXT = "#eaeaea"
MUTED = "#a8a8b3"


class MovieDetailWindow(tk.Toplevel):
    """Modal popup displaying the full details of a single movie."""

    def __init__(self, parent: tk.Widget, movie: Movie) -> None:
        """Create and centre the popup over the parent window."""
        super().__init__(parent)
        self._movie = movie

        self.title(movie.title)
        self.geometry("620x480")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._build()
        self._center(parent)

    def _build(self) -> None:
        """Populate the window with a header band, synopsis body, and close button."""
        header = tk.Frame(self, bg=HEADER_BG, pady=20, padx=28)
        header.pack(fill=tk.X)

        tk.Label(
            header, text=self._movie.title,
            font=("Helvetica", 20, "bold"),
            bg=HEADER_BG, fg=TEXT, wraplength=520, justify="left",
        ).pack(anchor="w")

        meta = tk.Frame(header, bg=HEADER_BG)
        meta.pack(anchor="w", pady=(10, 0))

        tk.Label(
            meta, text=self._movie.genre.upper(),
            font=("Helvetica", 9, "bold"),
            bg=ACCENT, fg="#ffffff", padx=8, pady=3,
        ).pack(side=tk.LEFT)

        tk.Label(
            meta, text=str(self._movie.year),
            font=("Helvetica", 11),
            bg=HEADER_BG, fg=MUTED, padx=14,
        ).pack(side=tk.LEFT)

        tk.Label(
            meta, text=f"★  {self._movie.rating:.1f} / 10",
            font=("Helvetica", 11, "bold"),
            bg=HEADER_BG, fg=ACCENT,
        ).pack(side=tk.LEFT)

        body = tk.Frame(self, bg=BG, padx=28, pady=24)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            body, text="Synopsis",
            font=("Helvetica", 11, "bold"),
            bg=BG, fg=ACCENT,
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            body, text=self._movie.synopsis,
            font=("Helvetica", 11),
            bg=BG, fg=TEXT,
            wraplength=560, justify="left",
        ).pack(anchor="w")

        footer = tk.Frame(self, bg=BG, pady=16)
        footer.pack(fill=tk.X)

        tk.Button(
            footer, text="Close",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg="#ffffff", activebackground="#c73652",
            activeforeground="#ffffff", relief=tk.FLAT,
            padx=28, pady=8, cursor="hand2",
            command=self.destroy,
        ).pack()

    def _center(self, parent: tk.Widget) -> None:
        """Position the popup at the centre of the parent window."""
        w, h = 620, 480
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
