import tkinter as tk          # GUI framework for all windows, canvases, and widgets
from tkinter import ttk       # styled widgets like Combobox (dropout)
import cmath                  # complex math functions: phase angle, polar form
import math                   # standard math: degrees conversion, cos, sin
import re as _re              # regular expressions used to clean up user input strings
import numpy as np            # numerical matrix operations for Linear Algebra
import sympy as sp            # symbolic math engine for integration, Laplace, simplification
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    implicit_application,
)
import matplotlib
matplotlib.use("TkAgg")       # must be set before pyplot is imported
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

_PARSE_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    implicit_application,
)


def _unit_step(x):
    # Use Heaviside(x, 1) so u(0)=1, matching common engineering convention.
    return sp.Heaviside(x, 1)

# ── Shared input parser (used by all pages) ───────────────────────────────────
# Only these names are recognized when evaluating user-typed expressions — nothing else can be executed
_SAFE_LOCALS = {
    # constants
    'pi': sp.pi, 'e': sp.E, 'E': sp.E, 'I': sp.I,
    'inf': sp.oo, 'oo': sp.oo,
    # functions
    'sqrt': sp.sqrt, 'cbrt': lambda x: sp.Rational(1,3)**x,
    'exp':  sp.exp,  'log': sp.log, 'ln': sp.log, 'log10': lambda x: sp.log(x, 10),
    'sin':  sp.sin,  'cos': sp.cos,  'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan, 'atan2': sp.atan2,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
    'abs':  sp.Abs,  'Abs': sp.Abs,  'sign': sp.sign,
    'floor': sp.floor, 'ceil': sp.ceiling,
    're': sp.re, 'im': sp.im, 'arg': sp.arg, 'conj': sp.conjugate,
    # signals (for Laplace)
    'u': _unit_step, 'U': _unit_step, 'H': _unit_step,
    'step': _unit_step, 'heaviside': _unit_step,
    'delta': sp.DiracDelta, 'dirac': sp.DiracDelta, 'impulse': sp.DiracDelta,
    'DiracDelta': sp.DiracDelta, 'δ': sp.DiracDelta,
}

def _normalize(raw):
    """Normalize a user math string to SymPy-compatible syntax.

    Handles:
      * ^ -> **          (MATLAB/calculator exponent)
      * × -> *  ÷ -> /  (unicode operators)
      * bare i or j  ->  I  (imaginary unit, skips pi/sin/etc.)
      * implicit mult: 2I -> 2*I,  3pi -> 3*pi
            * Laplace aliases: δ(t) -> delta(t), e^-at -> exp(-a*t)
    """
    s = raw.strip()
    s = s.replace('\u00d7', '*').replace('\u00f7', '/').replace('^', '**')
    s = s.replace('δ', 'delta')
    # Replace standalone imaginary i/j not inside a word  (e.g. j not in 'pi','sin')
    s = _re.sub(r'(?<![A-Za-z_])j(?![A-Za-z_0-9])', 'I', s)
    s = _re.sub(r'(?<![A-Za-z_])i(?![A-Za-z_0-9])', 'I', s)
    # Implicit multiplication: digit directly before I or pi or e
    s = _re.sub(r'(\d)(I\b)',  r'\1*\2', s)
    s = _re.sub(r'(\d)(pi\b)', r'\1*\2', s)
    s = _re.sub(r'(?<=[\d\)])(pi|e|I)\b', r'*\1', s)
    # Trig shorthand support: cos2t, cos 2t, sin3t -> cos(2*t), sin(3*t)
    s = _re.sub(
        r'\b(sin|cos|tan|sinh|cosh|tanh)\s*([+-]?\d+(?:\.\d+)?)\s*\*?\s*t\b',
        lambda m: f"{m.group(1)}({m.group(2)}*t)",
        s,
    )
    s = _re.sub(
        r'\b(sin|cos|tan|sinh|cosh|tanh)\s*t\b',
        lambda m: f"{m.group(1)}(t)",
        s,
    )
    # Common Laplace shorthand support: e^-t, e^-5t, e^-2.5t
    s = _re.sub(r'\be\*\*-\s*t\b', 'exp(-t)', s)
    s = _re.sub(r'\be\*\*-\s*([0-9]+(?:\.[0-9]+)?)\s*\*?\s*t\b', r'exp(-\1*t)', s)
    return s


def _parse_symbolic(raw, locs):
    """Parse symbolic math safely with implicit multiplication/application enabled."""
    return parse_expr(
        _normalize(raw),
        local_dict=locs,
        transformations=_PARSE_TRANSFORMS,
        evaluate=True,
    )


