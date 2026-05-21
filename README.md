# Watchlist — Movie Manager

A desktop application built with Python to browse, search, and manage a personal movie catalogue.

---

## Part 1 — Project Presentation & User Manual

### What is Watchlist?

Watchlist is a graphical desktop app that lets you maintain a personal movie catalogue. It ships with 9 pre-loaded films and allows you to add or delete entries at any time. All data is persisted in a local SQLite database (`movies.db`), so your changes survive between sessions.

### Prerequisites

- Python 3.11 or higher
- The following packages:

```
pip install pillow
```

> `tkinter` is included with the standard Python distribution. No additional install is required.

### How to Run

From the root of the project directory:

```bash
python main.py
```

### User Manual

**Main window**

| Element | Description |
|---|---|
| Search bar (top right) | Filter movies by title or synopsis — results update 300 ms after you stop typing |
| Genre dropdown | Narrow the grid to a single genre, or pick "All" to show everything |
| Movie grid | Scrollable grid of cards — hover to highlight, click to open the detail popup |
| `+ Add Movie` (bottom right) | Open the form to create a new entry |

**Detail popup**

Click any card to open a modal window showing the full synopsis, genre badge, year, and rating. A **Delete** button permanently removes the film after a confirmation prompt.

**Add Movie form**

Fill in all required fields (marked with `*`): Title, Genre, Year, Rating (0.0 – 10.0), and Synopsis. The Genre field accepts both existing genres from the dropdown and free-text custom genres. Click **Add Movie** to save or **Cancel** to discard.

---

## Part 2 — Project Structure & Key Functions

### Directory Layout

```
python_project/
├── main.py                  # Entry point
├── movies.db                # SQLite database (auto-created on first run)
├── exceptions.py            # Custom exception classes
├── images/                  # Cover images for the pre-seeded films
├── models/
│   ├── __init__.py
│   └── movie.py             # Movie dataclass + field validation
├── database/
│   ├── __init__.py
│   ├── db_manager.py        # All SQLite interactions
│   └── seed.py              # Initial catalogue (9 films)
└── gui/
    ├── __init__.py
    ├── app.py               # Root window — grid, header, footer
    ├── movie_card.py        # Individual card widget
    ├── detail_window.py     # Detail / delete popup
    └── add_movie_window.py  # Add movie form
```

### Architecture Overview

The project follows a layered architecture:

```
main.py  →  gui/app.py  →  database/db_manager.py  →  movies.db
                        →  models/movie.py
```

`App` is the root `tk.Tk` window. It owns the single `DatabaseManager` instance and passes callbacks down to child windows so they never touch the database directly.

### Key Functions Explained

#### `DatabaseManager.filter()` — `database/db_manager.py:77`

```python
def filter(self, genre: str, query: str) -> list[Movie]:
```

The central query used every time the search bar or genre dropdown changes. It combines both filters in a single SQL statement. When `genre` is `"All"` it skips the genre clause entirely; otherwise it uses a parameterised `WHERE genre = ?` to avoid SQL injection. The `LIKE` pattern is built with `%…%` for substring matching on both title and synopsis.

#### `App._on_search()` — `gui/app.py:145`

```python
def _on_search(self) -> None:
```

Implements a **debounce** mechanism: instead of querying the database on every keystroke, it cancels the previous `after()` timer and schedules a new one 300 ms in the future. Only when the user stops typing does `_apply_filter()` actually run. This prevents unnecessary DB calls while the user is mid-word.

#### `MovieCard._bind_recursive()` — `gui/movie_card.py:116`

```python
def _bind_recursive(self, widget, event, callback) -> None:
```

A card is a `tk.Frame` containing nested child widgets (labels, image label). In tkinter, mouse events only fire on the widget they land on — not the parent. This function walks the full widget tree and attaches the same hover/click handler to every child, making the entire card area interactive.

#### `MovieCard._build()` — `gui/movie_card.py:46`

Handles image loading for the pre-seeded films using Pillow. It looks up the film title in `_TITLE_TO_IMAGE`, opens the file, and resizes it to 200×300 px using the `LANCZOS` resampling filter (high quality downscale). If the image is missing or fails to open, it falls back silently to a placeholder frame with a film emoji — preventing any crash.

#### `Movie.__post_init__()` — `models/movie.py:17`

