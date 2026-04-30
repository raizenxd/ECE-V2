import tkinter as tk          # GUI framework for all windows, canvases, and widgets
from tkinter import ttk       # styled widgets like Combobox (dropdown)
import cmath                  # complex math functions: phase angle, polar form
import math                   # standard math: degrees conversion, cos, sin
import re as _re              # regular expressions used to clean up user input strings
import numpy as np            # numerical matrix operations for Linear Algebra
import sympy as sp            # symbolic math engine for integration, Laplace, simplification

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
}

def _normalize(raw):
    """Normalize a user math string to SymPy-compatible syntax.

    Handles:
      * ^ -> **          (MATLAB/calculator exponent)
      * × -> *  ÷ -> /  (unicode operators)
      * bare i or j  ->  I  (imaginary unit, skips pi/sin/etc.)
      * implicit mult: 2I -> 2*I,  3pi -> 3*pi
    """
    s = raw.strip()
    s = s.replace('\u00d7', '*').replace('\u00f7', '/').replace('^', '**')
    # Replace standalone imaginary i/j not inside a word  (e.g. j not in 'pi','sin')
    s = _re.sub(r'(?<![A-Za-z_])j(?![A-Za-z_0-9])', 'I', s)
    s = _re.sub(r'(?<![A-Za-z_])i(?![A-Za-z_0-9])', 'I', s)
    # Implicit multiplication: digit directly before I or pi or e
    s = _re.sub(r'(\d)(I\b)',  r'\1*\2', s)
    s = _re.sub(r'(\d)(pi\b)', r'\1*\2', s)
    s = _re.sub(r'(?<=[\d\)])(pi|e|I)\b', r'*\1', s)
    return s

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

    def _topbar(self, cv, back="home"):
        cbtn(cv, 30, 18, 180, 68, "BACK",
             ("OPTIVagRound-Bold", 20), RED, RED_DK, lambda: self.go(back), r=18)  # BACK navigates to the previous page
        otxt(cv, W//2, 44, "ECETHON",
             ("OPTIVagRound-Bold", 26), fill=GREEN, ol=NAVY, ow=2)  # centered app name label
        cbtn(cv, W-180, 18, W-30, 68, "HOME",
             ("OPTIVagRound-Bold", 20), YELLOW, YEL_DK, lambda: self.go("home"), r=18)  # HOME always goes to the landing screen

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

        card_w, gap = 235, 38
        total = len(self._TOPICS) * card_w + (len(self._TOPICS) - 1) * gap
        sx = (W - total) // 2   # starting x so all cards are centered horizontally
        y1, y2 = 225, 450       # top and bottom y coordinates for every card

        for i, (label, dest, color, dark) in enumerate(self._TOPICS):
            x1 = sx + i * (card_w + gap)  # left edge of this card
            x2 = x1 + card_w
            rr(cv, x1+5, y1+5, x2+5, y2+5, r=24, fill=dark, outline="")  # drop shadow
            b = rr(cv, x1, y1, x2, y2, r=24, fill=color, outline="")      # card face
            t = cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text=label, font=("OPTIVagRound-Bold", 22),
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
        self._topbar(cv, "topics")

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
    MW, MH = 580, 120 + (len(rows) * 46 if rows else 100) + 80  # height grows automatically with the number of result rows
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
        lx, vx = 44, 260
        for idx, (label, value) in enumerate(rows):
            y = 108 + idx * 46
            cv.create_text(lx, y, anchor="w", font=("OPTIVagRound-Bold", 15),
                           fill=NAVY, text=label)
            cv.create_text(vx, y, anchor="w", font=("OPTIVagRound-Bold", 15),
                           fill=NAVY, text=value)
            if idx < len(rows) - 1:
                cv.create_line(40, y+22, MW-40, y+22, fill="#90C8E8", width=1)
    cbtn(cv, MW//2-80, MH-58, MW//2+80, MH-12, "CLOSE",
         ("OPTIVagRound-Bold", 16), RED, RED_DK, m.destroy, r=18)


