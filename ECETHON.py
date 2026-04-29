import tkinter as tk
from tkinter import ttk
import cmath
import math
import numpy as np
import sympy as sp

# ── Window dimensions ─────────────────────────────────────────────────────────
W, H = 1280, 720

# ── Color palette ─────────────────────────────────────────────────────────────
SKY    = "#29ABE2"
RAY    = "#55CCFF"
PURPLE = "#5C3E9E"
GREEN  = "#6DD820"
GRN_DK = "#3A8A00"
RED    = "#E84040"
RED_DK = "#A01010"
YELLOW = "#F5C518"
YEL_DK = "#B08800"
NAVY   = "#1B2A72"
WHITE  = "#FFFFFF"
CARD   = "#5ABDE8"


# ── Drawing helpers ───────────────────────────────────────────────────────────
def rr(cv, x1, y1, x2, y2, r=22, **kw):
    """Smooth rounded rectangle as a polygon."""
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
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx or dy:
                cv.create_text(x + dx, y + dy, text=text, font=font, fill=ol, **kw)
    return cv.create_text(x, y, text=text, font=font, fill=fill, **kw)


def cbtn(cv, x1, y1, x2, y2, label, font, color, dark, cmd, r=20):
    """Canvas button with drop-shadow, body, label — all bound to cmd."""
    rr(cv, x1+4, y1+4, x2+4, y2+4, r=r, fill=dark, outline="")
    b = rr(cv, x1, y1, x2, y2, r=r, fill=color, outline="")
    t = cv.create_text((x1+x2)//2, (y1+y2)//2, text=label, font=font, fill=WHITE)
    for tag in (b, t):
        cv.tag_bind(tag, "<Button-1>", lambda e, c=cmd: c())
    return b, t


# ── App shell ─────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECETHON")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)

        self._pages = {}
        for name, cls in [
            ("home",    HomePage),
            ("topics",  TopicsPage),
            ("complex", ComplexPage),
            ("linear",  LinearPage),
            ("fourier", FourierPage),
            ("laplace", LaplacePage),
        ]:
            p = cls(self)
            p.place(x=0, y=0, width=W, height=H)
            self._pages[name] = p

        self.go("home")

    def go(self, name):
        for p in self._pages.values():
            p.lower()
        self._pages[name].lift()


# ── Base page ─────────────────────────────────────────────────────────────────
class Page(tk.Frame):
    def __init__(self, app):
        super().__init__(app, width=W, height=H, bg=SKY)
        self._app = app

    def go(self, name):
        self._app.go(name)

    def _topbar(self, cv, back="home"):
        cbtn(cv, 30, 18, 180, 68, "BACK",
             ("OPTIVagRound-Bold", 20), RED, RED_DK, lambda: self.go(back), r=18)
        otxt(cv, W//2, 44, "ECETHON",
             ("OPTIVagRound-Bold", 26), fill=GREEN, ol=NAVY, ow=2)
        cbtn(cv, W-180, 18, W-30, 68, "HOME",
             ("OPTIVagRound-Bold", 20), YELLOW, YEL_DK, lambda: self.go("home"), r=18)

    @staticmethod
    def _purplebar(cv):
        cv.create_rectangle(0, H-70, W, H, fill=PURPLE, outline="")


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
        for ox, hw in [(0, 18), (110, 14), (-110, 14),
                       (225, 11), (-225, 11), (345, 9), (-345, 9)]:
            cv.create_polygon(
                cx+ox-hw,    0,
                cx+ox+hw,    0,
                cx+ox+hw*14, H*0.85,
                cx+ox-hw*14, H*0.85,
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
        w = tk.Toplevel(self)
        w.title(title)
        w.geometry("480x230")
        w.resizable(False, False)
        w.configure(bg=SKY)
        w.transient(self._app)
        w.grab_set()
        tk.Label(w, text=title, font=("OPTIVagRound-Bold", 26),
                 bg=SKY, fg=GREEN).pack(pady=(20, 6))
        tk.Label(w, text=body, font=("OPTIVagRound-Bold", 14),
                 bg=SKY, fg=WHITE, justify="center").pack()
        tk.Button(w, text="Close", font=("OPTIVagRound-Bold", 14),
                  bg=RED, fg=WHITE, relief="flat", padx=20, pady=6,
                  cursor="hand2", command=w.destroy).pack(pady=18)

    def _about(self):
        self._modal(
            "About ECETHON",
            "An interactive ECE mathematics tool.\n"
            "Topics: Complex Numbers, Linear Algebra,\n"
            "Fourier Series & Laplace Transforms.",
        )

    def _creator(self):
        self._modal(
            "Creator",
            "Developed by ECE Students\n"
            "Advanced Engineering Mathematics · 2026",
        )


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
        sx = (W - total) // 2
        y1, y2 = 225, 450

        for i, (label, dest, color, dark) in enumerate(self._TOPICS):
            x1 = sx + i * (card_w + gap)
            x2 = x1 + card_w
            rr(cv, x1+5, y1+5, x2+5, y2+5, r=24, fill=dark, outline="")
            b = rr(cv, x1, y1, x2, y2, r=24, fill=color, outline="")
            t = cv.create_text((x1+x2)//2, (y1+y2)//2,
                               text=label, font=("OPTIVagRound-Bold", 22),
                               fill=WHITE, justify="center")
            for tag in (b, t):
                cv.tag_bind(tag, "<Button-1>", lambda e, d=dest: self.go(d))


# ── Complex Numbers page ──────────────────────────────────────────────────────
import re as _re

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
                       text="Enter expression  (e.g.  (3+2j) + (11-7j)  or  (3+2j) * (1-4j))")

        self.expr = tk.Entry(self, width=52,
                             font=("OPTIVagRound-Bold", 20),
                             bg="#D6EEFA", fg=NAVY,
                             relief="flat", highlightthickness=2,
                             highlightbackground=NAVY,
                             insertbackground=NAVY,
                             justify="center")
        self.expr.place(x=x1+40, y=260, height=44, width=cw-80)
        self.expr.bind("<Return>", lambda e: self._calc())

        # ── Calculate button ──────────────────────────────────────────────────
        cbtn(cv, cx-130, 345, cx+130, 400, "CALCULATE",
             ("OPTIVagRound-Bold", 20), GREEN, GRN_DK, self._calc, r=24)

    # ── Calculation ───────────────────────────────────────────────────────────
    @staticmethod
    def _safe_eval(s):
        """Evaluate a complex arithmetic expression using a strict character whitelist."""
        s = s.strip().replace(" ", "").replace("i", "j").replace("I", "j")
        # Allow only digits, operators, parentheses, decimal point, and 'j'
        if not _re.fullmatch(r'[\d\+\-\*\/\(\)\.j]+', s):
            raise ValueError("Invalid characters in expression")
        return eval(s, {"__builtins__": {}}, {})  # noqa: S307

    def _calc(self):
        raw = self.expr.get()
        if not raw.strip():
            self._result_modal(error="⚠  Please enter an expression")
            return
        try:
            res = self._safe_eval(raw)
            if not isinstance(res, (int, float, complex)):
                raise ValueError
            res = complex(res)
        except ZeroDivisionError:
            self._result_modal(error="⚠  Division by zero")
            return
        except Exception:
            self._result_modal(error="⚠  Invalid expression\nExample: (3+2j) + (11-7j)")
            return

        r, i  = res.real, res.imag
        sign  = "+" if i >= 0 else "-"
        r_str = f"{r:g}{sign}{abs(i):g}j"
        mag   = abs(res)
        phase = math.degrees(cmath.phase(res))
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

        # Center over main window
        m.update_idletasks()
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
                ("Result:",         f"({r_str})"),
                ("Real part:",      f"{r}"),
                ("Imaginary part:", f"{i}"),
                ("Magnitude:",      f"{mag:.6f}"),
                ("Phase:",          f"{phase:.2f}\u00b0"),
            ]
            lx, vx = 55, 280
            for idx, (label, value) in enumerate(rows):
                y = 118 + idx * 46
                cv.create_text(lx, y, anchor="w",
                               font=("OPTIVagRound-Bold", 17), fill=NAVY, text=label)
                cv.create_text(vx, y, anchor="w",
                               font=("OPTIVagRound-Bold", 17), fill=NAVY, text=value)
                if idx < len(rows) - 1:
                    cv.create_line(50, y+23, MW-50, y+23,
                                   fill="#90C8E8", width=1)

        # Close button
        cbtn(cv, MW//2-80, MH-58, MW//2+80, MH-12, "CLOSE",
             ("OPTIVagRound-Bold", 17), RED, RED_DK, m.destroy, r=20)


