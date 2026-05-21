import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable

from exceptions import MovieValidationError
from models import Movie

BG = "#1a1a2e"
HEADER_BG = "#16213e"
FIELD_BG = "#0f3460"
ACCENT = "#e94560"
TEXT = "#eaeaea"
MUTED = "#a8a8b3"
LABEL_FONT = ("Helvetica", 11)
ENTRY_FONT = ("Helvetica", 11)


class AddMovieWindow(tk.Toplevel):
    """Modal form for creating and submitting a new movie."""

    def __init__(self, parent: tk.Widget, genres: list[str],
                 on_add: Callable[[Movie], None]) -> None:
        """Open the form with the existing genres pre-loaded in the dropdown."""
        super().__init__(parent)
        self._genres = genres
        self._on_add = on_add

        self.title("Add a Movie")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._build()
        self._center(parent)

    def _build(self) -> None:
        """Lay out the header, form fields, and action buttons."""
        # Header
        header = tk.Frame(self, bg=HEADER_BG, pady=16, padx=24)
        header.pack(fill=tk.X)
        tk.Label(
            header, text="Add a Movie",
            font=("Helvetica", 17, "bold"),
            bg=HEADER_BG, fg=ACCENT,
        ).pack(anchor="w")

        # Form body
        body = tk.Frame(self, bg=BG, padx=28, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(1, weight=1)

        self._title_var   = tk.StringVar()
        self._genre_var   = tk.StringVar()
        self._year_var    = tk.StringVar()
        self._rating_var  = tk.StringVar()
        self._image_var   = tk.StringVar()

        fields = [
            ("Title *",    self._entry(body, self._title_var)),
            ("Genre *",    self._genre_combo(body)),
            ("Year *",     self._entry(body, self._year_var, width=10)),
            ("Rating *",   self._entry(body, self._rating_var, width=10, placeholder="0.0 – 10.0")),
            ("Synopsis *", None),
            ("Image",      self._image_row(body)),
        ]

        row = 0
        for label_text, widget in fields:
            tk.Label(
                body, text=label_text, font=LABEL_FONT,
                bg=BG, fg=MUTED, anchor="w",
            ).grid(row=row, column=0, sticky="nw", pady=(0, 12), padx=(0, 16))

            if label_text.startswith("Synopsis"):
                self._synopsis_box = tk.Text(
                    body, font=ENTRY_FONT,
                    bg=FIELD_BG, fg=TEXT, insertbackground=TEXT,
                    relief=tk.FLAT, height=5, wrap="word",
                )
                self._synopsis_box.grid(row=row, column=1, sticky="ew", pady=(0, 12))
            elif widget is not None:
                widget.grid(row=row, column=1, sticky="ew", pady=(0, 12))

            row += 1

        # Buttons
        footer = tk.Frame(self, bg=BG, pady=16)
        footer.pack(fill=tk.X, padx=28)

        tk.Button(
            footer, text="Add Movie",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg=ACCENT, activebackground="#c73652",
            activeforeground="#ffffff", relief=tk.FLAT,
            borderwidth=0, highlightthickness=0,
            padx=24, pady=10, cursor="hand2",
            command=self._submit,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(
            footer, text="Cancel",
            font=("Helvetica", 11),
            bg="#2c3e6e", fg=ACCENT, activebackground="#374f8a",
            activeforeground="#ffffff", relief=tk.FLAT,
            borderwidth=0, highlightthickness=0,
            padx=24, pady=10, cursor="hand2",
            command=self.destroy,
        ).pack(side=tk.RIGHT)

    # --- field helpers ---

    def _entry(self, parent: tk.Widget, var: tk.StringVar,
               width: int = 30, placeholder: str = "") -> tk.Entry:
        """Create a styled single-line entry bound to var."""
        e = tk.Entry(parent, textvariable=var, font=ENTRY_FONT,
                     bg=FIELD_BG, fg=TEXT, insertbackground=TEXT,
                     relief=tk.FLAT, width=width)
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=MUTED)
            e.bind("<FocusIn>",  lambda _: self._clear_placeholder(e, placeholder))
            e.bind("<FocusOut>", lambda _: self._restore_placeholder(e, var, placeholder))
        return e

    def _genre_combo(self, parent: tk.Widget) -> ttk.Combobox:
        """Create a combobox pre-populated with existing genres; allows custom input."""
        style = ttk.Style()
        style.configure(
            "Form.TCombobox",
            fieldbackground=FIELD_BG, background=FIELD_BG,
            foreground=TEXT, selectbackground=FIELD_BG,
            selectforeground=TEXT, arrowcolor=ACCENT,
        )
        combo = ttk.Combobox(
            parent, textvariable=self._genre_var,
            values=self._genres, font=ENTRY_FONT,
            style="Form.TCombobox",
        )
        return combo

    def _image_row(self, parent: tk.Widget) -> tk.Frame:
        """Create an entry + Browse button row for the optional image path."""
        frame = tk.Frame(parent, bg=BG)
        tk.Entry(
            frame, textvariable=self._image_var, font=ENTRY_FONT,
            bg=FIELD_BG, fg=TEXT, insertbackground=TEXT, relief=tk.FLAT,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        tk.Button(
            frame, text="Browse",
            font=("Helvetica", 10), bg="#2c3e6e", fg=ACCENT,
            activebackground="#374f8a", activeforeground="#ffffff",
            relief=tk.FLAT, borderwidth=0, highlightthickness=0,
            padx=12, pady=6, cursor="hand2",
            command=self._browse_image,
        ).pack(side=tk.LEFT, padx=(8, 0))
        return frame

    @staticmethod
    def _clear_placeholder(entry: tk.Entry, placeholder: str) -> None:
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT)

    @staticmethod
    def _restore_placeholder(entry: tk.Entry, var: tk.StringVar,
                             placeholder: str) -> None:
        if not var.get():
            entry.insert(0, placeholder)
            entry.config(fg=MUTED)

    def _browse_image(self) -> None:
        """Open a file picker for image selection (field only, not stored in DB)."""
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")],
        )
        if path:
            self._image_var.set(path)

    # --- submission ---

    def _submit(self) -> None:
        """Validate fields and pass a new Movie to the on_add callback."""
        title    = self._title_var.get().strip()
        genre    = self._genre_var.get().strip()
        year_raw = self._year_var.get().strip()
        rate_raw = self._rating_var.get().strip()
        synopsis = self._synopsis_box.get("1.0", tk.END).strip()

        # strip placeholder text
        if rate_raw == "0.0 – 10.0":
            rate_raw = ""

        if not all([title, genre, year_raw, rate_raw, synopsis]):
            messagebox.showerror("Missing fields", "Please fill in all required fields (*).",
                                 parent=self)
            return

        try:
            year = int(year_raw)
        except ValueError:
            messagebox.showerror("Invalid year", "Year must be a whole number.", parent=self)
            return

        try:
            rating = float(rate_raw)
        except ValueError:
            messagebox.showerror("Invalid rating", "Rating must be a number (e.g. 7.5).", parent=self)
            return

        try:
            movie = Movie(id=-1, title=title, genre=genre,
                          synopsis=synopsis, year=year, rating=rating)
        except MovieValidationError as e:
            messagebox.showerror("Validation error", str(e), parent=self)
            return

        self._on_add(movie)
        self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        """Position the form at the centre of the parent window."""
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