# ── Linear Algebra page ───────────────────────────────────────────────────────
class LinearPage(Page):
    _PURPLE = "#8B5CF6"
    _PRPDK  = "#5B2CC0"
    _MAX    = 5
    _CELL_W = 88
    _CELL_H = 44
    _PAD    = 5

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._cellsA: list[list[tk.Entry]] = []
        self._cellsB: list[list[tk.Entry]] = []
        self._grid_frame_A = tk.Frame(self, bg="#3A6FA8")
        self._grid_frame_B = tk.Frame(self, bg="#3A6FA8")
        self._op_lbl_id = None
        self._draw_static()
        self._build_grids()

    # ── static chrome ─────────────────────────────────────────────────────────
    def _draw_static(self):
        cv = self.cv
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        self._topbar(cv, "topics")

        # title
        otxt(cv, W//2, 105, "LINEAR ALGEBRA",
             ("OPTIVagRound-Bold", 46), fill=WHITE, ol=NAVY, ow=4)

        # ── control bar card ──────────────────────────────────────────────────
        rr(cv, 30, 128, W-30, 192, r=20, fill="#1B4F8A", outline="")

        # Operation label + combobox
        cv.create_text(52, 160, anchor="w",
                       font=("OPTIVagRound-Bold", 13), fill=WHITE, text="Operation:")
        ops = ["Addition (A+B)", "Subtraction (A-B)",
               "Multiplication (A×B)", "Division (A×B⁻¹)"]
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
        cv.create_text(W//2, 706, font=("OPTIVagRound-Bold", 11),
                       fill=WHITE, text="Supports complex numbers  e.g.  3+4j  or  2-1j")

        # CALCULATE button (fixed, always on top)
        cbtn(cv, W//2-140, 636, W//2+140, 686, "CALCULATE",
             ("OPTIVagRound-Bold", 20), self._PURPLE, self._PRPDK, self._calc, r=26)

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

    # ── grid builder ──────────────────────────────────────────────────────────
    def _build_grids(self, *_):
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
        op = self.op_var.get()
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

    # ── calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        op = self.op_var.get()
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

        try:
            if op == "Addition (A+B)":
                C, title = A + B, "A + B"              # element-wise addition
            elif op == "Subtraction (A-B)":
                C, title = A - B, "A − B"              # element-wise subtraction
            elif op == "Multiplication (A×B)":
                C, title = A @ B, "A × B"              # true matrix multiplication (dot product)
            elif op == "Division (A×B⁻¹)":
                C, title = A @ np.linalg.inv(B), "A × B⁻¹"  # A divided by B = A multiplied by the inverse of B
            else:
                return
            result_rows = [(f"Row {i+1}:", "  ".join(fmt(v) for v in r))  # format each row of the result matrix
                           for i, r in enumerate(C)]
            _show_modal(self._app, title, result_rows, hdr_color=self._PRPDK)
        except Exception as e:
            _show_modal(self._app, "LINEAR ALGEBRA", [],
                        error=f"⚠  {e}", hdr_color=self._PRPDK)  # catches shape mismatch, singular matrix, etc.