# ── Shared result-modal mixin ────────────────────────────────────────────────
def _show_modal(app, title, rows, error=None, hdr_color=NAVY):
    MW, MH = 580, 120 + (len(rows) * 46 if rows else 100) + 80
    MH = max(MH, 300)
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
        self.op_var.trace_add("write", lambda *_: self._build_grids())

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
        sb = tk.Spinbox(self, from_=1, to=self._MAX, textvariable=var,
                        width=2, font=("OPTIVagRound-Bold", 14),
                        bg="#D6EEFA", fg=NAVY, relief="flat",
                        highlightthickness=1, highlightbackground=NAVY,
                        justify="center", state="readonly",
                        command=self._build_grids)
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
                self.cv.delete(_id)
        ids = []
        rA = int(self.rA.get()); cA = int(self.cA.get())
        rB = int(self.rB.get()); cB = int(self.cB.get())
        gw_A = cA * (CW + P*2) + 20
        gw_B = cB * (CW + P*2) + 20
        A_LEFT  = 80
        B_RIGHT = W - 80
        B_LEFT  = B_RIGHT - gw_B
        B_LEFT  = max(B_LEFT, A_LEFT + gw_A + 120)  # at least 120px gap
        op_x    = (A_LEFT + gw_A + B_LEFT) // 2

        ids.append(self.cv.create_text(
            A_LEFT + 10, 204, anchor="w",
            font=("OPTIVagRound-Bold", 16), fill=NAVY, text="Matrix A"))
        ids.append(self.cv.create_text(
            B_LEFT + 10, 204, anchor="w",
            font=("OPTIVagRound-Bold", 16), fill=NAVY, text="Matrix B"))
        # operator symbol centred in the gap
        op = self.op_var.get()
        sym = {"Addition (A+B)": "+", "Subtraction (A-B)": "−",
               "Multiplication (A×B)": "×", "Division (A×B⁻¹)": "÷"}.get(op, "?")
        ids.append(self.cv.create_text(
            op_x, 370, font=("OPTIVagRound-Bold", 52), fill=NAVY, text=sym))
        self._op_lbl_id = ids

        TOP = 218

        # ── Matrix A ──────────────────────────────────────────────────────────
        self._grid_frame_A.destroy()
        self._grid_frame_A = tk.Frame(self, bg="#1B4F8A", padx=10, pady=10)
        self._cellsA = []
        for r in range(rA):
            row_e = []
            for c in range(cA):
                e = tk.Entry(self._grid_frame_A, **ef)
                e.insert(0, "0")
                e.grid(row=r, column=c, padx=P, pady=P, ipadx=3, ipady=5)
                row_e.append(e)
            self._cellsA.append(row_e)
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

    # ── read grids → numpy (supports complex) ─────────────────────────────────
    @staticmethod
    def _parse_cell(s):
        s = s.strip().replace(" ", "").replace("i", "j") or "0"
        return complex(s)

    def _read_grid(self, cells):
        arr = np.array([[self._parse_cell(cells[r][c].get())
                         for c in range(len(cells[r]))]
                        for r in range(len(cells))], dtype=complex)
        if not np.any(arr.imag):
            return arr.real
        return arr

    # ── calculation ───────────────────────────────────────────────────────────
    def _calc(self):
        op = self.op_var.get()
        try:
            A = self._read_grid(self._cellsA)
            B = self._read_grid(self._cellsB)
        except Exception:
            _show_modal(self._app, "LINEAR ALGEBRA", [],
                        error="⚠  Invalid value in a cell", hdr_color=self._PRPDK)
            return

        def fmt(v):
            v = complex(v)
            if v.imag == 0:
                return f"{v.real:.4g}"
            sign = "+" if v.imag >= 0 else "-"
            return f"{v.real:.4g}{sign}{abs(v.imag):.4g}j"

        try:
            if op == "Addition (A+B)":
                C, title = A + B, "A + B"
            elif op == "Subtraction (A-B)":
                C, title = A - B, "A − B"
            elif op == "Multiplication (A×B)":
                C, title = A @ B, "A × B"
            elif op == "Division (A×B⁻¹)":
                C, title = A @ np.linalg.inv(B), "A × B⁻¹"
            else:
                return
            result_rows = [(f"Row {i+1}:", "  ".join(fmt(v) for v in r))
                           for i, r in enumerate(C)]
            _show_modal(self._app, title, result_rows, hdr_color=self._PRPDK)
        except Exception as e:
            _show_modal(self._app, "LINEAR ALGEBRA", [],
                        error=f"⚠  {e}", hdr_color=self._PRPDK)


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
        self._add_piece("0",   "-pi", "0")
        self._add_piece("x",   "0",   "pi")

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
        try:
            N = int(self.nterms_var.get())
        except Exception:
            N = 5

        x_sym = sp.Symbol("x")
        pieces_data = []
        x_min_all = None
        x_max_all = None

        for p in self._pieces:
            raw = p["expr"].get().strip()
            try:
                xa = float(sp.sympify(p["from"].get().strip()))
                xb = float(sp.sympify(p["to"].get().strip()))
                f_expr = sp.sympify(raw)
            except Exception as e:
                _show_modal(self._app, "FOURIER SERIES", [],
                            error=f"⚠  Parse error: {e}", hdr_color=self._ORGDK)
                return
            pieces_data.append((f_expr, xa, xb))
            if x_min_all is None or xa < x_min_all: x_min_all = xa
            if x_max_all is None or xb > x_max_all: x_max_all = xb

        # Period
        period_raw = self.period_entry.get().strip()
        if period_raw:
            try:
                T = float(sp.sympify(period_raw))
            except Exception:
                _show_modal(self._app, "FOURIER SERIES", [],
                            error="⚠  Invalid period T", hdr_color=self._ORGDK)
                return
        else:
            T = x_max_all - x_min_all

        L = T / 2

        try:
            a0 = sum(float(sp.integrate(f, (x_sym, xa, xb)))
                     for f, xa, xb in pieces_data) * (2 / T)
            an_list, bn_list = [], []
            for n in range(1, N + 1):
                an = sum(float(sp.integrate(
                    f * sp.cos(n * sp.pi * x_sym / L), (x_sym, xa, xb)))
                    for f, xa, xb in pieces_data) * (2 / T)
                bn = sum(float(sp.integrate(
                    f * sp.sin(n * sp.pi * x_sym / L), (x_sym, xa, xb)))
                    for f, xa, xb in pieces_data) * (2 / T)
                an_list.append(an)
                bn_list.append(bn)
        except Exception as e:
            _show_modal(self._app, "FOURIER SERIES", [],
                        error=f"⚠  Integration error: {e}", hdr_color=self._ORGDK)
            return

        # Build formula string
        formula = f"f(x) ≈ {a0/2:.4g}"
        for n in range(1, N + 1):
            an, bn = an_list[n-1], bn_list[n-1]
            if abs(an) > 1e-10:
                sign = "+" if an >= 0 else "−"
                formula += f"  {sign}  {abs(an):.4g}·cos({n}πx/{L:.4g})"
            if abs(bn) > 1e-10:
                sign = "+" if bn >= 0 else "−"
                formula += f"  {sign}  {abs(bn):.4g}·sin({n}πx/{L:.4g})"

        self._show_result(T, L, a0, an_list, bn_list, formula,
                          pieces_data, N, x_sym)

    # ── result modal ──────────────────────────────────────────────────────────
    def _show_result(self, T, L, a0, an_list, bn_list, formula,
                     pieces_data, N, x_sym):
        def f_piecewise(xv):
            for expr, xa, xb in pieces_data:
                if xa - 1e-9 <= xv <= xb + 1e-9:
                    try:
                        return float(expr.subs(x_sym, xv))
                    except Exception:
                        return 0.0
            # periodic extension
            x_min = pieces_data[0][1]
            shifted = ((xv - x_min) % T) + x_min
            for expr, xa, xb in pieces_data:
                if xa - 1e-9 <= shifted <= xb + 1e-9:
                    try:
                        return float(expr.subs(x_sym, shifted))
                    except Exception:
                        return 0.0
            return 0.0

        def f_fourier(xv):
            v = a0 / 2
            for n, (an, bn) in enumerate(zip(an_list, bn_list), 1):
                v += an * math.cos(n * math.pi * xv / L)
                v += bn * math.sin(n * math.pi * xv / L)
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
        x_p0  = x_min - span * 0.15
        x_p1  = x_max + span * 0.15
        STEPS = 700
        xs = [x_p0 + i * (x_p1 - x_p0) / STEPS for i in range(STEPS + 1)]

        try:
            ys_o = [f_piecewise(v) for v in xs]
            ys_f = [f_fourier(v)   for v in xs]
        except Exception:
            ys_o = ys_f = [0.0] * len(xs)

        y_lo = min(ys_o + ys_f); y_hi = max(ys_o + ys_f)
        if abs(y_hi - y_lo) < 1e-10: y_lo -= 1; y_hi += 1
        pad = (y_hi - y_lo) * 0.12
        y_lo -= pad; y_hi += pad

        MG = 46
        pw = GW - 2*MG; ph = GH - 2*MG

        def tx(v): return MG + (v - x_p0) / (x_p1 - x_p0) * pw
        def ty(v): return MG + (1 - (v - y_lo) / (y_hi - y_lo)) * ph

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

        # original (white dashed)
        pts_o = [c for i in range(len(xs)) for c in (tx(xs[i]), ty(ys_o[i]))]
        gcv.create_line(*pts_o, fill="white", width=1, dash=(4,4), smooth=True)

        # fourier (orange)
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
        tk.Label(info, text=f"Period  T = {T:.6g}     |     L = T/2 = {L:.6g}     |     a₀ = {a0:.6g}     →     a₀/2 = {a0/2:.6g}",
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

        show_n = min(N, 8)
        for n in range(1, show_n + 1):
            bg = CARD if n % 2 == 0 else "#D6EEFA"
            tk.Label(tbl_frame, text=str(n), font=("OPTIVagRound-Bold", 11),
                     bg=bg, fg=NAVY, width=4,
                     relief="flat").grid(row=n, column=0, padx=2, pady=1)
            tk.Label(tbl_frame, text=f"{an_list[n-1]:.6g}", font=("OPTIVagRound-Bold", 11),
                     bg=bg, fg=NAVY, width=18,
                     relief="flat").grid(row=n, column=1, padx=2, pady=1)
            tk.Label(tbl_frame, text=f"{bn_list[n-1]:.6g}", font=("OPTIVagRound-Bold", 11),
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
        self.expr.insert(0, "exp(-t)")
        self.expr.place(x=x1+40, y=305, height=42, width=cw-80)
        self.expr.bind("<Return>", lambda e: self._calc())

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
            op   = self.op_var.get()
            expr = sp.sympify(raw)
            if op == "Laplace Transform":
                result = sp.laplace_transform(expr, t, s, noconds=True)
                rows = [
                    ("f(t):",  sp.pretty(expr,  use_unicode=True)),
                    ("F(s):",  sp.pretty(result, use_unicode=True)),
                    ("F(s) simplified:", str(sp.simplify(result))),
                ]
            else:
                result = sp.inverse_laplace_transform(expr, s, t, noconds=True)
                rows = [
                    ("F(s):",  sp.pretty(expr,   use_unicode=True)),
                    ("f(t):",  sp.pretty(result,  use_unicode=True)),
                    ("f(t) simplified:", str(sp.simplify(result))),
                ]
            _show_modal(self._app, op.upper(), rows, hdr_color=self._PINKDK)
        except Exception as e:
            _show_modal(self._app, "LAPLACE", [],
                        error=f"⚠  {e}", hdr_color=self._PINKDK)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()