def _laplace_preprocess(raw):
    """Apply laplace.py-style preprocessing for forward Laplace inputs."""
    expr_str = _normalize(raw).strip()
    expr_str = _re.sub(r'\bu\s*\(\s*t\s*\)', '1', expr_str)
    expr_str = _re.sub(r'\*\s*u\s*\(\s*t\s*\)', '', expr_str)
    expr_str = _re.sub(r'u\s*\(\s*t\s*\)\s*\*', '', expr_str)
    expr_str = _re.sub(r'\bdelta\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
    expr_str = _re.sub(r'\bimpulse\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
    expr_str = _re.sub(r'\bdirac\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
    expr_str = _re.sub(r'\bdelta\b', 'DiracDelta(t)', expr_str)
    expr_str = _re.sub(r'\bimpulse\b', 'DiracDelta(t)', expr_str)
    expr_str = _re.sub(r'\bdirac\b', 'DiracDelta(t)', expr_str)
    if not expr_str:
        expr_str = '0'
    return expr_str
    
def _laplace_clean_text(text):
    """Normalize Laplace display text for readability."""
    return (
        str(text)
        .replace("**", "^")
        .replace("DiracDelta(t)", "delta(t)")
        .replace("Heaviside(t, 1)", "u(t)")
        .replace("Heaviside(t)", "u(t)")
    )

def _laplace_format_parts(result, s_sym):
    """Split a rational expression into printable whole/fraction terms."""
    result = sp.simplify(sp.apart(result, s_sym))
    terms = sp.Add.make_args(result)
    parts = []
    for term in terms:
        numer, denom = sp.fraction(term)
        numer = sp.expand(numer)
        denom = sp.expand(denom)
        if denom == 1:
            parts.append(("whole", _laplace_clean_text(numer), None))
        else:
            parts.append(("frac", _laplace_clean_text(numer), _laplace_clean_text(denom)))
    return parts

def _laplace_render_parts(parts):
    """Render fractions in stacked/vertical form without decorative boxes."""
    lines_num, lines_bar, lines_den = [], [], []
    pad = 3

    for i, part in enumerate(parts):
        sign = "   "
        if i > 0:
            raw = part[1]
            sign = " - " if raw.startswith("-") else " + "

        if part[0] == "whole":
            val = part[1].lstrip("-") if (i > 0 and part[1].startswith("-")) else part[1]
            width = len(sign) + len(val)
            lines_num.append(sign + val)
            lines_bar.append(" " * width)
            lines_den.append(" " * width)
        else:
            n_str, d_str = part[1], part[2]
            inner_w = max(len(n_str), len(d_str)) + pad
            lines_num.append(sign + n_str.center(inner_w))
            lines_bar.append(" " * len(sign) + ("─" * inner_w))
            lines_den.append(" " * len(sign) + d_str.center(inner_w))

    row1 = "".join(lines_num).rstrip()
    row2 = "".join(lines_bar).rstrip()
    row3 = "".join(lines_den).rstrip()
    if row2.strip():
        return f"{row1}\n{row2}\n{row3}"
    return row1

def _parse_num(raw):
    """Parse a numeric expression string to Python complex.

    Accepts: integers, floats, fractions (1/2), exponents (2**3 or 2^3),
    complex numbers (3+2i, 3+2j, 3+2*I), constants (pi, e),
    and functions (sqrt, sin, cos, exp, log, abs, …).
    """
    s = _normalize(raw) or '0'                                 # clean the string; default to '0' if blank
    val = sp.sympify(s, locals=_SAFE_LOCALS, evaluate=True)    # parse into a SymPy expression using the safe whitelist
    return complex(val.evalf())                                # evaluate to a numeric value and return as Python complex

# ── Window dimensions ─────────────────────────────────────────────────────────
W, H = 1280, 720  # fixed window size in pixels — all pages are drawn to fit exactly this

# ── Color palette ─────────────────────────────────────────────────────────────
# All colors are defined here so the whole app theme can be changed in one place
SKY    = "#29ABE2"  # main background color
RAY    = "#55CCFF"  # spotlight ray color on the home screen
PURPLE = "#5C3E9E"  # footer bar color
GREEN  = "#6DD820"  # titles, START button, positive highlights
GRN_DK = "#3A8A00"  # dark green for button drop-shadow
RED    = "#E84040"  # BACK button and error messages
RED_DK = "#A01010"  # dark red for button drop-shadow
YELLOW = "#F5C518"  # HOME button and Laplace highlights
YEL_DK = "#B08800"  # dark yellow for button drop-shadow
NAVY   = "#1B2A72"  # text outlines, header bars
WHITE  = "#FFFFFF"  # general text color
CARD   = "#5ABDE8"  # card/panel background color


# ── Drawing helpers ───────────────────────────────────────────────────────────
def rr(cv, x1, y1, x2, y2, r=22, **kw):
    """Smooth rounded rectangle as a polygon."""
    # Each corner is defined as 3 points so Tkinter's smooth=True curves it correctly
    p = [
        x1+r, y1,  x2-r, y1,
        x2,   y1,  x2,   y1+r,
        x2,   y2-r, x2,  y2,
        x2-r, y2,  x1+r, y2,
        x1,   y2,  x1,   y2-r,
        x1,   y1+r, x1,  y1,
        x1+r, y1,
    ]
    return cv.create_polygon(p, smooth=True, **kw)


def otxt(cv, x, y, text, font, fill=WHITE, ol=NAVY, ow=3, **kw):
    """Canvas text with a solid outline effect."""
    # Draw the outline copies first by offsetting in every direction, then draw the real text on top
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx or dy:  # skip (0,0) — that is the main text drawn below
                cv.create_text(x + dx, y + dy, text=text, font=font, fill=ol, **kw)
    return cv.create_text(x, y, text=text, font=font, fill=fill, **kw)


def cbtn(cv, x1, y1, x2, y2, label, font, color, dark, cmd, r=20):
    """Canvas button with drop-shadow, body, label — all bound to cmd."""
    rr(cv, x1+4, y1+4, x2+4, y2+4, r=r, fill=dark, outline="")   # shadow drawn 4px offset behind the button
    b = rr(cv, x1, y1, x2, y2, r=r, fill=color, outline="")       # the visible button face
    t = cv.create_text((x1+x2)//2, (y1+y2)//2, text=label, font=font, fill=WHITE)  # centered label
    for tag in (b, t):
        cv.tag_bind(tag, "<Button-1>", lambda e, c=cmd: c())  # both shape and text are clickable
    return b, t  # return the canvas IDs so callers can bind additional events if needed

# ── App shell ─────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()              # initialize the root Tkinter window
        self.title("ECETHON")
        self.geometry(f"{W}x{H}")      # set the fixed window size
        self.resizable(False, False)   # prevent the user from resizing the window

        self._pages = {}  # dictionary mapping page name → page frame instance
        for name, cls in [
            ("home",    HomePage),
            ("topics",  TopicsPage),
            ("about",   AboutPage),
            ("creator", CreatorPage),
            ("complex", ComplexPage),
            ("linear",  LinearPage),
            # ("lineareq", LinearEquationPage),  # hidden from App pages
            ("fourier", FourierPage),
            ("laplace", LaplacePage),
        ]:
            p = cls(self)                           # create each page and pass the App as parent
            p.place(x=0, y=0, width=W, height=H)    # stack all pages on top of each other at (0,0)
            self._pages[name] = p

        self.go("home")  # start the app by showing the home screen

    def go(self, name):
        for p in self._pages.values():
            p.lower()              # push every page to the bottom of the stacking order
        page = self._pages[name]
        if hasattr(page, "on_show"):   # some pages (e.g. AboutPage) need to reset state when shown
            page.on_show()
        page.lift()                    # bring the target page to the top so it becomes visible


# ── Base page ─────────────────────────────────────────────────────────────────
class Page(tk.Frame):
    def __init__(self, app):
        super().__init__(app, width=W, height=H, bg=SKY)  # full-size frame matching the window
        self._app = app  # keep a reference to the App so any page can trigger navigation

    def go(self, name):  # shortcut so subclasses can call self.go() instead of self._app.go()
        self._app.go(name)

    def _topbar(self, cv, back="home", help_cmd=None):
        cbtn(cv, 30, 18, 180, 68, "BACK",
             ("OPTIVagRound-Bold", 20), RED, RED_DK, lambda: self.go(back), r=18)  # BACK navigates to the previous page
        otxt(cv, W//2, 44, "ECETHON",
             ("OPTIVagRound-Bold", 26), fill=GREEN, ol=NAVY, ow=2)  # centered app name label
        if help_cmd:
            cbtn(cv, W-230, 18, W-190, 68, "?",
                 ("OPTIVagRound-Bold", 22), YELLOW, YEL_DK, help_cmd, r=14)
        cbtn(cv, W-180, 18, W-30, 68, "HOME",
             ("OPTIVagRound-Bold", 20), YELLOW, YEL_DK, lambda: self.go("home"), r=18)  # HOME always goes to the landing screen

    def _show_how_to_use(self, rows):
        _show_modal(self._app, "HOW TO USE", rows, hdr_color=NAVY)

    @staticmethod
    def _purplebar(cv):
        cv.create_rectangle(0, H-70, W, H, fill=PURPLE, outline="")  # draws the purple footer strip at the bottom of every page


# ── Home page ─────────────────────────────────────────────────────────────────
class HomePage(Page):
    def __init__(self, app):
        super().__init__(app)
        cv = tk.Canvas(self, width=W, height=H, bd=0, highlightthickness=0, bg=SKY)
        cv.place(x=0, y=0)
        self._draw(cv)

    def _draw(self, cv):
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")

        # Stage spotlight rays from top-center
        cx = W // 2
        # each tuple is (horizontal offset from center, half-width at top) — rays spread outward like stage lights
        for ox, hw in [(0, 18), (110, 14), (-110, 14),
                       (225, 11), (-225, 11), (345, 9), (-345, 9)]:
            cv.create_polygon(
                cx+ox-hw,    0,          # top-left corner of the ray
                cx+ox+hw,    0,          # top-right corner of the ray
                cx+ox+hw*14, H*0.85,    # bottom-right (widened by factor 14)
                cx+ox-hw*14, H*0.85,    # bottom-left (widened by factor 14)
                fill=RAY, outline="",
            )

        self._purplebar(cv)

        # Main title
        otxt(cv, W//2, 235, "ECETHON",
             ("OPTIVagRound-Bold", 96), fill=GREEN, ol=NAVY, ow=7)

        # START button
        cbtn(cv, W//2-155, 400, W//2+155, 475, "START",
             ("OPTIVagRound-Bold", 30), GREEN, GRN_DK, lambda: self.go("topics"), r=30)

        # ABOUT / CREATOR in purple bar
        cbtn(cv, 120, H-62, 390, H-10, "ABOUT",
             ("OPTIVagRound-Bold", 22), RED, RED_DK, self._about, r=22)
        cbtn(cv, W-390, H-62, W-120, H-10, "CREATOR",
             ("OPTIVagRound-Bold", 22), YELLOW, YEL_DK, self._creator, r=22)

    # ── Modals ────────────────────────────────────────────────────────────────
    def _modal(self, title, body):
        w = tk.Toplevel(self)     # create a child popup window
        w.title(title)
        w.geometry("480x230")
        w.resizable(False, False)
        w.configure(bg=SKY)
        w.transient(self._app)    # keep the popup attached to the main window
        w.grab_set()              # block all interaction with other windows until this one is closed
        tk.Label(w, text=title, font=("OPTIVagRound-Bold", 26),
                 bg=SKY, fg=GREEN).pack(pady=(20, 6))
        tk.Label(w, text=body, font=("OPTIVagRound-Bold", 14),
                 bg=SKY, fg=WHITE, justify="center").pack()
        tk.Button(w, text="Close", font=("OPTIVagRound-Bold", 14),
                  bg=RED, fg=WHITE, relief="flat", padx=20, pady=6,
                  cursor="hand2", command=w.destroy).pack(pady=18)

    def _about(self):
        self.go("about")    # navigate to the 5-slide About page

    def _creator(self):
        self.go("creator")  # navigate to the Creator profile page


# ── Creator page ────────────────────────────────────────────────────────────────
class CreatorPage(Page):
    # HOME button hit-zone measured from Creator.png (1280×720)
    _BTN_HOME = (1090, 18, 1248, 70)

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._img_ref = None
        self._draw()

    def _draw(self):
        cv = self.cv
        cv.delete("all")

        # ── Full-screen image ─────────────────────────────────────────────────
        try:
            self._img_ref = tk.PhotoImage(file="creator/Creator.png")  # load the PNG from the creator/ subfolder
            cv.create_image(0, 0, anchor="nw", image=self._img_ref)    # draw it starting from the top-left corner
        except Exception:
            # graceful fallback if the image file is missing
            cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
            cv.create_text(W//2, H//2, text="creator/Creator.png not found",
                           font=("OPTIVagRound-Bold", 24), fill=WHITE)

        # ── Invisible HOME hit-zone ───────────────────────────────────────────
        x1, y1, x2, y2 = self._BTN_HOME
        zone = cv.create_rectangle(x1, y1, x2, y2, fill="", outline="")  # transparent clickable area over the image's HOME button
        cv.tag_bind(zone, "<Button-1>", lambda e: self.go("home"))        # clicking navigates home
        cv.tag_bind(zone, "<Enter>",    lambda e: cv.config(cursor="hand2"))  # pointer cursor on hover
        cv.tag_bind(zone, "<Leave>",    lambda e: cv.config(cursor=""))        # restore default cursor on leave


# ── About page (5-slide deck) ─────────────────────────────────────────────────
class AboutPage(Page):
    _PURPLE = "#8B5CF6"
    _TX     = 70          # body text left anchor x
    _TW     = W - 140     # body text wrap width

    def __init__(self, app):
        super().__init__(app)
        self._slide = 0
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._render()

    def on_show(self):
        """Called by App.go() — always start at slide 0."""
        self._slide = 0   # reset to the first slide every time the user navigates to About
        self._render()

    # ── slide navigation ──────────────────────────────────────────────────────
    def _go(self, idx):
        self._slide = idx   # update the current slide index
        self._render()      # redraw the entire canvas for the new slide

    # ── full redraw ───────────────────────────────────────────────────────────
    def _render(self):
        cv = self.cv
        cv.delete("all")
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)

        # BACK (hidden on first slide)
        if self._slide > 0:
            cbtn(cv, 30, 18, 180, 68, "BACK",
                 ("OPTIVagRound-Bold", 20), RED, RED_DK,
                 lambda: self._go(self._slide - 1), r=18)
            otxt(cv, W//2, 44, "About the Project",
                 ("OPTIVagRound-Bold", 20), fill=WHITE, ol=NAVY, ow=2)

        # HOME always visible
        cbtn(cv, W-180, 18, W-30, 68, "HOME",
             ("OPTIVagRound-Bold", 20), YELLOW, YEL_DK,
             lambda: self.go("home"), r=18)

        # NEXT is hidden on the last slide so the user cannot go past slide 4
        if self._slide < 4:
            cbtn(cv, W-230, H-65, W-30, H-10, "NEXT",
                 ("OPTIVagRound-Bold", 22), GREEN, GRN_DK,
                 lambda: self._go(self._slide + 1), r=22)

        # use the slide index to call the matching slide method (0→_s0, 1→_s1, etc.)
        [self._s0, self._s1, self._s2, self._s3, self._s4][self._slide]()

    # ── shared drawing helpers ────────────────────────────────────────────────
    def _card(self, y1, y2):
        """Slightly darker card background for formula blocks."""
        rr(self.cv, 60, y1, W-60, y2, r=16, fill="#2A6A9A", outline="")

    def _body(self, y, text, size=13):
        self.cv.create_text(self._TX, y, anchor="nw", width=self._TW,
                            justify="left", fill=WHITE,
                            font=("OPTIVagRound-Bold", size), text=text)

    def _fline(self, y, text, color=WHITE, size=14):
        otxt(self.cv, W//2, y, text,
             ("OPTIVagRound-Bold", size), fill=color, ol=NAVY, ow=2)

    def _flabel(self, y):
        self.cv.create_text(W//2, y, text="FORMULAS:",
                            font=("OPTIVagRound-Bold", 14), fill=NAVY)

    # ── Slide 0 · About the Project ──────────────────────────────────────────
    def _s0(self):
        cv = self.cv
        otxt(cv, W//2, 108, "About the Project",
             ("OPTIVagRound-Bold", 48), fill=WHITE, ol=NAVY, ow=5)

        self._body(185, (
            "This project is an interactive computational tool developed for Advanced "
            "Engineering Mathematics. It is designed to help students solve and understand "
            "high-level mathematical problems in a simpler and more organized way."
        ))

        self._body(295, "The system focuses on key topics such as:")

        # colored topic names row
        for name, color, xc in [
            ("Linear Algebra",    GREEN,        195),
            ("Complex Numbers",   self._PURPLE, 455),
            ("Fourier Series",    GREEN,        715),
            ("Laplace Transform", YELLOW,       980),
        ]:
            otxt(cv, xc, 335, name,
                 ("OPTIVagRound-Bold", 17), fill=color, ol=NAVY, ow=2)

        self._body(370, (
            "It allows users to input mathematical problems and generate accurate solutions "
            "that support learning and problem-solving."
        ))

        self._body(440, (
            "The main purpose of this project is to connect mathematical theory with practical "
            "application. By using a Python-based program, the project helps make complex "
            "engineering mathematics easier to analyze, compute, and understand."
        ))

    # ── Slide 1 · Linear Algebra ──────────────────────────────────────────────
    def _s1(self):
        cv = self.cv
        otxt(cv, W//2, 145, "LINEAR ALGEBRA",
             ("OPTIVagRound-Bold", 46), fill=WHITE, ol=NAVY, ow=5)

        self._body(210, (
            "Description:  Linear Algebra is a branch of mathematics that deals with vectors, "
            "matrices, and linear equations. It focuses on understanding relationships in "
            "multi-dimensional space and solving systems of equations efficiently."
        ))

        self._flabel(338)
        self._card(350, 425)
        self._fline(387, "Ax = b", WHITE, 28)

        self._body(440, (
            "Application:  Linear Algebra is widely used in engineering for circuit analysis, "
            "computer graphics, machine learning, signal processing, and solving real-world "
            "systems involving multiple variables."
        ))

    # ── Slide 2 · Complex Numbers ─────────────────────────────────────────────
    def _s2(self):
        cv = self.cv
        otxt(cv, W//2, 143, "COMPLEX NUMBERS",
             ("OPTIVagRound-Bold", 44), fill=self._PURPLE, ol=NAVY, ow=5)

        self._body(200, (
            "Description:  Complex Numbers have both a real and imaginary part, written as "
            "z = x + jy, where x is the real part and y is the coefficient of the imaginary unit j. "
            "They represent quantities that cannot be expressed using real numbers alone."
        ), size=13)

        self._flabel(316)
        self._card(328, 490)

        left_lines = [
            "General Form:  z = x + jy",
            "Polar Form:  z = r(cos\u03b8 + jsin\u03b8)",
            "Where r = \u221a(x\u00b2+y\u00b2),  \u03b8 = tan\u207b\u00b9(y/x)",
            "Addition:  (x+jy)\u00b1(a+jb) = (x\u00b1a)+j(y\u00b1b)",
        ]
        right_lines = [
            "Multiplication: (x+jy)(a+jb) = (xa\u2212yb)+j(xb+ya)",
            "Division: (x+jy)/(a+jb) = (x+jy)(a\u2212jb)/(a\u00b2+b\u00b2)",
            "Modulus:  |z| = \u221a(x\u00b2+y\u00b2)",
            "Conjugate:  z\u0305 = x \u2212 jy",
        ]
        for i, line in enumerate(left_lines):
            cv.create_text(90, 348+i*35, anchor="nw",
                           text=line, font=("OPTIVagRound-Bold", 13), fill=WHITE)
        for i, line in enumerate(right_lines):
            cv.create_text(660, 348+i*35, anchor="nw",
                           text=line, font=("OPTIVagRound-Bold", 13), fill=WHITE)

        self._body(498, (
            "Application:  Complex numbers are vital in ECE \u2014 they model AC circuits via phasors, "
            "compute impedance, phase differences, and frequency behaviour of resistors, "
            "capacitors, and inductors, simplifying analysis of voltages and currents."
        ), size=12)

    # ── Slide 3 · Fourier Series ──────────────────────────────────────────────
    def _s3(self):
        otxt(self.cv, W//2, 143, "FOURIER SERIES",
             ("OPTIVagRound-Bold", 46), fill=GREEN, ol=NAVY, ow=5)

        self._body(205, (
            "Description:  The Fourier series represents periodic signals as the sum of simple "
            "sine and cosine waves, breaking down complex signals into basic trigonometric "
            "components. It transforms a time-domain signal into a frequency-based description, "
            "making it easier to analyze and understand."
        ))

        self._flabel(338)
        self._card(350, 490)
        for i, f in enumerate([
            "g(t) = a\u2080 + \u03a3 [ a\u2099 cos(2n\u03c0t/T) + b\u2099 sin(2n\u03c0t/T) ]",
            "a\u2080 = (1/T) \u222b\u2080\u1d40 f(t) dt",
            "a\u2099 = (2/T) \u222b\u2080\u1d40 f(t) cos(2n\u03c0t/T) dt",
            "b\u2099 = (2/T) \u222b\u2080\u1d40 f(t) sin(2n\u03c0t/T) dt",
        ]):
            self._fline(370+i*32, f, GREEN, 14)

        self._body(498, (
            "Application:  The Fourier series is widely used in electronics to analyze circuits "
            "and signals involving AC currents, filters, and communication signals. It helps "
            "engineers understand wave behaviour under capacitors, inductors, and amplifiers, "
            "aiding circuit design and signal transmission optimization."
        ), size=12)

    # ── Slide 4 · Laplace Transform ───────────────────────────────────────────
    def _s4(self):
        otxt(self.cv, W//2, 143, "LAPLACE TRANSFORM",
             ("OPTIVagRound-Bold", 40), fill=YELLOW, ol=NAVY, ow=5)

        self._body(205, (
            "Description:  The Laplace transform, named after Pierre-Simon Laplace, is an "
            "integral transform that converts a function of a real variable t (time domain) "
            "into a function of a complex variable s (frequency domain / s-domain or s-plane)."
        ))

        self._flabel(318)
        self._card(330, 468)
        for i, f in enumerate([
            "F(s) = \u222b\u208b\u221e\u207f\u221e e\u207b\u02e2\u1d57 f(t) dt",
            "f(t) = \u2112\u207b\u00b9{F}(t) = (1/2\u03c0i) \u222b\u209c\u208b\u1d35\u221e^\u1d40\u207a\u1d35\u221e e\u02e2\u1d57 F(s) ds",
            "\u2112{f}(s) = \u222b\u2080^\u221e f(t) e\u207b\u02e2\u1d57 dt",
        ]):
            self._fline(355+i*38, f, YELLOW, 14)

        self._body(476, (
            "Application:  The Laplace Transform is widely used in Electronics Engineering to "
            "analyze circuits dealing with time-dependent signals such as switching, charging, "
            "and discharging. It converts complex time-domain circuit equations into simpler "
            "algebraic equations in the s-domain, making differential equations easier to solve."
        ), size=12)


# ── Topics page ───────────────────────────────────────────────────────────────
class TopicsPage(Page):
    _TOPICS = [
        ("Complex\nNumbers",   "complex",  GREEN,     GRN_DK),
        ("Linear\nAlgebra",    "linear",   "#8B5CF6", "#5B2CC0"),
        # ("Linear\nEquation",   "lineareq", "#7C3AED", "#5B21B6"),  # hidden from Topics
        ("Fourier\nSeries",    "fourier",  "#F97316", "#C05010"),
        ("Laplace\nTransform", "laplace",  "#EC4899", "#A01060"),
    ]

    def __init__(self, app):
        super().__init__(app)
        cv = tk.Canvas(self, width=W, height=H, bd=0, highlightthickness=0, bg=SKY)
        cv.place(x=0, y=0)
        self._draw(cv)

    def _draw(self, cv):
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        self._topbar(cv)

        otxt(cv, W//2, 148, "SELECT A TOPIC",
             ("OPTIVagRound-Bold", 44), fill=WHITE, ol=NAVY, ow=3)

        # Keep cards fitting in one row even when more topics are added.
        gap = 20
        card_w = min(235, (W - 120 - gap * (len(self._TOPICS) - 1)) // len(self._TOPICS))
        total = len(self._TOPICS) * card_w + (len(self._TOPICS) - 1) * gap
        sx = (W - total) // 2   # starting x so all cards are centered horizontally
        y1, y2 = 225, 450       # top and bottom y coordinates for every card

        for i, (label, dest, color, dark) in enumerate(self._TOPICS):
            x1 = sx + i * (card_w + gap)  # left edge of this card
            x2 = x1 + card_w
            rr(cv, x1+5, y1+5, x2+5, y2+5, r=24, fill=dark, outline="")  # drop shadow
            b = rr(cv, x1, y1, x2, y2, r=24, fill=color, outline="")      # card face
            t = cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text=label, font=("OPTIVagRound-Bold", 20),
                               fill=WHITE, justify="center")
            for tag in (b, t):
                cv.tag_bind(tag, "<Button-1>", lambda e, d=dest: self.go(d))  # clicking card OR label navigates to the topic


# ── Complex Numbers page ──────────────────────────────────────────────────────

class ComplexPage(Page):

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._draw()

    def _draw(self):
        cv = self.cv
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        help_rows = [
            ("Input:", "Complex expression using i/j, pi, e, sqrt, sin, cos, exp, log."),
            ("How to use:", "Type in the box, then press CALCULATE or Enter."),
            ("Result:", "Shows a+bj plus real/imag, magnitude, and phase."),
            ("Hotkeys:", "Enter = Calculate"),
        ]
        self._topbar(cv, "topics", lambda: self._show_how_to_use(help_rows))

        otxt(cv, W//2, 148, "COMPLEX NUMBERS",
             ("OPTIVagRound-Bold", 54), fill=WHITE, ol=NAVY, ow=4)

        cx = W // 2
        cw = 880
        x1 = cx - cw // 2
        x2 = cx + cw // 2

        # ── Input card ────────────────────────────────────────────────────────
        rr(cv, x1, 190, x2, 330, r=30, fill=CARD, outline="")

        cv.create_text(cx, 228, anchor="center",
                       font=("OPTIVagRound-Bold", 16), fill=NAVY,
                       text="Enter expression  (e.g.  3+2i,  (1/2+3i)*(2-i),  sqrt(2)+pi*i,  2^3 + 1j)")

        self.expr = tk.Entry(self, width=52,
                             font=("OPTIVagRound-Bold", 20),
                             bg="#D6EEFA", fg=NAVY,
                             relief="flat", highlightthickness=2,
                             highlightbackground=NAVY,
                             insertbackground=NAVY,
                             justify="center")
        self.expr.place(x=x1+40, y=260, height=44, width=cw-80)
        self.expr.bind("<Return>", lambda e: self._calc())  # pressing Enter triggers calculation without clicking the button

        # ── Calculate button ──────────────────────────────────────────────────
        cbtn(cv, cx-130, 345, cx+130, 400, "CALCULATE",
             ("OPTIVagRound-Bold", 20), GREEN, GRN_DK, self._calc, r=24)

    # ── Calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        raw = self.expr.get()
        if not raw.strip():  # do nothing if the input box is empty
            self._result_modal(error="⚠  Please enter an expression")
            return
        try:
            res = _parse_num(raw)  # parse the string into a Python complex number
        except ZeroDivisionError:
            self._result_modal(error="⚠  Division by zero")
            return
        except Exception:
            self._result_modal(
                error="⚠  Invalid expression\n"
                      "Examples: (3+2i)*(1-i)  |  1/2+sqrt(3)*i  |  2^4  |  pi+e*i")
            return

        r, i  = res.real, res.imag           # split the result into real and imaginary parts
        sign  = "+" if i >= 0 else "-"       # determine the sign character for display
        r_str = f"{r:g}{sign}{abs(i):g}j"   # build a human-readable complex string e.g. "3+4j"
        mag   = abs(res)                      # magnitude = distance from origin = √(r²+i²)
        phase = math.degrees(cmath.phase(res))  # phase angle in degrees from the positive real axis
        self._result_modal(r_str=r_str, r=r, i=i, mag=mag, phase=phase)

    # ── Result modal ──────────────────────────────────────────────────────────
    def _result_modal(self, *, r_str=None, r=None, i=None,
                      mag=None, phase=None, error=None):
        MW, MH = 540, 420
        m = tk.Toplevel(self)
        m.title("Result")
        m.geometry(f"{MW}x{MH}")
        m.resizable(False, False)
        m.configure(bg=SKY)
        m.transient(self._app)
        m.grab_set()

        # Center the popup over the main window by calculating the offset from the app's current position
        m.update_idletasks()  # force Tkinter to compute the window's actual size before positioning
        mx = self._app.winfo_x() + (W - MW) // 2
        my = self._app.winfo_y() + (H - MH) // 2
        m.geometry(f"+{mx}+{my}")

        cv = tk.Canvas(m, width=MW, height=MH,
                       bd=0, highlightthickness=0, bg=SKY)
        cv.place(x=0, y=0)

        # Header bar
        cv.create_rectangle(0, 0, MW, 64, fill=NAVY, outline="")
        otxt(cv, MW//2, 32, "RESULT", ("OPTIVagRound-Bold", 26),
             fill=GREEN, ol=NAVY, ow=3)

        if error:
            cv.create_text(MW//2, MH//2, text=error,
                           font=("OPTIVagRound-Bold", 18), fill=RED,
                           justify="center")
        else:
            # Result card
            rr(cv, 30, 80, MW-30, MH-70, r=24, fill=CARD, outline="")

            rows = [
                ("Result:",         f"({r_str})"),    # full complex number
                ("Real part:",      f"{r}"),           # x component
                ("Imaginary part:", f"{i}"),           # y component
                ("Magnitude:",      f"{mag:.6f}"),     # |z| = √(x²+y²)
                ("Phase:",          f"{phase:.2f}\u00b0"),  # angle in degrees
            ]
            lx, vx = 55, 280  # x positions for the label column and value column
            for idx, (label, value) in enumerate(rows):
                y = 118 + idx * 46  # each row is 46 pixels apart
                cv.create_text(lx, y, anchor="w",
                               font=("OPTIVagRound-Bold", 17), fill=NAVY, text=label)
                cv.create_text(vx, y, anchor="w",
                               font=("OPTIVagRound-Bold", 17), fill=NAVY, text=value)
                if idx < len(rows) - 1:
                    cv.create_line(50, y+23, MW-50, y+23,
                                   fill="#90C8E8", width=1)  # thin divider line between rows

        # Close button
        cbtn(cv, MW//2-80, MH-58, MW//2+80, MH-12, "CLOSE",
             ("OPTIVagRound-Bold", 17), RED, RED_DK, m.destroy, r=20)


# ── Shared result-modal mixin ────────────────────────────────────────────────
def _show_modal(app, title, rows, error=None, hdr_color=NAVY):
    max_chars = 0
    if rows:
        for _, value in rows:
            for ln in str(value).splitlines() or [""]:
                max_chars = max(max_chars, len(ln))

    MW = max(580, min(940, 320 + max_chars * 8))
    row_heights = []
    if rows:
        for _, value in rows:
            line_count = str(value).count("\n") + 1
            row_heights.append(max(46, 14 + line_count * 20))
        content_h = sum(row_heights)
    else:
        content_h = 100

    MH = 120 + content_h + 80  # height grows with row count and multiline content
    MH = max(MH, 300)  # enforce a minimum height so the modal never looks too small
    m = tk.Toplevel()
    m.title(title)
    m.geometry(f"{MW}x{MH}")
    m.resizable(False, False)
    m.configure(bg=SKY)
    m.transient(app)
    m.grab_set()
    m.update_idletasks()
    mx = app.winfo_x() + (W - MW) // 2
    my = app.winfo_y() + (H - MH) // 2
    m.geometry(f"+{mx}+{my}")
    cv = tk.Canvas(m, width=MW, height=MH, bd=0, highlightthickness=0, bg=SKY)
    cv.place(x=0, y=0)
    cv.create_rectangle(0, 0, MW, 64, fill=hdr_color, outline="")
    otxt(cv, MW//2, 32, title, ("OPTIVagRound-Bold", 22), fill=GREEN, ol=hdr_color, ow=3)
    if error:
        cv.create_text(MW//2, MH//2 - 20, text=error,
                       font=("OPTIVagRound-Bold", 16), fill=RED, justify="center")
    else:
        rr(cv, 24, 76, MW-24, MH-68, r=22, fill=CARD, outline="")
        lx, vx = 44, 190
        y = 108
        for idx, (label, value) in enumerate(rows):
            value_text = str(value)
            line_count = value_text.count("\n") + 1
            row_h = row_heights[idx] if idx < len(row_heights) else 46
            value_font = ("Consolas", 13) if line_count > 1 else ("OPTIVagRound-Bold", 15)

            cv.create_text(lx, y, anchor="nw", font=("OPTIVagRound-Bold", 15),
                           fill=NAVY, text=label)
            cv.create_text(vx, y, anchor="nw", font=value_font,
                           fill=NAVY, text=value_text)
            if idx < len(rows) - 1:
                cv.create_line(40, y + row_h - 8, MW-40, y + row_h - 8,
                               fill="#90C8E8", width=1)
            y += row_h
    cbtn(cv, MW//2-80, MH-58, MW//2+80, MH-12, "CLOSE",
         ("OPTIVagRound-Bold", 16), RED, RED_DK, m.destroy, r=18)


# ── Linear Algebra page ───────────────────────────────────────────────────────
class LinearPage(Page):
    _PURPLE = "#8B5CF6"
    _PRPDK  = "#5B2CC0"
    _EQ_OP  = "Linear Equations (solve variables)"
    _MAX    = 5
    _CELL_W = 88
    _CELL_H = 44
    _PAD    = 5

    def __init__(self, app, equation_only=False, page_title="LINEAR ALGEBRA"):
        super().__init__(app)
        self._equation_only = equation_only
        self._page_title = page_title
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._cellsA: list[list[tk.Entry]] = []
        self._cellsB: list[list[tk.Entry]] = []
        self._grid_frame_A = tk.Frame(self, bg="#3A6FA8")
        self._grid_frame_B = tk.Frame(self, bg="#3A6FA8")
        self._eq_frame = tk.Frame(self, bg="#1B4F8A")
        self._eq_vars = None
        self._eq_text = None
        self._op_lbl_id = None
        self._draw_static()
        self._build_equation_panel()
        self._build_grids()

    # ── static chrome ─────────────────────────────────────────────────────────
    def _draw_static(self):
        cv = self.cv
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        help_rows = [
            ("Input:", "Set sizes, then fill Matrix A and B. Or pick Linear Equations (solve variables)."),
            ("How to use:", "CALCULATE for matrix ops; SOLVE X,Y,Z for A*X=B or augmented A."),
            ("Result:", "Matrix output or variable solution."),
            ("Hotkeys:", "None"),
        ]
        self._topbar(cv, "topics", lambda: self._show_how_to_use(help_rows))

        # title
        otxt(cv, W//2, 105, self._page_title,
             ("OPTIVagRound-Bold", 46), fill=WHITE, ol=NAVY, ow=4)

        if self._equation_only:
            self.op_var = tk.StringVar(value=self._EQ_OP)
            self._hint_id = cv.create_text(
                W//2, 706, font=("OPTIVagRound-Bold", 11),
                fill=WHITE, text="Example: 3x + y = 9 | x + 2y = 8   (supports x, y, z, a, b, c, ...)"
            )
            cbtn(cv, W//2-140, 636, W//2+140, 686, "CALCULATE",
                 ("OPTIVagRound-Bold", 20), self._PURPLE, self._PRPDK, self._calc, r=26)
            return

        # ── control bar card ──────────────────────────────────────────────────
        rr(cv, 30, 128, W-30, 192, r=20, fill="#1B4F8A", outline="")

        # Operation label + combobox
        cv.create_text(52, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="Operation:")
        ops = ["Addition (A+B)", "Subtraction (A-B)",
             "Multiplication (A×B)", "Division (A×B⁻¹)", self._EQ_OP]
        self.op_var = tk.StringVar(value=ops[0])
        self.op_cb  = ttk.Combobox(self, textvariable=self.op_var, values=ops,
                                   font=("OPTIVagRound-Bold", 13),
                                   state="readonly", width=22)
        self.op_cb.place(x=148, y=142, height=36)
        self.op_var.trace_add("write", lambda *_: self._build_grids())  # rebuild grids automatically whenever the operation changes

        # A size spinboxes  (each spinbox widget ~68px wide at this font)
        cv.create_text(400, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="A rows:")
        self.rA = tk.StringVar(value="2")
        self._spin(472, 142, self.rA)          # ends ~540
        cv.create_text(548, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="cols:")
        self.cA = tk.StringVar(value="2")
        self._spin(602, 142, self.cA)          # ends ~670

        # B size spinboxes
        cv.create_text(686, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="B rows:")
        self.rB = tk.StringVar(value="2")
        self._spin(758, 142, self.rB)          # ends ~826
        cv.create_text(834, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="cols:")
        self.cB = tk.StringVar(value="2")
        self._spin(888, 142, self.cB)          # ends ~956

        # SET button
        cbtn(cv, 968, 138, 1072, 178, "SET",
             ("OPTIVagRound-Bold", 13), self._PURPLE, self._PRPDK,
             self._build_grids, r=14)

        # hint
        self._hint_id = cv.create_text(
            W//2, 706, font=("OPTIVagRound-Bold", 11),
            fill=WHITE,
            text="Use A and B for A*X=B, or augmented A (e.g. 6 7 8 -> 6x+7y=8). Supports complex values."
        )

        # Two actions: matrix operation result, and variable solve for A*X=B
        cbtn(cv, W//2-310, 636, W//2-20, 686, "CALCULATE",
             ("OPTIVagRound-Bold", 20), self._PURPLE, self._PRPDK, self._calc, r=26)
        cbtn(cv, W//2+20, 636, W//2+310, 686, "SOLVE X,Y,Z",
             ("OPTIVagRound-Bold", 20), GREEN, GRN_DK, self._solve_from_matrices, r=26)

    def _spin(self, x, y, var):
        # read-only spinbox so users can only increment/decrement (not type invalid values)
        sb = tk.Spinbox(self, from_=1, to=self._MAX, textvariable=var,
                        width=2, font=("OPTIVagRound-Bold", 14),
                        bg="#D6EEFA", fg=NAVY, relief="flat",
                        highlightthickness=1, highlightbackground=NAVY,
                        justify="center", state="readonly",
                        command=self._build_grids)  # rebuilds the matrix grids every time the dimension changes
        sb.place(x=x, y=y, height=34)
        return sb

    def _build_equation_panel(self):
        # Dedicated panel for solving systems like: 3x + y = 9, x + 2y = 8
        self._eq_frame = tk.Frame(self, bg="#1B4F8A", padx=14, pady=12)
        tk.Label(self._eq_frame, text="Enter one equation per line:",
                 font=("OPTIVagRound-Bold", 13), bg="#1B4F8A",
                 fg=WHITE).pack(anchor="w")

        vars_row = tk.Frame(self._eq_frame, bg="#1B4F8A")
        vars_row.pack(fill="x", pady=(8, 8))
        tk.Label(vars_row, text="Variables (optional, comma-separated):",
                 font=("OPTIVagRound-Bold", 12), bg="#1B4F8A",
                 fg=WHITE).pack(side="left")

        self._eq_vars = tk.Entry(vars_row, font=("OPTIVagRound-Bold", 12),
                                 bg="#D6EEFA", fg=NAVY, relief="flat",
                                 highlightthickness=2,
                                 highlightbackground=self._PURPLE,
                                 insertbackground=NAVY, justify="left")
        self._eq_vars.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=4)
        self._eq_vars.insert(0, "x, y")

        self._eq_text = tk.Text(self._eq_frame, font=("Consolas", 13),
                                bg="white", fg=NAVY, relief="flat",
                                highlightthickness=2,
                                highlightbackground=self._PURPLE,
                                insertbackground=NAVY)
        self._eq_text.pack(fill="both", expand=True)
        self._eq_text.insert("1.0", "3x + y = 9\nx + 2y = 8")

    # ── grid builder ──────────────────────────────────────────────────────────
    def _build_grids(self, *_):
        if self._equation_only:
            self._grid_frame_A.place_forget()
            self._grid_frame_B.place_forget()
            if self._op_lbl_id:
                for _id in self._op_lbl_id:
                    self.cv.delete(_id)
                self._op_lbl_id = None
            self._eq_frame.place(x=80, y=220, width=W-160, height=390)
            self.cv.itemconfigure(
                self._hint_id,
                text="Example: 3x + y = 9 | x + 2y = 8   (supports x, y, z, a, b, c, ...)"
            )
            return

        op = self.op_var.get()
        if op == self._EQ_OP:
            self._grid_frame_A.place_forget()
            self._grid_frame_B.place_forget()
            if self._op_lbl_id:
                for _id in self._op_lbl_id:
                    self.cv.delete(_id)
                self._op_lbl_id = None
            self._eq_frame.place(x=80, y=220, width=W-160, height=390)
            self.cv.itemconfigure(
                self._hint_id,
                text="Example: 3x + y = 9 | x + 2y = 8   (supports x, y, z, a, b, c, ...)"
            )
            return

        self._eq_frame.place_forget()
        self.cv.itemconfigure(self._hint_id,
                              text="Use A and B for A*X=B, or augmented A (e.g. 6 7 8 -> 6x+7y=8). Supports complex values.")

        CW, CH, P = self._CELL_W, self._CELL_H, self._PAD

        ef = dict(font=("OPTIVagRound-Bold", 13), bg="white", fg=NAVY,
                  relief="flat", highlightthickness=2,
                  highlightbackground="#8B5CF6", insertbackground=NAVY,
                  justify="center", width=8)

        # ── labels on canvas ──────────────────────────────────────────────────
        if self._op_lbl_id:
            for _id in self._op_lbl_id:
                self.cv.delete(_id)  # remove old "Matrix A", "Matrix B", and operator labels before redrawing
        ids = []
        rA = int(self.rA.get()); cA = int(self.cA.get())  # current dimensions for Matrix A
        rB = int(self.rB.get()); cB = int(self.cB.get())  # current dimensions for Matrix B
        gw_A = cA * (CW + P*2) + 20  # pixel width of the Matrix A grid
        gw_B = cB * (CW + P*2) + 20  # pixel width of the Matrix B grid
        A_LEFT  = 80                                          # Matrix A always starts near the left edge
        B_RIGHT = W - 80
        B_LEFT  = B_RIGHT - gw_B                             # Matrix B is right-aligned
        B_LEFT  = max(B_LEFT, A_LEFT + gw_A + 120)           # ensure at least 120px gap between the two grids
        op_x    = (A_LEFT + gw_A + B_LEFT) // 2              # operator symbol is centered between the two grids

        ids.append(self.cv.create_text(
            A_LEFT + 10, 204, anchor="w",
            font=("OPTIVagRound-Bold", 16), fill=NAVY, text="Matrix A"))
        ids.append(self.cv.create_text(
            B_LEFT + 10, 204, anchor="w",
            font=("OPTIVagRound-Bold", 16), fill=NAVY, text="Matrix B"))
        # map the operation name to its mathematical symbol for display between the matrices
        sym = {"Addition (A+B)": "+", "Subtraction (A-B)": "−",
               "Multiplication (A×B)": "×", "Division (A×B⁻¹)": "÷"}.get(op, "?")
        ids.append(self.cv.create_text(
            op_x, 370, font=("OPTIVagRound-Bold", 52), fill=NAVY, text=sym))
        self._op_lbl_id = ids

        TOP = 218

        # ── Matrix A ──────────────────────────────────────────────────────────
        self._grid_frame_A.destroy()  # destroy the old frame so its entry cells are also removed
        self._grid_frame_A = tk.Frame(self, bg="#1B4F8A", padx=10, pady=10)
        self._cellsA = []  # reset the 2D list of Entry widgets for Matrix A
        for r in range(rA):
            row_e = []
            for c in range(cA):
                e = tk.Entry(self._grid_frame_A, **ef)
                e.insert(0, "0")  # pre-fill every cell with 0 so the user only changes what they need
                e.grid(row=r, column=c, padx=P, pady=P, ipadx=3, ipady=5)
                row_e.append(e)
            self._cellsA.append(row_e)  # store each row as a list inside the 2D list
        gh_A = rA * (CH + P*2) + 20
        self._grid_frame_A.place(x=A_LEFT, y=TOP)

        # ── Matrix B ──────────────────────────────────────────────────────────
        self._grid_frame_B.destroy()
        self._grid_frame_B = tk.Frame(self, bg="#1B4F8A", padx=10, pady=10)
        self._cellsB = []
        for r in range(rB):
            row_e = []
            for c in range(cB):
                e = tk.Entry(self._grid_frame_B, **ef)
                e.insert(0, "0")
                e.grid(row=r, column=c, padx=P, pady=P, ipadx=3, ipady=5)
                row_e.append(e)
            self._cellsB.append(row_e)
        gh_B = rB * (CH + P*2) + 20
        self._grid_frame_B.place(x=B_LEFT, y=TOP)

    # ── read grids → numpy (supports complex, fractions, exponents) ─────────────
    @staticmethod
    def _parse_cell(s):
        s = s.strip() or "0"  # treat blank cells as zero
        return _parse_num(s)   # reuse the shared parser so complex inputs like 3+4j work

    def _read_grid(self, cells):
        # build a 2D NumPy array from all Entry widget values
        arr = np.array([[self._parse_cell(cells[r][c].get())
                         for c in range(len(cells[r]))]
                        for r in range(len(cells))], dtype=complex)
        if not np.any(arr.imag):
            return arr.real  # return a real array if no imaginary parts exist (cleaner output)
        return arr

    @staticmethod
    def _default_var_symbols(count):
        names = ["x", "y", "z", "w", "v", "u"]
        syms = [sp.Symbol(n) for n in names[:count]]
        if count > len(names):
            syms.extend(sp.Symbol(f"x{i+1}") for i in range(len(names), count))
        return syms

    @staticmethod
    def _fmt_solution(val):
        val = sp.simplify(val)
        if getattr(val, "free_symbols", set()):
            return str(val)
        try:
            c = complex(val.evalf())
            if abs(c.imag) < 1e-12:
                return f"{c.real:.6g}"
            sign = "+" if c.imag >= 0 else "-"
            return f"{c.real:.6g}{sign}{abs(c.imag):.6g}j"
        except Exception:
            return str(val)

    def _equation_from_row(self, coeff_row, rhs, vars_list):
        terms = []
        for coeff, var in zip(coeff_row, vars_list):
            c = complex(coeff)
            if abs(c.real) < 1e-12 and abs(c.imag) < 1e-12:
                continue

            if abs(c.imag) < 1e-12:
                rv = c.real
                if abs(rv - 1.0) < 1e-12:
                    terms.append(f"{var}")
                elif abs(rv + 1.0) < 1e-12:
                    terms.append(f"-{var}")
                else:
                    terms.append(f"{rv:.6g}{var}")
            else:
                terms.append(f"({self._fmt_solution(c)}){var}")

        lhs = " + ".join(terms) if terms else "0"
        lhs = lhs.replace("+ -", "- ")
        return f"{lhs} = {self._fmt_solution(rhs)}"

    def _solve_from_matrices(self):
        if self._equation_only:
            self._calc_linear_equations()
            return

        if self.op_var.get() == self._EQ_OP:
            self._calc_linear_equations()
            return

        try:
            A = np.asarray(self._read_grid(self._cellsA), dtype=complex)
            B = np.asarray(self._read_grid(self._cellsB), dtype=complex)
        except Exception:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error="⚠  Invalid value in a matrix cell", hdr_color=self._PRPDK)
            return

        if A.ndim != 2 or B.ndim != 2:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error="⚠  Matrices must be 2D", hdr_color=self._PRPDK)
            return

        rA, cA = A.shape
        rB, cB = B.shape

        if cA < 1:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error="⚠  Matrix A must have at least 1 column", hdr_color=self._PRPDK)
            return

        use_augmented = not (rB == rA and cB == 1)
        if use_augmented:
            if cA < 2:
                _show_modal(self._app, "SOLVE X,Y,Z", [],
                            error="⚠  For augmented mode, Matrix A must be n×(m+1)",
                            hdr_color=self._PRPDK)
                return
            coeff = A[:, :-1]
            rhs = A[:, -1].reshape(rA, 1)
            source_label = "Mode: augmented Matrix A"
        else:
            coeff = A
            rhs = B.reshape(rB, 1)
            source_label = "Mode: A*X = B"

        eq_count, var_count = coeff.shape
        if var_count < 1:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error="⚠  No variable columns found", hdr_color=self._PRPDK)
            return

        vars_list = self._default_var_symbols(var_count)
        A_sp = sp.Matrix(coeff.tolist())
        b_sp = sp.Matrix(rhs.tolist())

        try:
            sol_set = sp.linsolve((A_sp, b_sp), *vars_list)
        except Exception as e:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error=f"⚠  Solve error: {e}", hdr_color=self._PRPDK)
            return

        if sol_set == sp.EmptySet:
            _show_modal(self._app, "SOLVE X,Y,Z", [],
                        error="⚠  No solution", hdr_color=self._PRPDK)
            return

        sol_tuple = next(iter(sol_set))
        eq_rows = [self._equation_from_row(coeff[i], rhs[i][0], vars_list)
                   for i in range(eq_count)]
        rows = [
            ("System:", f"{eq_count} equations, {var_count} unknowns"),
            ("Variables:", ", ".join(str(v) for v in vars_list)),
            ("Interpretation:", source_label),
        ]
        rows.extend((f"Eq {i+1}:", eq_text) for i, eq_text in enumerate(eq_rows))
        rows.extend((f"{var} =", self._fmt_solution(val))
                    for var, val in zip(vars_list, sol_tuple))
        _show_modal(self._app, "SOLVE X,Y,Z", rows, hdr_color=self._PRPDK)

    # ── calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        if self._equation_only:
            self._calc_linear_equations()
            return

        op = self.op_var.get()
        if op == self._EQ_OP:
            self._calc_linear_equations()
            return

        try:
            A = self._read_grid(self._cellsA)  # convert Matrix A entries to a NumPy array
            B = self._read_grid(self._cellsB)  # convert Matrix B entries to a NumPy array
        except Exception:
            _show_modal(self._app, "LINEAR ALGEBRA", [],
                        error="⚠  Invalid value in a cell", hdr_color=self._PRPDK)
            return

        def fmt(v):
            # format a single matrix element: show as real if no imaginary part, else show as complex
            v = complex(v)
            if v.imag == 0:
                return f"{v.real:.4g}"
            sign = "+" if v.imag >= 0 else "-"
            return f"{v.real:.4g}{sign}{abs(v.imag):.4g}j"

        rA, cA = A.shape
        rB, cB = B.shape

        try:
            if op == "Addition (A+B)":
                if (rA, cA) != (rB, cB):
                    _show_modal(
                        self._app,
                        "A + B",
                        [],
                        error=f"⚠  Undefined: Matrix sizes must match exactly ({rA}x{cA} and {rB}x{cB})",
                        hdr_color=self._PRPDK,
                    )
                    return
                C, title = A + B, "A + B"              # element-wise addition
            elif op == "Subtraction (A-B)":
                if (rA, cA) != (rB, cB):
                    _show_modal(
                        self._app,
                        "A - B",
                        [],
                        error=f"⚠  Undefined: Matrix sizes must match exactly ({rA}x{cA} and {rB}x{cB})",
                        hdr_color=self._PRPDK,
                    )
                    return
                C, title = A - B, "A − B"              # element-wise subtraction
            elif op == "Multiplication (A×B)":
                if cA != rB:
                    _show_modal(
                        self._app,
                        "A × B",
                        [],
                        error=f"⚠  Undefined: columns of A must equal rows of B ({cA} != {rB})",
                        hdr_color=self._PRPDK,
                    )
                    return
                C, title = A @ B, "A × B"              # true matrix multiplication (dot product)
            elif op == "Division (A×B⁻¹)":
                if rB != cB:
                    _show_modal(
                        self._app,
                        "A × B⁻¹",
                        [],
                        error=f"⚠  Undefined: Matrix B must be square ({rB}x{cB})",
                        hdr_color=self._PRPDK,
                    )
                    return
                if cA != rB:
                    _show_modal(
                        self._app,
                        "A × B⁻¹",
                        [],
                        error=f"⚠  Undefined: columns of A must equal rows of B ({cA} != {rB})",
                        hdr_color=self._PRPDK,
                    )
                    return
                C, title = A @ np.linalg.inv(B), "A × B⁻¹"  # A divided by B = A multiplied by the inverse of B
            else:
                return
            result_rows = [(f"Row {i+1}:", "  ".join(fmt(v) for v in r))  # format each row of the result matrix
                           for i, r in enumerate(C)]
            _show_modal(self._app, title, result_rows, hdr_color=self._PRPDK)
        except Exception as e:
            _show_modal(self._app, "LINEAR ALGEBRA", [],
                        error=f"⚠  {e}", hdr_color=self._PRPDK)  # catches shape mismatch, singular matrix, etc.

    @staticmethod
    def _parse_linear_expr(raw, locs):
        return parse_expr(
            _normalize(raw),
            local_dict=locs,
            transformations=_PARSE_TRANSFORMS,
            evaluate=True,
        )

    def _calc_linear_equations(self):
        lines = [ln.strip() for ln in self._eq_text.get("1.0", "end").splitlines() if ln.strip()]
        if not lines:
            _show_modal(self._app, "LINEAR EQUATIONS", [],
                        error="⚠  Enter at least one equation", hdr_color=self._PRPDK)
            return

        locs = {**_SAFE_LOCALS}
        raw_vars = self._eq_vars.get().strip()
        var_names = [name.strip() for name in raw_vars.replace(";", ",").split(",") if name.strip()]

        if var_names:
            bad = [name for name in var_names if not _re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)]
            if bad:
                _show_modal(self._app, "LINEAR EQUATIONS", [],
                            error=f"⚠  Invalid variable name(s): {', '.join(bad)}",
                            hdr_color=self._PRPDK)
                return
            for name in var_names:
                locs[name] = sp.Symbol(name)

        equations = []
        try:
            for line in lines:
                if "=" in line:
                    left, right = line.split("=", 1)
                else:
                    left, right = line, "0"
                lhs = self._parse_linear_expr(left, locs)
                rhs = self._parse_linear_expr(right, locs)
                equations.append(sp.Eq(lhs, rhs))
        except Exception as e:
            _show_modal(self._app, "LINEAR EQUATIONS", [],
                        error=f"⚠  Parse error: {e}", hdr_color=self._PRPDK)
            return

        if var_names:
            vars_list = [sp.Symbol(name) for name in var_names]
        else:
            vars_set = set()
            for eq in equations:
                vars_set.update(eq.free_symbols)
            vars_list = sorted(vars_set, key=lambda s: s.name)

        if not vars_list:
            _show_modal(self._app, "LINEAR EQUATIONS", [],
                        error="⚠  No variables found", hdr_color=self._PRPDK)
            return

        try:
            linear_eqs = [eq.lhs - eq.rhs for eq in equations]
            A, b = sp.linear_eq_to_matrix(linear_eqs, vars_list)
            sol_set = sp.linsolve((A, b), *vars_list)
        except Exception as e:
            _show_modal(self._app, "LINEAR EQUATIONS", [],
                        error=f"⚠  Linear solve error: {e}", hdr_color=self._PRPDK)
            return

        if sol_set == sp.EmptySet:
            _show_modal(self._app, "LINEAR EQUATIONS", [],
                        error="⚠  No solution", hdr_color=self._PRPDK)
            return

        sol_tuple = next(iter(sol_set))
        all_numeric = all(v.is_number for v in sol_tuple)
        if all_numeric:
            try:
                arr = np.array([float(sp.N(v)) for v in sol_tuple], dtype=float)
                vec_str = np.array2string(arr, precision=6, separator=" ")
            except Exception:
                vec_str = "[" + ", ".join(str(sp.simplify(v)) for v in sol_tuple) + "]"
        else:
            vec_str = "[" + ", ".join(str(sp.simplify(v)) for v in sol_tuple) + "]"

        rows = [
            ("Variables:", ", ".join(str(v) for v in vars_list)),
            ("Solution vector:", vec_str),
        ]
        rows.extend((f"{var} =", str(sp.simplify(val))) for var, val in zip(vars_list, sol_tuple))
        _show_modal(self._app, "LINEAR EQUATIONS", rows, hdr_color=self._PRPDK)