The `Movie` dataclass uses `__post_init__` to validate all fields immediately after construction. Invalid data (empty strings, out-of-range year or rating) raises a `MovieValidationError` before the object is ever used — keeping bad data out of the database.

#### `AddMovieWindow._center()` — `gui/add_movie_window.py:221`

```python
def _center(self, parent) -> None:
```

Positions the popup at the geometric centre of the parent window. It calls `update_idletasks()` first to force tkinter to calculate the actual window dimensions before reading `winfo_reqwidth/height`, then computes the offset from the parent's screen position.

---

## Part 3 — Difficulties We Encountered

### Image Resizing with Pillow

Displaying movie posters at a consistent size was not straightforward. Tkinter's built-in `PhotoImage` class does not support resizing, so we had to bring in the **Pillow** library. The main challenge was maintaining the correct aspect ratio: movie posters follow a 2:3 ratio (1080×1620 px standard). We fixed a target width of 200 px and derived the height mathematically:

```python
_IMG_W = 200
_IMG_H = int(_IMG_W * 1620 / 1080)  # 300 px
```

We also had to keep a reference to the `ImageTk.PhotoImage` object (`self._photo`) on the card instance. Tkinter's garbage collector destroys images that have no Python reference, causing them to disappear from the UI silently — a frustrating bug to track down.

### Making the Entire Card Clickable (tkinter Event Propagation)

A `MovieCard` is a `tk.Frame` containing several child labels and an image label. In tkinter, mouse events (`<Enter>`, `<Leave>`, `<Button-1>`) do **not** bubble up to parent widgets — each event is delivered only to the widget it lands on. This meant that hovering over the title label or the image did not trigger the card's hover highlight.

The solution was `_bind_recursive()`, which walks the full widget tree and attaches the same callback to every descendant. It also required special care for the genre badge: its background colour must stay `ACCENT` (red) even when the rest of the card highlights on hover, so it is explicitly excluded in `_set_bg()`.

### Popup Window Sizing

The detail popup (`MovieDetailWindow`) is set to a fixed `500×340` size, but the add-movie form (`AddMovieWindow`) has dynamic content whose dimensions are only known after tkinter has laid out the widgets. Calling `self.geometry("WxH")` before `update_idletasks()` returned incorrect measurements, leading to a window that was either too small (content clipped) or too large (excess blank space).

The fix was to call `update_idletasks()` before reading `winfo_reqwidth()` and `winfo_reqheight()`, letting tkinter finish its layout pass first. For the detail window, a fixed size was fine because its content never changes structure; for the add-movie form we let the geometry adapt to the actual content size.

---

## Part 4 — What We Learnt

### Building GUIs with tkinter

This project was our first real tkinter application beyond simple examples. We learnt:

- How to structure a multi-window app with a root `tk.Tk` and child `tk.Toplevel` popups
- The difference between `pack`, `grid`, and `place` geometry managers — and when to combine them
- How to build a scrollable canvas with a dynamically resized inner frame (`_build_grid()`)
- How to style widgets consistently using a shared colour palette and `ttk.Style`
- The event model: binding callbacks, using `StringVar.trace_add()` for reactive search, and implementing debounce with `after()` / `after_cancel()`

### Working with SQLite in Python

We went from raw SQL queries to a clean abstraction layer:

- Designing a normalised schema for a single-table app and managing it with `CREATE TABLE IF NOT EXISTS`
- Using parameterised queries (`?` placeholders) to prevent SQL injection
- Using `sqlite3.Row` as the row factory so columns are accessible by name rather than index
- Structuring a `DatabaseManager` class that owns the connection and exposes typed methods — keeping SQL out of the GUI layer entirely
- Implementing a seed function that only runs on an empty database, allowing the app to be restarted without duplicating data

### Working as a Team

Splitting a GUI project across multiple people introduced coordination challenges we had not faced in solo scripts:

- We used Git for version control and worked on separate modules (database layer vs. GUI layer) to limit merge conflicts
- Defining clear interfaces early (what `DatabaseManager` returns, what callbacks the windows expect) let us develop independently and integrate without surprises
- We learnt to communicate about shared state: the `App` class owns the database connection and the filter state, and child windows communicate back through callbacks rather than accessing shared globals
