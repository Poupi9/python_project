import tkinter as tk
from tkinter import messagebox
from typing import Callable

from models import Movie

BG = "#1a1a2e"
HEADER_BG = "#16213e"
ACCENT = "#e94560"
TEXT = "#eaeaea"
MUTED = "#a8a8b3"

_WIN_W, _WIN_H = 500, 340


class MovieDetailWindow(tk.Toplevel):
    """Modal popup displaying the full details of a single movie."""

    def __init__(self, parent: tk.Widget, movie: Movie,
                 on_delete: Callable[[int], None] | None = None) -> None:
        super().__init__(parent)
        self._movie = movie
        self._on_delete = on_delete

        self.title(movie.title)
        self.geometry(f"{_WIN_W}x{_WIN_H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._build()
        self._center(parent)

    def _build(self) -> None:
        # Header: title + meta badges
        header = tk.Frame(self, bg=HEADER_BG, pady=16, padx=24)
        header.pack(fill=tk.X)

        tk.Label(
            header, text=self._movie.title,
            font=("Helvetica", 16, "bold"),
            bg=HEADER_BG, fg=TEXT, wraplength=450, justify="left",
        ).pack(anchor="w")

        meta = tk.Frame(header, bg=HEADER_BG)
        meta.pack(anchor="w", pady=(8, 0))

        tk.Label(
            meta, text=self._movie.genre.upper(),
            font=("Helvetica", 9, "bold"),
            bg=ACCENT, fg="#ffffff", padx=8, pady=3,
        ).pack(side=tk.LEFT)

        tk.Label(
            meta, text=str(self._movie.year),
            font=("Helvetica", 11),
            bg=HEADER_BG, fg=MUTED, padx=12,
        ).pack(side=tk.LEFT)

        tk.Label(
            meta, text=f"★  {self._movie.rating:.1f} / 10",
            font=("Helvetica", 11, "bold"),
            bg=HEADER_BG, fg=ACCENT,
        ).pack(side=tk.LEFT)

        # Body: synopsis
        body = tk.Frame(self, bg=BG, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            body, text=self._movie.synopsis,
            font=("Helvetica", 10),
            bg=BG, fg=TEXT,
            wraplength=450, justify="left",
        ).pack(anchor="nw")

        # Footer: action buttons
        footer = tk.Frame(self, bg=BG, pady=12)
        footer.pack(fill=tk.X)

        tk.Button(
            footer, text="Close",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg="#000000", activebackground="#c73652",
            activeforeground="#ffffff", relief=tk.FLAT,
            borderwidth=0, highlightthickness=0,
            padx=24, pady=8, cursor="hand2",
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=(0, 24))

        if self._on_delete is not None:
            tk.Button(
                footer, text="Delete",
                font=("Helvetica", 11, "bold"),
                bg="#c0392b", fg="#000000", activebackground="#a93226",
                activeforeground="#ffffff", relief=tk.FLAT,
                borderwidth=0, highlightthickness=0,
                padx=24, pady=8, cursor="hand2",
                command=self._confirm_delete,
            ).pack(side=tk.LEFT, padx=(24, 0))

    def _confirm_delete(self) -> None:
        confirmed = messagebox.askyesno(
            "Delete movie",
            f"Delete \"{self._movie.title}\" permanently?",
            parent=self,
        )
        if confirmed:
            self._on_delete(self._movie.id)
            self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - _WIN_W) // 2
        y = py + (ph - _WIN_H) // 2
        self.geometry(f"{_WIN_W}x{_WIN_H}+{x}+{y}")