class LinearEquationPage(LinearPage):
    def __init__(self, app):
        super().__init__(app, equation_only=True,
                         page_title="SYSTEM OF LINEAR EQUATION")

    def on_show(self):
        self._build_grids()


# ── Fourier Series page ───────────────────────────────────────────────────────
class FourierPage(Page):
    _ORG   = "#F97316"
    _ORGDK = "#C05010"
    _n_sym = sp.Symbol("n", integer=True, positive=True)

    _DEFAULT_HARMONICS = 10

    _MAX_PIECES = 6

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._pieces = []
        self._draw_static()
        self._add_piece("0", "-pi", "0")   # default piece 1
        self._add_piece("x", "0",  "pi")   # default piece 2

    # ── static chrome ──────────────────────────────────────────────────────────
    def _draw_static(self):
        cv = self.cv
        y_shift = 43
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        help_rows = [
            ("Input:", "Add piece rows with f(x) and interval bounds."),
            ("How to use:", "Use + ADD PIECE / REMOVE LAST, then CALCULATE."),
            ("Result:", "Shows coefficients, plot, and final series (N=10)."),
            ("Hotkeys:", "None"),
        ]
        self._topbar(cv, "topics", lambda: self._show_how_to_use(help_rows))
        otxt(cv, W//2, 105 + y_shift, "FOURIER SERIES",
             ("OPTIVagRound-Bold", 46), fill=WHITE, ol=NAVY, ow=4)

        # Main input card
        rr(cv, 30, 128 + y_shift, W-30, 598 + y_shift, r=24, fill=CARD, outline="")

        # Column headers
        cv.create_text(90,  153 + y_shift, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="#")
        cv.create_text(280, 153 + y_shift, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY,
                       text="f(x)  Expression")
        cv.create_text(500, 153 + y_shift, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="From  x =")
        cv.create_text(650, 153 + y_shift, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="To  x =")
        cv.create_line(50, 166 + y_shift, W-50, 166 + y_shift, fill="#4A7AB5", width=1)

        # Piece row container
        self._piece_container = tk.Frame(self, bg=CARD)
        self._piece_container.place(x=50, y=172 + y_shift, width=W-100, height=270)

        # Add / Remove buttons
        cbtn(cv, 50,  454 + y_shift, 220, 492 + y_shift, "+ ADD PIECE",
             ("OPTIVagRound-Bold", 12), self._ORG, self._ORGDK,
             self._add_piece, r=14)
        cbtn(cv, 228, 454 + y_shift, 398, 492 + y_shift, "REMOVE LAST",
             ("OPTIVagRound-Bold", 12), "#DC2626", "#7F1D1D",
             self._remove_piece, r=14)

        # CALCULATE button
        cbtn(cv, W//2-165, 516 + y_shift, W//2+165, 576 + y_shift, "CALCULATE",
             ("OPTIVagRound-Bold", 22), self._ORG, self._ORGDK, self._calc, r=28)

    # ── piece row management ──────────────────────────────────────────────────
    def _add_piece(self, default_expr="0", x_from="0", x_to="1"):
        if len(self._pieces) >= self._MAX_PIECES:
            return
        idx = len(self._pieces)
        ef = dict(font=("OPTIVagRound-Bold", 13), bg="white", fg=NAVY,
                  relief="flat", highlightthickness=2,
                  highlightbackground=self._ORG, insertbackground=NAVY,
                  justify="center")

        row = tk.Frame(self._piece_container, bg=CARD)
        row.pack(fill="x", pady=3)

        tk.Label(row, text=f"#{idx+1}", font=("OPTIVagRound-Bold", 12),
                 bg=CARD, fg=NAVY, width=4).pack(side="left", padx=(0, 6))

        expr_var = tk.StringVar(value=default_expr)
        tk.Entry(row, textvariable=expr_var, width=30, **ef).pack(
            side="left", ipady=5, padx=(0, 10))

        tk.Label(row, text="for", font=("OPTIVagRound-Bold", 12),
                 bg=CARD, fg=NAVY).pack(side="left", padx=4)

        from_var = tk.StringVar(value=x_from)
        tk.Entry(row, textvariable=from_var, width=9, **ef).pack(
            side="left", ipady=5, padx=(0, 4))

        tk.Label(row, text="≤ x ≤", font=("OPTIVagRound-Bold", 12),
                 bg=CARD, fg=NAVY).pack(side="left", padx=4)

        to_var = tk.StringVar(value=x_to)
        tk.Entry(row, textvariable=to_var, width=9, **ef).pack(
            side="left", ipady=5)

        self._pieces.append({"frame": row, "expr": expr_var,
                              "from": from_var, "to": to_var})

    def _remove_piece(self):
        if len(self._pieces) <= 1:
            return
        p = self._pieces.pop()
        p["frame"].destroy()

    # ── calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        if not self._pieces:
            return

        x_sym = sp.Symbol("x")
        n_sym = self._n_sym

        N = self._DEFAULT_HARMONICS

        locs = {**_SAFE_LOCALS, 'x': x_sym, 'Piecewise': sp.Piecewise}

        # Parse each piece and collect symbolic bounds
        pieces_sym = []   # (f_expr, xa_sym, xb_sym)
        for p in self._pieces:
            raw = _normalize(p["expr"].get().strip())
            try:
                xa_sym = sp.sympify(_normalize(p["from"].get().strip()), locals=locs)
                xb_sym = sp.sympify(_normalize(p["to"].get().strip()),   locals=locs)
                f_expr = sp.sympify(raw, locals=locs)
            except Exception as e:
                _show_modal(self._app, "FOURIER SERIES", [],
                            error=f"⚠  Parse error: {e}", hdr_color=self._ORGDK)
                return
            pieces_sym.append((f_expr, xa_sym, xb_sym))

        # Auto-detect limits from outermost piece bounds
        a_sym = pieces_sym[0][1]
        b_sym = pieces_sym[-1][2]
        L_sym = (b_sym - a_sym) / 2   # half-period

        # Build a SymPy Piecewise from all piece rows
        pw_args = [(f, (x_sym >= xa) & (x_sym <= xb))
                   for f, xa, xb in pieces_sym]
        pw_args.append((sp.Integer(0), True))   # fallback for any gap
        f_full = sp.Piecewise(*pw_args)

        try:
            # Compute symbolic general coefficients  (same formulas as asdd2.py)
            a0_sym = sp.simplify(
                sp.Rational(1, 2) / L_sym *
                sp.integrate(f_full, (x_sym, a_sym, b_sym)))

            an_sym = sp.simplify(
                sp.Integer(1) / L_sym *
                sp.integrate(f_full * sp.cos(n_sym * sp.pi * x_sym / L_sym),
                             (x_sym, a_sym, b_sym)))

            bn_sym = sp.simplify(
                sp.Integer(1) / L_sym *
                sp.integrate(f_full * sp.sin(n_sym * sp.pi * x_sym / L_sym),
                             (x_sym, a_sym, b_sym)))

            # Build the Fourier series by substituting n = 1 … N, then simplify
            series = a0_sym
            for k in range(1, N + 1):
                ak = an_sym.subs(n_sym, k)
                bk = bn_sym.subs(n_sym, k)
                series += ak * sp.cos(k * sp.pi * x_sym / L_sym)
                series += bk * sp.sin(k * sp.pi * x_sym / L_sym)
            series = sp.simplify(series)

        except Exception as e:
            _show_modal(self._app, "FOURIER SERIES", [],
                        error=f"⚠  Integration error: {e}", hdr_color=self._ORGDK)
            return

        self._show_result(f_full, a_sym, b_sym, L_sym, N,
                          a0_sym, an_sym, bn_sym, series, x_sym)

    # ── result modal ──────────────────────────────────────────────────────────
    def _show_result(self, f_expr, a_sym, b_sym, L_sym, N,
                     a0_sym, an_sym, bn_sym, series, x_sym):
        MW, MH = 1140, 700
        m = tk.Toplevel()
        m.title("Fourier Series — Result")
        m.configure(bg=NAVY)
        m.resizable(False, False)
        sx = max(0, (m.winfo_screenwidth()  - MW) // 2)
        sy = max(0, (m.winfo_screenheight() - MH) // 2)
        m.geometry(f"{MW}x{MH}+{sx}+{sy}")

        # ── Header bar ────────────────────────────────────────────────────────
        hcv = tk.Canvas(m, width=MW, height=56, bg=self._ORGDK,
                        bd=0, highlightthickness=0)
        hcv.place(x=0, y=0)
        hcv.create_text(MW//2, 28, text="FOURIER SERIES — RESULT",
                        font=("OPTIVagRound-Bold", 22), fill=WHITE)

        # ── Graph (matplotlib, left column) ───────────────────────────────────
        GW, GH = 650, 310
        graph_frame = tk.Frame(m, bg="#0D1B2A", width=GW, height=GH)
        graph_frame.place(x=18, y=62)
        graph_frame.pack_propagate(False)

        fig_ref = [None]
        try:
            a_f    = float(a_sym.evalf())
            b_f    = float(b_sym.evalf())
            x_vals = np.linspace(a_f, b_f, 1000)

            f_lamb = sp.lambdify(x_sym, f_expr, "numpy")
            s_lamb = sp.lambdify(x_sym, series,  "numpy")
            y_orig = np.array(f_lamb(x_vals), dtype=float)
            y_ser  = np.real(np.array(s_lamb(x_vals), dtype=complex)).astype(float)

            fig, ax = plt.subplots(figsize=(GW / 100, GH / 100), dpi=100)
            fig_ref[0] = fig
            fig.patch.set_facecolor("#0D1B2A")
            ax.set_facecolor("#020617")
            ax.plot(x_vals, y_orig, color="white", lw=1.5, ls="--", label="Original  f(x)")
            ax.plot(x_vals, y_ser,  color=self._ORG, lw=2,   label=f"Fourier approx  N={N}")
            ax.axhline(0, color="#4A7AB5", lw=0.8)
            ax.axvline(0, color="#4A7AB5", lw=0.8)
            ax.set_title("Fourier Series Approximation", color="white", fontsize=11)
            ax.set_xlabel("x", color="white")
            ax.set_ylabel("f(x)", color="white")
            ax.tick_params(colors="white")
            ax.grid(True, alpha=0.25, color="#4A7AB5")
            for spine in ax.spines.values():
                spine.set_color("#4A7AB5")
            leg = ax.legend(facecolor="#1B2A72", edgecolor="#4A7AB5", fontsize=9)
            for t in leg.get_texts():
                t.set_color("white")
            fig.tight_layout(pad=0.5)

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception:
            tk.Label(graph_frame, text="Graph unavailable",
                     bg="#0D1B2A", fg=WHITE,
                     font=("OPTIVagRound-Bold", 14)).pack(expand=True)

        def _on_close():
            if fig_ref[0] is not None:
                plt.close(fig_ref[0])   # free matplotlib memory when the popup closes
            m.destroy()

        # ── Coefficients panel (right column) ─────────────────────────────────
        CW = MW - GW - 54
        coef_frame = tk.Frame(m, bg=CARD, width=CW, height=GH)
        coef_frame.place(x=GW + 36, y=62)
        coef_frame.pack_propagate(False)

        tk.Label(coef_frame, text="FOURIER COEFFICIENTS",
                 font=("OPTIVagRound-Bold", 13), bg="#1B4F8A", fg=WHITE
                 ).pack(fill="x")

        for lbl, val in [
            ("a₀  =",  sp.simplify(a0_sym)),
            ("aₙ  =",  sp.simplify(an_sym)),
            ("bₙ  =",  sp.simplify(bn_sym)),
        ]:
            row = tk.Frame(coef_frame, bg=CARD)
            row.pack(fill="x", padx=8, pady=5)
            tk.Label(row, text=lbl, font=("OPTIVagRound-Bold", 12),
                     bg=CARD, fg=NAVY, width=5, anchor="w").pack(side="left")
            tk.Label(row, text=str(val),
                     font=("Consolas", 11), bg="#D6EEFA", fg=NAVY,
                     anchor="nw", justify="left", wraplength=CW - 70,
                     padx=6, pady=4).pack(side="left", fill="x", expand=True)

        # ── Final series (full-width strip) ───────────────────────────────────
        bottom_y = 62 + GH + 8
        bottom_h = MH - bottom_y - 50
        series_frame = tk.Frame(m, bg=CARD)
        series_frame.place(x=18, y=bottom_y, width=MW - 36, height=bottom_h)

        tk.Label(series_frame, text="FINAL FOURIER SERIES",
                 font=("OPTIVagRound-Bold", 13), bg="#1B4F8A", fg=WHITE
                 ).pack(fill="x")

        txt = tk.Text(series_frame, font=("Consolas", 12),
                      bg="#020617", fg=WHITE, relief="flat",
                      wrap="word", padx=8, pady=6)
        txt.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        txt.insert("1.0", "f(x)  ≈  " + str(series))
        txt.configure(state="disabled")

        # ── Close button ──────────────────────────────────────────────────────
        tk.Button(m, text="CLOSE", font=("OPTIVagRound-Bold", 14),
                  bg=RED, fg=WHITE, relief="flat",
                  activebackground=RED_DK,
                  command=_on_close, cursor="hand2").place(
            x=MW // 2 - 70, y=MH - 46, width=140, height=36)

        m.protocol("WM_DELETE_WINDOW", _on_close)  # also close figure when X is clicked


# ── Laplace Transform page ────────────────────────────────────────────────────
class LaplacePage(Page):
    _PINK   = "#EC4899"
    _PINKDK = "#A01060"

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._draw()

    def _draw(self):
        cv = self.cv
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        help_rows = [
            ("Input:", "Enter f(t) using t, exp(), sin(), cos(), u(t), delta(t)."),
            ("How to use:", "Press CALCULATE or Enter."),
            ("Result:", "Shows F(s) Laplace transform."),
            ("Hotkeys:", "Enter = Calculate"),
        ]
        self._topbar(cv, "topics", lambda: self._show_how_to_use(help_rows))
        otxt(cv, W//2, 148, "LAPLACE TRANSFORM",
             ("OPTIVagRound-Bold", 48), fill=WHITE, ol=NAVY, ow=4)

        cx = W // 2
        cw = 880
        x1, x2 = cx - cw//2, cx + cw//2

        rr(cv, x1, 190, x2, 360, r=30, fill=CARD, outline="")

        cv.create_text(x1+40, 230, anchor="w",
                       font=("OPTIVagRound-Bold", 15), fill=NAVY,
                   text="Expression  (use t; supports u(t), delta(t)):")
        self.expr = tk.Entry(self, font=("OPTIVagRound-Bold", 18),
                             bg="#D6EEFA", fg=NAVY, relief="flat",
                             highlightthickness=2, highlightbackground=NAVY,
                             insertbackground=NAVY, justify="center")
        self.expr.insert(0, "delta(t) + 7*u(t) - 6*exp(-5*t)*u(t)")
        self.expr.place(x=x1+40, y=255, height=42, width=cw-80)
        self.expr.bind("<Return>", lambda e: self._calc())  # Enter key triggers calculation

        cbtn(cv, cx-130, 375, cx+130, 428, "CALCULATE",
             ("OPTIVagRound-Bold", 20), self._PINK, self._PINKDK, self._calc, r=24)

    def _calc(self):
        raw = self.expr.get().strip()
        if not raw:
            _show_modal(self._app, "LAPLACE", [],
                        error="⚠  Enter an expression", hdr_color=self._PINKDK)
            return
        try:
            t, s = sp.Symbol("t", positive=True), sp.Symbol("s")
            locs = {**_SAFE_LOCALS, 't': t, 's': s}  # extend the safe whitelist with the two transform variables
            preprocessed = _laplace_preprocess(raw)
            expr = _parse_symbolic(preprocessed, locs)
            result = sp.simplify(sp.laplace_transform(expr, t, s, noconds=True))
            expr_display = _laplace_clean_text(sp.simplify(expr))
            fs_display = _laplace_clean_text(sp.simplify(sp.apart(result, s)))
            rows = [
                ("f(t) =", expr_display),
                ("F(s) =", fs_display),
            ]
            _show_modal(self._app, "LAPLACE TRANSFORM", rows, hdr_color=self._PINKDK)
        except Exception as e:
            _show_modal(self._app, "LAPLACE", [],
                        error=f"⚠  {e}", hdr_color=self._PINKDK)  # catches unsupported transforms or parse errors


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":  # only run when this file is executed directly (not when imported)
    App().mainloop()         # create the App window and start the Tkinter event loop
