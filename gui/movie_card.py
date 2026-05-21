import os
import tkinter as tk
from typing import Callable

from PIL import Image, ImageTk

from models import Movie

CARD_BG = "#16213e"
CARD_HOVER = "#0f3460"
ACCENT = "#e94560"
TEXT = "#eaeaea"
MUTED = "#a8a8b3"

_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "images")

_TITLE_TO_IMAGE: dict[str, str] = {
    "Inception": "inception.jpg",
    "The Dark Knight": "the_dark_knight.jpg",
    "Interstellar": "interstellar.jpg",
    "The Shawshank Redemption": "the_shawshank_redemption.webp",
    "Parasite": "parasite.webp",
    "The Grand Budapest Hotel": "the_grand_budapest.webp",
    "Get Out": "getOut.jpg",
    "Hereditary": "hereditary.jpg",
    "Mad Max: Fury Road": "mad_max.jpg",
}

# Card image slot: 1080×1620 standard scaled down to card width
_IMG_W = 200
_IMG_H = int(_IMG_W * 1620 / 1080)  # 300px — preserves the 1080:1620 (2:3) ratio


class MovieCard(tk.Frame):
    """A card widget displaying a movie summary in the grid."""

    def __init__(self, parent: tk.Widget, movie: Movie,
                 on_click: Callable[[Movie], None]) -> None:
        super().__init__(parent, bg=CARD_BG, cursor="hand2", bd=0, relief=tk.FLAT)
        self._movie = movie
        self._on_click = on_click
        self._photo: ImageTk.PhotoImage | None = None
        self._build()
        self._bind_hover()

    def _build(self) -> None:
        img_name = _TITLE_TO_IMAGE.get(self._movie.title)
        loaded = False
        if img_name:
            img_path = os.path.join(_IMAGES_DIR, img_name)
            try:
                img = Image.open(img_path).resize((_IMG_W, _IMG_H), Image.LANCZOS)
                self._photo = ImageTk.PhotoImage(img)
                tk.Label(self, image=self._photo, bg=CARD_BG, bd=0).pack(fill=tk.X)
                loaded = True
            except Exception:
                pass
        if not loaded:
            placeholder = tk.Frame(self, bg="#0d1b2e", width=_IMG_W, height=_IMG_H)
            placeholder.pack(fill=tk.X)
            placeholder.pack_propagate(False)
            tk.Label(
                placeholder, text="🎬",
                font=("Helvetica", 32),
                bg="#0d1b2e", fg="#2a3f5f",
            ).place(relx=0.5, rely=0.5, anchor="center")

        self._genre_badge = tk.Label(
            self, text=self._movie.genre.upper(),
            font=("Helvetica", 8, "bold"),
            bg=ACCENT, fg="#ffffff", padx=6, pady=2,
        )
        self._genre_badge.pack(anchor="w", padx=10, pady=(8, 4))

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
        snippet = raw[:75] + "…" if len(raw) > 75 else raw
        tk.Label(
            self, text=snippet,
            font=("Helvetica", 9),
            bg=CARD_BG, fg=MUTED, wraplength=180, justify="left",
        ).pack(anchor="w", padx=10, pady=(6, 10))

    def _bind_hover(self) -> None:
        self._bind_recursive(self, "<Enter>",    lambda _: self._set_bg(CARD_HOVER))
        self._bind_recursive(self, "<Leave>",    lambda _: self._set_bg(CARD_BG))
        self._bind_recursive(self, "<Button-1>", lambda _: self._on_click(self._movie))

    def _set_bg(self, color: str) -> None:
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
        widget.bind(event, callback)
        for child in widget.winfo_children():
            self._bind_recursive(child, event, callback)
