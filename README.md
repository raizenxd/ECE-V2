# ECETHON — Documentation Guide

ECETHON is a Python-based interactive computational tool for Advanced Engineering Mathematics. It provides a graphical desktop application built with **Tkinter** that allows students to solve problems in four key topics: **Complex Numbers**, **Linear Algebra**, **Fourier Series**, and **Laplace Transform**.

---

## Table of Contents

1. [How to Run](#how-to-run)
2. [Dependencies](#dependencies)
3. [Application Structure](#application-structure)
4. [Global Constants & Configuration](#global-constants--configuration)
5. [Input Parser (Shared Utilities)](#input-parser-shared-utilities)
6. [Drawing Helper Functions](#drawing-helper-functions)
7. [App Class — Main Window](#app-class--main-window)
8. [Page Class — Base Page](#page-class--base-page)
9. [HomePage](#homepage)
10. [TopicsPage](#topicspage)
11. [AboutPage](#aboutpage)
12. [CreatorPage](#creatorpage)
13. [ComplexPage — Complex Numbers](#complexpage--complex-numbers)
14. [LinearPage — Linear Algebra](#linearpage--linear-algebra)
15. [FourierPage — Fourier Series](#fourierpage--fourier-series)
16. [LaplacePage — Laplace Transform](#laplacepage--laplace-transform)
17. [Shared Modal Helper](#shared-modal-helper)
18. [Navigation Flow](#navigation-flow)
19. [Accepted Input Formats](#accepted-input-formats)

---

## How to Run

```bash
python ECETHON.py
```

Make sure all dependencies are installed first (see below). The app opens a fixed **1280 × 720** window.

---

## Dependencies

| Library | Purpose |
|---|---|
| `tkinter` | GUI framework — windows, canvases, buttons, entries |
| `tkinter.ttk` | Styled widgets (Combobox) |
| `sympy` | Symbolic mathematics — integration, Laplace, simplification |
| `numpy` | Numerical matrix operations (Linear Algebra module) |
| `cmath` | Complex number math (phase, polar) |
| `math` | Standard math functions (degrees, cos, sin) |
| `re` | Regular expressions for input normalization |

Install with:

```bash
pip install sympy numpy
```

---

## Application Structure

```
ECETHON.py
│
├── Global constants & color palette
├── _SAFE_LOCALS          ← whitelist of math functions for eval
├── _normalize()          ← sanitize user input strings
├── _parse_num()          ← convert string → Python complex
│
├── Drawing helpers
│   ├── rr()              ← rounded rectangle
│   ├── otxt()            ← outlined text
│   └── cbtn()            ← canvas button
│
├── App                   ← root Tk window, page router
├── Page                  ← base frame all pages inherit from
│
├── HomePage              ← landing screen
├── TopicsPage            ← topic selector
├── AboutPage             ← 5-slide educational deck
├── CreatorPage           ← creator profile image
│
├── ComplexPage           ← Complex Numbers calculator
├── LinearPage            ← Linear Algebra matrix calculator
├── FourierPage           ← Fourier Series calculator
└── LaplacePage           ← Laplace Transform calculator
```

---

## Global Constants & Configuration

### Window Size

```python
W, H = 1280, 720
```

Fixed window width and height in pixels. All pages are drawn to fit exactly this size. The window is not resizable.

---

### Color Palette

All colors used throughout the UI are defined as hex strings at the top of the file for easy theme management.

| Name | Hex | Used For |
|---|---|---|
| `SKY` | `#29ABE2` | Main background color |
| `RAY` | `#55CCFF` | Spotlight ray effect on home screen |
| `PURPLE` | `#5C3E9E` | Footer bar |
| `GREEN` | `#6DD820` | Title text, buttons, highlights |
| `GRN_DK` | `#3A8A00` | Green button shadow |
| `RED` | `#E84040` | BACK button, error text |
| `RED_DK` | `#A01010` | Red button shadow |
| `YELLOW` | `#F5C518` | HOME button, Laplace highlights |
| `YEL_DK` | `#B08800` | Yellow button shadow |
| `NAVY` | `#1B2A72` | Text outlines, header bars |
| `WHITE` | `#FFFFFF` | General text |
| `CARD` | `#5ABDE8` | Card/panel backgrounds |

---

## Input Parser (Shared Utilities)

These two functions are used by **every calculator page** to safely convert user-typed strings into numeric values.

---

### `_SAFE_LOCALS`

```python
_SAFE_LOCALS = { 'pi': sp.pi, 'sqrt': sp.sqrt, 'sin': sp.sin, ... }
```

A **whitelist dictionary** passed to SymPy's `sympify()`. It maps allowed names (like `pi`, `sqrt`, `sin`, `log`) to their SymPy equivalents. This prevents arbitrary Python code from being evaluated — only recognized math symbols are accepted.

**Supported constants:** `pi`, `e`, `E`, `I` (imaginary unit), `inf`, `oo`

**Supported functions:** `sqrt`, `cbrt`, `exp`, `log`, `ln`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sinh`, `cosh`, `tanh`, `abs`, `Abs`, `sign`, `floor`, `ceil`, `re`, `im`, `arg`, `conj`

---

### `_normalize(raw)`

```python
def _normalize(raw): ...
```

**Purpose:** Cleans up a raw math string typed by a user and converts it to valid Python/SymPy syntax before evaluation.

**What it handles:**

| Input | Converted To | Reason |
|---|---|---|
| `2^3` | `2**3` | Python uses `**` for exponentiation |
| `3×2` | `3*2` | Unicode multiplication sign |
| `6÷2` | `6/2` | Unicode division sign |
| `3+2i` | `3+2*I` | `i` → SymPy imaginary unit `I` |
| `3+2j` | `3+2*I` | `j` → SymPy imaginary unit `I` |
| `2I` | `2*I` | Implicit multiplication (digit before I) |
| `3pi` | `3*pi` | Implicit multiplication (digit before pi) |

**Note:** It is careful not to replace the `i` inside words like `sin`, `pi`, `sinh` — only standalone `i` or `j` are converted.

**Parameters:**
- `raw` — raw string from user input

**Returns:** Normalized string ready for `sp.sympify()`

---

### `_parse_num(raw)`

```python
def _parse_num(raw): ...
```

**Purpose:** Full pipeline to convert a user-typed math string into a Python `complex` number.

**Steps:**
1. Calls `_normalize(raw)` to clean the string
2. Passes the result to `sp.sympify()` with `_SAFE_LOCALS`
3. Evaluates to a numeric value with `.evalf()`
4. Converts to Python `complex` and returns it

**Parameters:**
- `raw` — raw math expression string (e.g. `"3+2i"`, `"sqrt(2)*pi"`, `"1/2+3j"`)

**Returns:** Python `complex` number

**Used by:** `ComplexPage._calc()`, `LinearPage._parse_cell()`, `FourierPage._calc()`

---

## Drawing Helper Functions

These are low-level canvas drawing utilities shared across all pages.

---

### `rr(cv, x1, y1, x2, y2, r=22, **kw)`

**Purpose:** Draws a smooth **rounded rectangle** on a Tkinter canvas using a polygon with `smooth=True`.

**Parameters:**
- `cv` — the Tkinter Canvas to draw on
- `x1, y1` — top-left corner coordinates
- `x2, y2` — bottom-right corner coordinates
- `r` — corner radius in pixels (default `22`)
- `**kw` — extra keyword arguments passed to `create_polygon` (e.g. `fill`, `outline`)

**Returns:** Canvas item ID of the polygon

**Used for:** All cards, panels, and buttons throughout the app.

---

### `otxt(cv, x, y, text, font, fill=WHITE, ol=NAVY, ow=3, **kw)`

**Purpose:** Draws **outlined text** on a canvas by first drawing multiple copies of the text in the outline color (`ol`) offset in every direction by up to `ow` pixels, then drawing the main text on top.

**Parameters:**
- `cv` — canvas
- `x, y` — center position
- `text` — string to draw
- `font` — font tuple e.g. `("OPTIVagRound-Bold", 24)`
- `fill` — main text color (default `WHITE`)
- `ol` — outline color (default `NAVY`)
- `ow` — outline width in pixels (default `3`)
- `**kw` — extra arguments passed to `create_text`

**Returns:** Canvas item ID of the foreground text

**Used for:** All titles, headings, and any text that needs to stand out against a colored background.

---

### `cbtn(cv, x1, y1, x2, y2, label, font, color, dark, cmd, r=20)`

**Purpose:** Creates a complete **canvas button** consisting of:
1. A shadow rectangle (drawn offset by 4px in dark color)
2. A main rounded rectangle body
3. A text label centered on the body
4. Click bindings on both the rectangle and the text

**Parameters:**
- `cv` — canvas
- `x1, y1, x2, y2` — bounding box of the button
- `label` — button text
- `font` — font tuple
- `color` — button face color
- `dark` — shadow/dark variant of the button color
- `cmd` — Python callable executed when clicked
- `r` — corner radius (default `20`)

**Returns:** Tuple `(body_id, text_id)` — the canvas item IDs for the button body and label

---

## App Class — Main Window

```python
class App(tk.Tk):
```

**Purpose:** The root Tkinter window. Manages all pages and handles navigation between them.

---

### `App.__init__(self)`

Creates the window, sets the title to `"ECETHON"`, fixes the size to `1280 × 720`, and instantiates **all eight pages**:

| Key | Page Class |
|---|---|
| `"home"` | `HomePage` |
| `"topics"` | `TopicsPage` |
| `"about"` | `AboutPage` |
| `"creator"` | `CreatorPage` |
| `"complex"` | `ComplexPage` |
| `"linear"` | `LinearPage` |
| `"fourier"` | `FourierPage` |
| `"laplace"` | `LaplacePage` |

All pages are stacked on top of each other at position `(0, 0)`. The app starts by calling `self.go("home")`.

---

### `App.go(self, name)`

**Purpose:** Navigates to a named page by raising it to the top of the stacking order.

**Steps:**
1. Lowers all pages to the bottom
2. Looks up `name` in `self._pages`
3. If the page has an `on_show()` method, calls it (used by `AboutPage` to reset the slide)
4. Calls `.lift()` on the target page to bring it to the front

**Parameters:**
- `name` — string key (e.g. `"home"`, `"complex"`)

---

## Page Class — Base Page

```python
class Page(tk.Frame):
```

**Purpose:** The parent class for all pages. Provides shared navigation methods and common UI elements.

---

### `Page.__init__(self, app)`

Creates a full-size `tk.Frame` with the sky-blue background color. Stores a reference to the `App` instance as `self._app`.

---

### `Page.go(self, name)`

Calls `self._app.go(name)`. Convenience method so any page can trigger navigation without needing to reference the app directly.

---

### `Page._topbar(self, cv, back="home")`

**Purpose:** Draws the standard **top navigation bar** present on all calculator and info pages.

Draws three elements:
- **BACK button** (red, left side) — navigates to the `back` page (default `"home"`)
- **ECETHON label** (green, centered) — decorative title
- **HOME button** (yellow, right side) — always navigates to `"home"`

**Parameters:**
- `cv` — canvas
- `back` — page name to navigate to when BACK is pressed (default `"home"`)

---

### `Page._purplebar(cv)` *(static method)*

**Purpose:** Draws the **purple footer bar** at the bottom of every page.

Draws a filled rectangle from `(0, H-70)` to `(W, H)` in `PURPLE` (`#5C3E9E`).

---

## HomePage

```python
class HomePage(Page):
```

**Purpose:** The **landing/splash screen** of the application. It is the first screen the user sees.

---

### `HomePage.__init__(self, app)`

Creates the canvas and calls `_draw()`.

---

### `HomePage._draw(self, cv)`

**Purpose:** Renders the full home screen.

What it draws:
1. **Spotlight rays** — Seven radiating trapezoid shapes from the top-center of the screen in `RAY` color, creating a stage-light effect
2. **Purple footer bar** via `_purplebar()`
3. **ECETHON title** — Large outlined text at font size 96
4. **START button** — Green, centered, navigates to `TopicsPage`
5. **ABOUT button** — Red, in the footer bar, navigates to `AboutPage`
6. **CREATOR button** — Yellow, in the footer bar, navigates to `CreatorPage`

---

### `HomePage._modal(self, title, body)`

**Purpose:** Creates a small **popup dialog window** (Toplevel) with a title, body text, and a Close button. Used as a legacy helper (About/Creator now use full pages instead).

**Parameters:**
- `title` — dialog title string
- `body` — body text to display

---

### `HomePage._about(self)`

Calls `self.go("about")` to navigate to the About page.

---

### `HomePage._creator(self)`

Calls `self.go("creator")` to navigate to the Creator page.

---

## TopicsPage

```python
class TopicsPage(Page):
```

**Purpose:** Displays the **four topic selection cards**. The user clicks a card to enter the corresponding calculator.

---

### `TopicsPage._TOPICS`

Class-level list of tuples defining the four topic cards:

```python
_TOPICS = [
    ("Complex\nNumbers",   "complex",  GREEN,     GRN_DK),
    ("Linear\nAlgebra",    "linear",   "#8B5CF6", "#5B2CC0"),
    ("Fourier\nSeries",    "fourier",  "#F97316", "#C05010"),
    ("Laplace\nTransform", "laplace",  "#EC4899", "#A01060"),
]
```

Each tuple: `(display_label, page_key, color, shadow_color)`

---

### `TopicsPage._draw(self, cv)`

**Purpose:** Renders the topic selection screen.

1. Draws background, purple bar, and top navigation bar
2. Draws the "SELECT A TOPIC" heading
3. Calculates total width of all cards + gaps and centers them horizontally
4. For each topic, draws a drop-shadow rounded rectangle, a colored card, and a text label
5. Binds click events on both the card and label to `self.go(dest)` where `dest` is the page key

---

## AboutPage

```python
class AboutPage(Page):
```

**Purpose:** A **5-slide educational presentation** covering the purpose of the project and each of the four math topics. Users navigate with BACK and NEXT buttons.

---

### `AboutPage.__init__(self, app)`

Initializes with `self._slide = 0` (always starts at the first slide) and renders.

---

### `AboutPage.on_show(self)`

**Purpose:** Called by `App.go()` every time the About page is navigated to. Resets `self._slide` to `0` and calls `_render()` so the user always starts at slide 0.

---

### `AboutPage._go(self, idx)`

Sets `self._slide` to `idx` and calls `_render()` to redraw the page for the new slide.

---

### `AboutPage._render(self)`

**Purpose:** Completely clears and redraws the canvas for the current slide index.

Logic:
- Always draws the purple bar and HOME button
- Draws the BACK button (with "About the Project" subtitle) only if `self._slide > 0`
- Draws the NEXT button only if `self._slide < 4`
- Dispatches to the appropriate slide method: `_s0`, `_s1`, `_s2`, `_s3`, or `_s4`

---

### `AboutPage._card(self, y1, y2)`

Draws a **dark blue card** (`#2A6A9A`) behind formula blocks so they stand out from the background.

---

### `AboutPage._body(self, y, text, size=13)`

Draws **left-aligned, word-wrapped body text** starting at `y`. Uses the `_TX` (left margin, x=70) and `_TW` (wrap width) class constants.

---

### `AboutPage._fline(self, y, text, color=WHITE, size=14)`

Draws a **centered formula line** using `otxt()` with a navy outline for readability over the dark card background.

---

### `AboutPage._flabel(self, y)`

Draws the label `"FORMULAS:"` centered at the given `y` position, used as a section heading before formula cards.

---

### `AboutPage._s0(self)` — Slide 0: About the Project

Renders the overview slide with:
- Project description paragraphs
- Colored row of the four topic names

---

### `AboutPage._s1(self)` — Slide 1: Linear Algebra

Renders a description of Linear Algebra, the formula **Ax = b** inside a card, and a practical application note.

---

### `AboutPage._s2(self)` — Slide 2: Complex Numbers

Renders the complex number description and a two-column formula card showing:
- General form, polar form, addition
- Multiplication, division, modulus, conjugate

---

### `AboutPage._s3(self)` — Slide 3: Fourier Series

Renders a description of the Fourier series and a formula card with the general formula plus the three coefficient integrals (a₀, aₙ, bₙ).

---

### `AboutPage._s4(self)` — Slide 4: Laplace Transform

Renders a description of the Laplace transform and a formula card showing the bilateral and unilateral transform definitions.

---

## CreatorPage

```python
class CreatorPage(Page):
```

**Purpose:** Displays a full-screen image from `creator/Creator.png` that serves as the creator's profile/credits page.

---

### `CreatorPage._BTN_HOME`

```python
_BTN_HOME = (1090, 18, 1248, 70)
```

The pixel coordinates of an **invisible click zone** overlaid on top of the HOME button area in the image. These coordinates were measured directly from the `Creator.png` image.

---

### `CreatorPage._draw(self)`

**Purpose:** Loads and displays the creator image, then overlays an invisible rectangle hit-zone for the HOME button.

1. Attempts to load `creator/Creator.png` with `tk.PhotoImage`
2. If the image loads, renders it full-screen
3. If the file is missing, shows a fallback error message on a blue background
4. Creates an invisible rectangle at `_BTN_HOME` coordinates and binds:
   - `<Button-1>` → `self.go("home")`
   - `<Enter>` → changes cursor to `"hand2"` (pointer)
   - `<Leave>` → restores default cursor

---

## ComplexPage — Complex Numbers

```python
class ComplexPage(Page):
```

**Purpose:** Allows the student to type any complex number expression and receive a breakdown of its **real part, imaginary part, magnitude (modulus), and phase angle**.

---

### `ComplexPage._draw(self)`

Renders the calculator UI:
- Page title "COMPLEX NUMBERS"
- An input card with a hint showing example expressions
- A text entry field (`self.expr`) that also triggers calculation on `<Return>`
- A CALCULATE button

---

### `ComplexPage._calc(self)`

**Purpose:** Reads the expression from `self.expr`, parses it, and shows the result modal.

**Steps:**
1. Gets the raw text from the entry field
2. Shows an error modal if the input is empty
3. Calls `_parse_num(raw)` to evaluate the expression
4. Catches `ZeroDivisionError` and general `Exception` separately, showing descriptive error messages
5. On success, extracts `real`, `imag`, `magnitude` (`abs()`), and `phase` (`cmath.phase()` in degrees)
6. Calls `_result_modal()` with the computed values

---

### `ComplexPage._result_modal(self, *, r_str, r, i, mag, phase, error)`

**Purpose:** Displays a **popup modal window** with the result of the complex number computation.

**Parameters (keyword-only):**
- `r_str` — formatted result string e.g. `"3.0+2.0j"`
- `r` — real part (float)
- `i` — imaginary part (float)
- `mag` — magnitude/modulus (float)
- `phase` — phase angle in degrees (float)
- `error` — error message string (if set, shows error instead of result)

**Modal content (success):**
| Row | Value |
|---|---|
| Result | Full complex representation |
| Real part | Numeric real component |
| Imaginary part | Numeric imaginary component |
| Magnitude | `√(r² + i²)` to 6 decimal places |
| Phase | Angle in degrees to 2 decimal places |

The modal is centered on the main window, has a NAVY header bar, a card-style result area, horizontal dividers between rows, and a CLOSE button.

---

## LinearPage — Linear Algebra

```python
class LinearPage(Page):
```

**Purpose:** Allows the student to perform **matrix operations** (addition, subtraction, multiplication, division) on two matrices A and B of configurable size (1×1 to 5×5). Supports complex number entries.

**Class constants:**
- `_MAX = 5` — maximum matrix dimension
- `_CELL_W = 88`, `_CELL_H = 44`, `_PAD = 5` — grid cell sizing

---

### `LinearPage._draw_static(self)`

**Purpose:** Draws the permanent (non-rebuilt) parts of the UI:
- Title "LINEAR ALGEBRA"
- Control bar card with:
  - **Operation dropdown** (Combobox): Addition, Subtraction, Multiplication, Division
  - **A rows/cols spinboxes** for Matrix A dimensions
  - **B rows/cols spinboxes** for Matrix B dimensions
  - **SET button** to rebuild grids
- A hint label supporting complex inputs
- The CALCULATE button (always visible, always calls `_calc()`)

Changing the operation dropdown automatically triggers `_build_grids()` via `trace_add`.

---

### `LinearPage._spin(self, x, y, var)`

**Purpose:** Creates a read-only **Spinbox** widget for selecting a matrix dimension (1–5).

**Parameters:**
- `x, y` — position to place the widget
- `var` — `tk.StringVar` that holds the current value

**Returns:** The `tk.Spinbox` widget

---

### `LinearPage._build_grids(self, *_)`

**Purpose:** Destroys and recreates the matrix entry grids every time the user changes the dimensions or operation.

**Steps:**
1. Reads current row/column counts from `self.rA`, `self.cA`, `self.rB`, `self.cB`
2. Calculates the pixel width of each grid
3. Positions Matrix A on the left and Matrix B on the right with at least 120px gap
4. Draws/updates canvas labels: "Matrix A", "Matrix B", and the operator symbol (`+`, `−`, `×`, `÷`) centered between them
5. Destroys old grid frames, creates new `tk.Frame` containers
6. Fills each frame with a grid of `tk.Entry` widgets pre-filled with `"0"`

---

### `LinearPage._parse_cell(s)` *(static method)*

**Purpose:** Parses a single matrix cell string into a `complex` number using `_parse_num()`. Returns `0` for blank cells.

---

### `LinearPage._read_grid(self, cells)`

**Purpose:** Reads all entries from a grid of `tk.Entry` widgets and converts them to a **NumPy array**.

- Calls `_parse_cell()` on every cell
- Creates a `numpy` array with `dtype=complex`
- If no imaginary parts exist, returns a real-valued array instead

**Parameters:**
- `cells` — 2D list of `tk.Entry` widgets (`self._cellsA` or `self._cellsB`)

**Returns:** `numpy.ndarray` (real or complex)

---

### `LinearPage._calc(self)`

**Purpose:** Reads both matrices, performs the selected operation, and displays the result.

**Operations:**
| Selection | Computation |
|---|---|
| Addition (A+B) | `A + B` |
| Subtraction (A-B) | `A - B` |
| Multiplication (A×B) | `A @ B` (matrix multiplication) |
| Division (A×B⁻¹) | `A @ numpy.linalg.inv(B)` |

**Error handling:**
- Invalid cell values → shows error modal
- Dimension mismatch, singular matrix, etc. → catches `Exception` and shows the error message

**Result:** Shows each row of the result matrix in a modal via `_show_modal()`.

---

## FourierPage — Fourier Series

```python
class FourierPage(Page):
```

**Purpose:** Computes the **Fourier series approximation** of a piecewise-defined function and displays the coefficients plus a graph comparing the original function against the Fourier approximation.

**Class constants:**
- `_MAX_PIECES = 6` — maximum number of piecewise pieces

---

### `FourierPage._draw_static(self)`

**Purpose:** Renders the static portions of the Fourier page UI:
- Title "FOURIER SERIES"
- Input card with column headers: `#`, `f(x) Expression`, `From x =`, `To x =`
- A container frame (`self._piece_container`) where piece rows are placed
- **+ ADD PIECE** and **REMOVE LAST** buttons
- **Harmonics N** spinbox (1–20, default 5) — controls how many Fourier terms to compute
- **Period T** entry (optional; if blank, auto-calculated from the piece ranges)
- A usage tip
- CALCULATE button

Starts with two default pieces: `f(x)=0` on `[-π, 0]` and `f(x)=x` on `[0, π]`.

---

### `FourierPage._add_piece(self, default_expr="0", x_from="0", x_to="1")`

**Purpose:** Adds a new **piecewise piece row** to the input container.

Each row contains:
- A `#N` index label
- An expression entry field (e.g. `x**2`, `sin(x)`, `0`)
- A "for" label
- A `From x =` entry
- A `≤ x ≤` label
- A `To x =` entry

The piece data is appended to `self._pieces` as a dictionary: `{frame, expr, from, to}`.

**Parameters:**
- `default_expr` — initial value for the expression field
- `x_from`, `x_to` — initial interval boundaries

---

### `FourierPage._remove_piece(self)`

**Purpose:** Removes the **last piece row** from the UI and the `self._pieces` list. Minimum of 1 piece is enforced (does nothing if only one piece remains).

---

### `FourierPage._calc(self)`

**Purpose:** Core computation function that calculates Fourier series coefficients using **SymPy symbolic integration**.

**Steps:**
1. Reads `N` (number of harmonics) from the spinbox
2. Parses each piece: normalizes expressions, evaluates `x_from`/`x_to` numerically, and calls `sp.sympify()` on the function expression
3. Determines the period `T`:
   - If the Period field is filled, uses that value
   - Otherwise, `T = x_max - x_min` (auto-detected from piece ranges)
4. Computes half-period `L = T / 2`
5. Integrates to compute:
   - `a₀ = (2/T) × Σ ∫ f(x) dx` over each piece
   - `aₙ = (2/T) × Σ ∫ f(x)·cos(nπx/L) dx` for n = 1..N
   - `bₙ = (2/T) × Σ ∫ f(x)·sin(nπx/L) dx` for n = 1..N
6. Builds a readable formula string showing non-negligible terms (> 1e-10)
7. Calls `_show_result()` with all computed data

---

### `FourierPage._show_result(self, T, L, a0, an_list, bn_list, formula, pieces_data, N, x_sym)`

**Purpose:** Opens a large **1140 × 700 result modal** window containing:

1. **Header bar** — "FOURIER SERIES — RESULT"
2. **Graph canvas** — Plots two curves on a dark background:
   - Original piecewise function `f(x)` — white dashed line
   - Fourier approximation with N terms — orange solid line
   - Grid lines, axis labels, and a legend
3. **Info panel** with:
   - Period T, L = T/2, a₀, a₀/2
   - Coefficient table showing n, aₙ, bₙ for up to 8 terms (indicates more if N > 8)
   - Full formula string
4. **CLOSE button**

**Graph functions defined internally:**
- `f_piecewise(xv)` — evaluates the original function at a point, with periodic extension
- `f_fourier(xv)` — evaluates the Fourier sum at a point

---

## LaplacePage — Laplace Transform

```python
class LaplacePage(Page):
```

**Purpose:** Computes the **Laplace Transform** of a time-domain function `f(t)` or the **Inverse Laplace Transform** of a frequency-domain function `F(s)` using SymPy's symbolic engine.

---

### `LaplacePage._draw(self)`

**Purpose:** Renders the Laplace calculator UI:
- Title "LAPLACE TRANSFORM"
- A **mode dropdown** (Combobox) to select:
  - `"Laplace Transform"` — input uses variable `t`
  - `"Inverse Laplace"` — input uses variable `s`
- An expression input field (pre-filled with `exp(-t)`)
- Pressing `<Return>` also triggers calculation
- A CALCULATE button

---

### `LaplacePage._calc(self)`

**Purpose:** Reads the expression, performs the selected symbolic transform, and shows the result.

**Steps:**
1. Gets the raw expression string and strips whitespace
2. Defines SymPy symbols: `t` (positive real), `s` (complex frequency)
3. Builds a local symbol dict by extending `_SAFE_LOCALS` with `t` and `s`
4. Parses the expression with `sp.sympify(_normalize(raw), locals=locs)`
5. Depending on mode:
   - **Laplace Transform:** calls `sp.laplace_transform(expr, t, s, noconds=True)`
   - **Inverse Laplace:** calls `sp.inverse_laplace_transform(expr, s, t, noconds=True)`
6. Builds result rows with the original expression, the transform result (formatted with `sp.pretty()`), and a simplified version via `sp.simplify()`
7. Displays via `_show_modal()`

**Error handling:** Any SymPy exception (unrecognized function, unsupported transform, etc.) is caught and shown as an error in the modal.

---

## Shared Modal Helper

### `_show_modal(app, title, rows, error=None, hdr_color=NAVY)`

**Purpose:** A **standalone function** (not inside any class) that creates a generic result popup. Used by `LinearPage` and `LaplacePage` to display results without duplicating modal code.

**Parameters:**
- `app` — the `App` instance (used to center the modal)
- `title` — header title text
- `rows` — list of `(label, value)` tuples to display in the result card
- `error` — if set, shows only this error message in red instead of rows
- `hdr_color` — header bar background color (each calculator uses its own accent color)

**Behavior:**
- Modal height is auto-calculated from the number of rows: `120 + len(rows) * 46 + 80`
- Minimum height is 300 pixels
- Content is displayed in a card (`CARD` color background) with alternating row dividers
- A CLOSE button at the bottom destroys the modal

---

## Navigation Flow

```
HomePage
  ├── START ──────────────────────────────► TopicsPage
  │                                             ├── Complex Numbers ─► ComplexPage
  │                                             ├── Linear Algebra ──► LinearPage
  │                                             ├── Fourier Series ──► FourierPage
  │                                             └── Laplace Transform ► LaplacePage
  ├── ABOUT ─────────────────────────────► AboutPage (5 slides)
  └── CREATOR ───────────────────────────► CreatorPage

All pages with a top bar:
  BACK → previous page   |   HOME → HomePage
```

---

## Accepted Input Formats

All calculator pages use the shared `_parse_num()` / `_normalize()` pipeline. The following formats are accepted everywhere:

| Format | Example | Notes |
|---|---|---|
| Integer | `3` | |
| Float | `3.14` | |
| Fraction | `1/2` | |
| Exponent (Python) | `2**3` | Result: 8 |
| Exponent (MATLAB) | `2^3` | Converted to `2**3` |
| Imaginary unit | `3+2i`, `3+2j`, `3+2*I` | All equivalent |
| Constants | `pi`, `e` | SymPy symbolic |
| Functions | `sqrt(2)`, `sin(pi/4)`, `exp(-1)` | See `_SAFE_LOCALS` |
| Complex expressions | `(1+2i)*(3-i)`, `sqrt(2)+pi*i` | Full arithmetic |
| Implicit multiply | `2pi`, `3I` | Converted to `2*pi`, `3*I` |
| Unicode operators | `3×2`, `6÷3` | Converted to `*`, `/` |