# ── Fourier Series page ───────────────────────────────────────────────────────
class FourierPage(Page):
    _ORG   = "#F97316"
    _ORGDK = "#C05010"
    _MAX_PIECES = 6

    def __init__(self, app):
        super().__init__(app)
        self.cv = tk.Canvas(self, width=W, height=H,
                            bd=0, highlightthickness=0, bg=SKY)
        self.cv.place(x=0, y=0)
        self._pieces = []   # list of dicts: {frame, expr, x_from, x_to}
        self._draw_static()
        self._add_piece("0",   "-pi", "0")   # default piece 1: f(x)=0 on [-π, 0]
        self._add_piece("x",   "0",   "pi")  # default piece 2: f(x)=x on [0, π]

    # ── static chrome ─────────────────────────────────────────────────────────
    def _draw_static(self):
        cv = self.cv
        cv.create_rectangle(0, 0, W, H, fill=SKY, outline="")
        self._purplebar(cv)
        self._topbar(cv, "topics")
        otxt(cv, W//2, 105, "FOURIER SERIES",
             ("OPTIVagRound-Bold", 46), fill=WHITE, ol=NAVY, ow=4)

        # Main input card
        rr(cv, 30, 128, W-30, 598, r=24, fill=CARD, outline="")

        # Column header labels
        cv.create_text(90,  153, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="#")
        cv.create_text(390, 153, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="f(x)  Expression  (use x, sin, cos, pi, abs, …)")
        cv.create_text(730, 153, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="From  x =")
        cv.create_text(910, 153, anchor="center",
                       font=("OPTIVagRound-Bold", 12), fill=NAVY, text="To  x =")
        cv.create_line(50, 166, W-50, 166, fill="#4A7AB5", width=1)

        # Piece row container (frame packed into canvas area)
        self._piece_container = tk.Frame(self, bg=CARD)
        self._piece_container.place(x=50, y=172, width=W-100, height=270)

        # Add / Remove buttons
        cbtn(cv, 50,  454, 220, 492, "+ ADD PIECE",
             ("OPTIVagRound-Bold", 12), self._ORG, self._ORGDK,
             self._add_piece, r=14)
        cbtn(cv, 228, 454, 398, 492, "REMOVE LAST",
             ("OPTIVagRound-Bold", 12), "#DC2626", "#7F1D1D",
             self._remove_piece, r=14)

        # Harmonics N
        cv.create_text(460, 474, anchor="w",
                       font=("OPTIVagRound-Bold", 14), fill=NAVY, text="Harmonics  N :")
        self.nterms_var = tk.StringVar(value="5")
        tk.Spinbox(self, from_=1, to=20, textvariable=self.nterms_var,
                   width=3, font=("OPTIVagRound-Bold", 14),
                   bg="#D6EEFA", fg=NAVY, relief="flat",
                   highlightthickness=1, highlightbackground=NAVY,
                   justify="center").place(x=616, y=456, height=36)

        # Period T
        cv.create_text(678, 474, anchor="w",
                       font=("OPTIVagRound-Bold", 14), fill=NAVY,
                       text="Period  T  (blank = auto) :")
        self.period_entry = tk.Entry(self, font=("OPTIVagRound-Bold", 14),
                                     bg="#D6EEFA", fg=NAVY, relief="flat",
                                     highlightthickness=1, highlightbackground=NAVY,
                                     insertbackground=NAVY, justify="center", width=10)
        self.period_entry.place(x=920, y=456, height=36)

        # Hint
        cv.create_text(W//2, 506,
                       font=("OPTIVagRound-Bold", 11), fill=NAVY,
                       text="Tip: use  pi  for π,  sin(x),  cos(x),  x**2,  abs(x), etc.")

        # CALCULATE button
        cbtn(cv, W//2-165, 516, W//2+165, 576, "CALCULATE",
             ("OPTIVagRound-Bold", 22), self._ORG, self._ORGDK, self._calc, r=28)

    # ── piece row management ──────────────────────────────────────────────────
    def _add_piece(self, default_expr="0", x_from="0", x_to="1"):
        if len(self._pieces) >= self._MAX_PIECES:
            return  # silently do nothing if the maximum number of pieces is already reached
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
                              "from": from_var, "to": to_var})  # store the StringVars so _calc() can read the values later

    def _remove_piece(self):
        if len(self._pieces) <= 1:
            return  # always keep at least one piece so there is something to compute
        p = self._pieces.pop()    # remove the last piece from the list
        p["frame"].destroy()      # destroy its widget row so it disappears from the UI

    # ── calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        if not self._pieces:
            return
        try:
            N = int(self.nterms_var.get())
        except Exception:
            N = 5

        x_sym = sp.Symbol("x")  # symbolic variable used in all SymPy expressions
        pieces_data = []          # will hold (sympy_expr, x_start_float, x_end_float) for graph/plot
        pieces_sym  = []          # will hold (sympy_expr, x_start_sym,   x_end_sym)   for exact coefficients
        x_min_all = None
        x_max_all = None

        for p in self._pieces:
            raw = _normalize(p["expr"].get().strip())  # normalize the function expression
            try:
                xa_sym = sp.sympify(_normalize(p["from"].get().strip()), locals=_SAFE_LOCALS)
                xb_sym = sp.sympify(_normalize(p["to"].get().strip()),   locals=_SAFE_LOCALS)
                xa = float(xa_sym)  # evaluate start of interval as float (for graph)
                xb = float(xb_sym)  # evaluate end of interval as float (for graph)
                f_expr = sp.sympify(raw, locals=_SAFE_LOCALS)  # parse expression into a SymPy object
            except Exception as e:
                _show_modal(self._app, "FOURIER SERIES", [],
                            error=f"⚠  Parse error: {e}", hdr_color=self._ORGDK)
                return
            pieces_data.append((f_expr, xa, xb))
            pieces_sym.append((f_expr, xa_sym, xb_sym))
            if x_min_all is None or xa < x_min_all: x_min_all = xa  # track the overall minimum x
            if x_max_all is None or xb > x_max_all: x_max_all = xb  # track the overall maximum x

        # Period
        period_raw = self.period_entry.get().strip()
        if period_raw:
            try:
                T_sym = sp.sympify(period_raw)
                T = float(T_sym)  # use the manually entered period
            except Exception:
                _show_modal(self._app, "FOURIER SERIES", [],
                            error="⚠  Invalid period T", hdr_color=self._ORGDK)
                return
        else:
            T = x_max_all - x_min_all  # auto-detect period as the total span of all pieces
            T_sym = pieces_sym[-1][2] - pieces_sym[0][1]  # exact symbolic period

        L = T / 2  # half-period (float), used for graph and formula display
        L_sym = T_sym / 2  # half-period (symbolic), used for exact coefficient computation

        try:
            # a0 is the DC offset: (2/T) × integral of f(x) over one period
            a0_sym = sp.simplify(sp.Integer(2) / T_sym * sum(
                sp.integrate(f, (x_sym, xa_s, xb_s))
                for f, xa_s, xb_s in pieces_sym))
            a0 = float(a0_sym.evalf())
            an_list, bn_list = [], []
            an_sym_list, bn_sym_list = [], []
            for n in range(1, N + 1):
                # aₙ: cosine coefficient — (2/T) × integral of f(x)·cos(nπx/L), simplified
                an_s = sp.simplify(sp.Integer(2) / T_sym * sum(
                    sp.integrate(f * sp.cos(n * sp.pi * x_sym / L_sym), (x_sym, xa_s, xb_s))
                    for f, xa_s, xb_s in pieces_sym))
                # bₙ: sine coefficient — (2/T) × integral of f(x)·sin(nπx/L), simplified
                bn_s = sp.simplify(sp.Integer(2) / T_sym * sum(
                    sp.integrate(f * sp.sin(n * sp.pi * x_sym / L_sym), (x_sym, xa_s, xb_s))
                    for f, xa_s, xb_s in pieces_sym))
                an_list.append(float(an_s.evalf()))
                bn_list.append(float(bn_s.evalf()))
                an_sym_list.append(an_s)
                bn_sym_list.append(bn_s)
        except Exception as e:
            _show_modal(self._app, "FOURIER SERIES", [],
                        error=f"⚠  Integration error: {e}", hdr_color=self._ORGDK)
            return

        # Build formula string — only include terms where the coefficient is non-negligible (> 1e-10)
        formula = f"f(x) ≈ {a0/2:.4g}"
        for n in range(1, N + 1):
            an, bn = an_list[n-1], bn_list[n-1]
            if abs(an) > 1e-10:  # skip near-zero cosine terms to keep the formula clean
                sign = "+" if an >= 0 else "−"
                formula += f"  {sign}  {abs(an):.4g}·cos({n}πx/{L:.4g})"
            if abs(bn) > 1e-10:  # skip near-zero sine terms
                sign = "+" if bn >= 0 else "−"
                formula += f"  {sign}  {abs(bn):.4g}·sin({n}πx/{L:.4g})"

        self._show_result(T, L, a0, a0_sym, an_list, bn_list, an_sym_list, bn_sym_list,
                          formula, pieces_data, N, x_sym)

    # ── result modal ──────────────────────────────────────────────────────────
    def _show_result(self, T, L, a0, a0_sym, an_list, bn_list, an_sym_list, bn_sym_list,
                     formula, pieces_data, N, x_sym):
        def f_piecewise(xv):
            # evaluate the original piecewise function at a single point xv
            for expr, xa, xb in pieces_data:
                if xa - 1e-9 <= xv <= xb + 1e-9:  # small tolerance avoids boundary gaps
                    try:
                        return float(expr.subs(x_sym, xv))
                    except Exception:
                        return 0.0
            # if xv is outside all pieces, use the periodic extension to wrap it back into range
            x_min = pieces_data[0][1]
            shifted = ((xv - x_min) % T) + x_min  # shift xv into the first period
            for expr, xa, xb in pieces_data:
                if xa - 1e-9 <= shifted <= xb + 1e-9:
                    try:
                        return float(expr.subs(x_sym, shifted))
                    except Exception:
                        return 0.0
            return 0.0

        def f_fourier(xv):
            # evaluate the Fourier series approximation at a single point xv
            v = a0 / 2  # DC term
            for n, (an, bn) in enumerate(zip(an_list, bn_list), 1):
                v += an * math.cos(n * math.pi * xv / L)  # add the nth cosine term
                v += bn * math.sin(n * math.pi * xv / L)  # add the nth sine term
            return v

        MW, MH = 1140, 700
        m = tk.Toplevel()
        m.title("Fourier Series — Result")
        m.configure(bg=NAVY)
        m.resizable(False, False)
        sx = max(0, (m.winfo_screenwidth()  - MW) // 2)
        sy = max(0, (m.winfo_screenheight() - MH) // 2)
        m.geometry(f"{MW}x{MH}+{sx}+{sy}")

        # Header bar
        hcv = tk.Canvas(m, width=MW, height=56, bg=self._ORGDK,
                        bd=0, highlightthickness=0)
        hcv.place(x=0, y=0)
        hcv.create_text(MW//2, 28, text="FOURIER SERIES — RESULT",
                        font=("OPTIVagRound-Bold", 22), fill=WHITE)

        # ── Graph ─────────────────────────────────────────────────────────────
        GW, GH = MW - 40, 260
        gcv = tk.Canvas(m, width=GW, height=GH, bg="#0D1B2A",
                        bd=0, highlightthickness=1, highlightbackground="#4A7AB5")
        gcv.place(x=20, y=66)

        x_min = pieces_data[0][1]
        x_max = pieces_data[-1][2]
        span  = x_max - x_min
        x_p0  = x_min - span * 0.15  # extend the plot 15% beyond the left boundary
        x_p1  = x_max + span * 0.15  # extend the plot 15% beyond the right boundary
        STEPS = 700  # number of sample points — higher = smoother curve
        xs = [x_p0 + i * (x_p1 - x_p0) / STEPS for i in range(STEPS + 1)]  # evenly spaced x values

        try:
            ys_o = [f_piecewise(v) for v in xs]
            ys_f = [f_fourier(v)   for v in xs]
        except Exception:
            ys_o = ys_f = [0.0] * len(xs)

        y_lo = min(ys_o + ys_f); y_hi = max(ys_o + ys_f)
        if abs(y_hi - y_lo) < 1e-10: y_lo -= 1; y_hi += 1  # prevent zero-height graph for flat functions
        pad = (y_hi - y_lo) * 0.12
        y_lo -= pad; y_hi += pad  # add vertical padding so curves don't touch the graph edges

        MG = 46  # margin in pixels around the graph area for axis labels
        pw = GW - 2*MG; ph = GH - 2*MG  # plot width and height inside the margins

        def tx(v): return MG + (v - x_p0) / (x_p1 - x_p0) * pw   # map a math x-value to a canvas pixel x
        def ty(v): return MG + (1 - (v - y_lo) / (y_hi - y_lo)) * ph  # map a math y-value to a canvas pixel y (inverted)

        # grid
        for i in range(5):
            yg = y_lo + i*(y_hi-y_lo)/4
            gy = ty(yg)
            gcv.create_line(MG, gy, MG+pw, gy, fill="#1E3A5F", width=1)
            gcv.create_text(MG-4, gy, anchor="e",
                            text=f"{yg:.2g}", font=("Helvetica", 9), fill="#7EB8D8")
        for i in range(6):
            xg = x_p0 + i*(x_p1-x_p0)/5
            gx = tx(xg)
            gcv.create_line(gx, MG, gx, MG+ph, fill="#1E3A5F", width=1)
            gcv.create_text(gx, MG+ph+5, anchor="n",
                            text=f"{xg:.2g}", font=("Helvetica", 9), fill="#7EB8D8")
        if y_lo <= 0 <= y_hi:
            gcv.create_line(MG, ty(0), MG+pw, ty(0), fill="#4A7AB5", width=1)
        if x_p0 <= 0 <= x_p1:
            gcv.create_line(tx(0), MG, tx(0), MG+ph, fill="#4A7AB5", width=1)

        # original (white dashed) — the true piecewise function for reference
        pts_o = [c for i in range(len(xs)) for c in (tx(xs[i]), ty(ys_o[i]))]  # flatten (x,y) pairs into a flat list for create_line
        gcv.create_line(*pts_o, fill="white", width=1, dash=(4,4), smooth=True)

        # fourier (orange) — the Fourier approximation with N harmonic terms
        pts_f = [c for i in range(len(xs)) for c in (tx(xs[i]), ty(ys_f[i]))]
        gcv.create_line(*pts_f, fill=self._ORG, width=2, smooth=True)

        # legend
        gcv.create_line(GW-190, 18, GW-160, 18, fill="white", width=1, dash=(4,4))
        gcv.create_text(GW-155, 18, anchor="w", text="Original f(x)",
                        font=("Helvetica", 10), fill="white")
        gcv.create_line(GW-190, 36, GW-160, 36, fill=self._ORG, width=2)
        gcv.create_text(GW-155, 36, anchor="w",
                        text=f"Fourier approx  (N={N})",
                        font=("Helvetica", 10), fill=self._ORG)

        # ── Info area ─────────────────────────────────────────────────────────
        info = tk.Frame(m, bg=CARD)
        info.place(x=20, y=336, width=MW-40, height=316)

        # Period row
        a0_str      = str(a0_sym)
        a0_half_str = str(sp.simplify(a0_sym / 2))
        tk.Label(info, text=f"Period  T = {T:.6g}  |  L = T/2 = {L:.6g}  |  a₀ = {a0_str}  →  a₀/2 = {a0_half_str}",
                 font=("OPTIVagRound-Bold", 13), bg=CARD, fg=NAVY,
                 anchor="w").pack(fill="x", padx=14, pady=(10, 4))

        # Coefficient table  (scrollable if many terms)
        tbl_frame = tk.Frame(info, bg=CARD)
        tbl_frame.pack(fill="x", padx=14, pady=4)

        hdrs = [("n", 4), ("aₙ", 18), ("bₙ", 18)]
        for col, (h, w) in enumerate(hdrs):
            tk.Label(tbl_frame, text=h, font=("OPTIVagRound-Bold", 12),
                     bg="#1B4F8A", fg=WHITE, width=w,
                     relief="flat").grid(row=0, column=col, padx=2, pady=1, sticky="ew")

        show_n = min(N, 8)  # cap the visible table at 8 rows to avoid overcrowding the UI
        for n in range(1, show_n + 1):
            bg = CARD if n % 2 == 0 else "#D6EEFA"  # alternate row colors for readability
            tk.Label(tbl_frame, text=str(n), font=("OPTIVagRound-Bold", 11),
                     bg=bg, fg=NAVY, width=4,
                     relief="flat").grid(row=n, column=0, padx=2, pady=1)
            an_str = str(an_sym_list[n-1]) if n-1 < len(an_sym_list) else f"{an_list[n-1]:.6g}"
            bn_str = str(bn_sym_list[n-1]) if n-1 < len(bn_sym_list) else f"{bn_list[n-1]:.6g}"
            tk.Label(tbl_frame, text=an_str, font=("OPTIVagRound-Bold", 11),
                     bg=bg, fg=NAVY, width=18,
                     relief="flat").grid(row=n, column=1, padx=2, pady=1)
            tk.Label(tbl_frame, text=bn_str, font=("OPTIVagRound-Bold", 11),
                     bg=bg, fg=NAVY, width=18,
                     relief="flat").grid(row=n, column=2, padx=2, pady=1)
        if N > 8:
            tk.Label(tbl_frame, text=f"… and {N-8} more terms",
                     font=("OPTIVagRound-Bold", 11), bg=CARD, fg=NAVY,
                     anchor="w").grid(row=show_n+1, column=0, columnspan=3,
                                      padx=4, pady=2, sticky="w")

        # General formula
        tk.Label(info, text="General Formula:",
                 font=("OPTIVagRound-Bold", 13), bg=CARD, fg=NAVY,
                 anchor="w").pack(fill="x", padx=14, pady=(8, 0))
        tk.Label(info, text=formula, wraplength=MW-80,
                 font=("OPTIVagRound-Bold", 11), bg="#D6EEFA", fg=NAVY,
                 relief="flat", justify="left",
                 padx=8, pady=6).pack(fill="x", padx=14, pady=(2, 8))

        # Close button
        tk.Button(m, text="CLOSE", font=("OPTIVagRound-Bold", 14),
                  bg=RED, fg=WHITE, relief="flat",
                  activebackground=RED_DK,
                  command=m.destroy, cursor="hand2").place(
            x=MW//2-70, y=MH-46, width=140, height=36)


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
        self._topbar(cv, "topics")
        otxt(cv, W//2, 148, "LAPLACE TRANSFORM",
             ("OPTIVagRound-Bold", 48), fill=WHITE, ol=NAVY, ow=4)

        cx = W // 2
        cw = 880
        x1, x2 = cx - cw//2, cx + cw//2

        rr(cv, x1, 190, x2, 360, r=30, fill=CARD, outline="")

        ops = ["Laplace Transform", "Inverse Laplace"]
        self.op_var = tk.StringVar(value=ops[0])
        cb = ttk.Combobox(self, textvariable=self.op_var, values=ops,
                          font=("OPTIVagRound-Bold", 16), state="readonly", width=22)
        cb.place(x=x1+40, y=215, height=40)

        cv.create_text(x1+40, 280, anchor="w",
                       font=("OPTIVagRound-Bold", 15), fill=NAVY,
                       text="Expression  (use  t  for Laplace,  s  for Inverse):")
        self.expr = tk.Entry(self, font=("OPTIVagRound-Bold", 18),
                             bg="#D6EEFA", fg=NAVY, relief="flat",
                             highlightthickness=2, highlightbackground=NAVY,
                             insertbackground=NAVY, justify="center")
        self.expr.insert(0, "exp(-t)")  # pre-fill with a common example so the user can run it immediately
        self.expr.place(x=x1+40, y=305, height=42, width=cw-80)
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
            t, s = sp.Symbol("t", positive=True), sp.Symbol("s")  # t is the time variable, s is the complex frequency variable
            op   = self.op_var.get()
            locs = {**_SAFE_LOCALS, 't': t, 's': s}  # extend the safe whitelist with the two transform variables
            expr = sp.sympify(_normalize(raw), locals=locs)  # parse the user expression into a SymPy expression
            if op == "Laplace Transform":
                result = sp.laplace_transform(expr, t, s, noconds=True)  # compute F(s) from f(t); noconds=True suppresses convergence conditions
                rows = [
                    ("f(t):",  sp.pretty(expr,  use_unicode=True)),   # original time-domain expression
                    ("F(s):",  sp.pretty(result, use_unicode=True)),   # Laplace result in s-domain
                    ("F(s) simplified:", str(sp.simplify(result))),    # algebraically simplified form
                ]
            else:
                result = sp.inverse_laplace_transform(expr, s, t, noconds=True)  # compute f(t) from F(s)
                rows = [
                    ("F(s):",  sp.pretty(expr,   use_unicode=True)),   # original s-domain expression
                    ("f(t):",  sp.pretty(result,  use_unicode=True)),   # inverse Laplace result in time-domain
                    ("f(t) simplified:", str(sp.simplify(result))),     # algebraically simplified form
                ]
            _show_modal(self._app, op.upper(), rows, hdr_color=self._PINKDK)
        except Exception as e:
            _show_modal(self._app, "LAPLACE", [],
                        error=f"⚠  {e}", hdr_color=self._PINKDK)  # catches unsupported transforms or parse errors


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":  # only run when this file is executed directly (not when imported)
    App().mainloop()         # create the App window and start the Tkinter event loop
