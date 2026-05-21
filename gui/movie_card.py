import tkinter as tk
from typing import Callable

from models import Movie

CARD_BG = "#16213e"
CARD_HOVER = "#0f3460"
ACCENT = "#e94560"
TEXT = "#eaeaea"
MUTED = "#a8a8b3"


class MovieCard(tk.Frame):
    """A fixed-height card widget displaying a movie summary in the grid."""

    def __init__(self, parent: tk.Widget, movie: Movie,
                 on_click: Callable[[Movie], None]) -> None:
        """Create the card, build its labels, and attach hover/click bindings."""
        super().__init__(parent, bg=CARD_BG, height=270,
                         cursor="hand2", bd=0, relief=tk.FLAT)
        self.pack_propagate(False)
        self._movie = movie
        self._on_click = on_click
        self._build()
        self._bind_hover()

    def _build(self) -> None:
        """Populate the card with genre badge, title, year, rating, and synopsis snippet."""
        self._genre_badge = tk.Label(
            self, text=self._movie.genre.upper(),
            font=("Helvetica", 8, "bold"),
            bg=ACCENT, fg="#ffffff", padx=6, pady=2,
        )
        self._genre_badge.pack(anchor="w", padx=10, pady=(12, 4))

        tk.Label(
            self, text=self._movie.title,
            font=("Helvetica", 12, "bold"),
            bg=CARD_BG, fg=TEXT, wraplength=180, justify="left",
        ).pack(anchor="w", padx=10)

        tk.Label(
            self, text=str(self._movie.year),
            font=("Helvetica", 10),
            bg=CARD_BG, fg=MUTED,
        ).pack(anchor="w", padx=10, pady=(2, 0))

        tk.Label(
            self, text=f"★  {self._movie.rating:.1f}",
            font=("Helvetica", 11, "bold"),
            bg=CARD_BG, fg=ACCENT,
        ).pack(anchor="w", padx=10, pady=(4, 0))

        raw = self._movie.synopsis
        snippet = raw[:90] + "…" if len(raw) > 90 else raw
        tk.Label(
            self, text=snippet,
            font=("Helvetica", 9),
            bg=CARD_BG, fg=MUTED, wraplength=180, justify="left",
        ).pack(anchor="w", padx=10, pady=(8, 12))

    def _bind_hover(self) -> None:
        """Attach enter, leave, and click events recursively to the card and all children."""
        self._bind_recursive(self, "<Enter>",    lambda _: self._set_bg(CARD_HOVER))
        self._bind_recursive(self, "<Leave>",    lambda _: self._set_bg(CARD_BG))
        self._bind_recursive(self, "<Button-1>", lambda _: self._on_click(self._movie))

    def _set_bg(self, color: str) -> None:
        """Change the background of the card and its children, preserving the genre badge color."""
        self.configure(bg=color)
        for widget in self.winfo_children():
            if widget is self._genre_badge:
                continue
            try:
                widget.configure(bg=color)
            except tk.TclError:
                pass

    def _bind_recursive(self, widget: tk.Widget, event: str,
                        callback: Callable) -> None:
        """Bind an event to a widget and all its descendants."""
        widget.bind(event, callback)
        for child in widget.winfo_children():
            self._bind_recursive(child, event, callback)
