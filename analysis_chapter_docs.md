**Analysis**

The ECETHON program is a Python-based interactive computational tool built using the Tkinter graphical framework, designed to solve and visualize four core topics in Advanced Engineering Mathematics: Complex Numbers, Linear Algebra, Fourier Series, and Laplace Transforms. The system is architected as a single-window, multi-page application where all pages co-exist in memory at launch and are made visible or hidden by raising and lowering their stacking order through the canvas layer system. Understanding the program requires tracing not just what each module computes, but how every input string is intercepted, validated, normalized, symbolically evaluated, and finally rendered back to the user in a readable form.

---

**Imports and Global Configuration — Lines 1 to 22**

```python
 1  import tkinter as tk
 2  from tkinter import ttk
 3  import cmath
 4  import math
 5  import re as _re
 6  import numpy as np
 7  import sympy as sp
 8  from sympy.parsing.sympy_parser import (
 9      parse_expr,
10      standard_transformations,
11      implicit_multiplication_application,
12      implicit_application,
13  )
14  import matplotlib
15  matplotlib.use("TkAgg")
16  import matplotlib.pyplot as plt
17  from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
18
19  _PARSE_TRANSFORMS = standard_transformations + (
20      implicit_multiplication_application,
21      implicit_application,
22  )
```

**Line 1** — Imports Python's built-in GUI toolkit under the alias `tk`, making every Tkinter widget class, canvas method, and event system available through the shorter prefix throughout the entire program.

**Line 2** — Imports the themed widget submodule `ttk` separately because themed widgets such as `Combobox` are not part of the core `tk` namespace; they require their own import path.

**Line 3** — Imports `cmath`, Python's complex-number math module, which is used specifically to compute the phase angle of a complex result using `cmath.phase()`, since the standard `math` module does not support complex inputs.

**Line 4** — Imports Python's standard `math` module, used to convert the phase angle from radians to degrees via `math.degrees()` after the phase is computed by `cmath`.

**Line 5** — Imports the `re` regular expression module under the private alias `_re`. The underscore prefix signals that this name is internal and not intended to be referenced by outside code or users. It is used extensively inside `_normalize()` to find and replace patterns in user input strings.

**Line 6** — Imports NumPy under the alias `np`. NumPy provides the fast two-dimensional array type and linear algebra operations used by the Matrix module, including element-wise arithmetic, matrix multiplication via the `@` operator, and matrix inversion via `np.linalg.inv`.

**Line 7** — Imports SymPy under the alias `sp`. SymPy is the symbolic computation engine that powers all four mathematical modules: it performs exact integration for Fourier coefficients, symbolic Laplace and inverse Laplace transforms, linear system solving via `linsolve`, and expression simplification via `simplify` and `apart`.

**Lines 8–13** — Import four specific names from SymPy's expression parser. `parse_expr` is the main function that converts a Python string into a symbolic expression. `standard_transformations` is a baseline set of parsing rules. `implicit_multiplication_application` allows adjacent tokens like `2x` to be read as `2*x` automatically. `implicit_application` allows function names followed by arguments without parentheses, such as `sin x`, to be interpreted as a function call. These four are assembled in lines 19–22.

**Line 14** — Imports the Matplotlib library itself. This must be done as a separate step before the pyplot submodule is imported, because line 15 must change the rendering backend before pyplot initializes.

**Line 15** — Calls `matplotlib.use("TkAgg")` to force Matplotlib to use the TkAgg rendering backend, which draws figures inside Tkinter windows. This call must come before `import matplotlib.pyplot` is executed; if pyplot is imported first, the backend is already selected and this call has no effect.

**Line 16** — Imports the `pyplot` interface, which provides the `plt.subplots()` and `plt.close()` functions used to create and destroy the Fourier Series graph.

**Line 17** — Imports `FigureCanvasTkAgg`, the bridge class that embeds a Matplotlib figure as a Tkinter widget inside any Frame or Toplevel window. This is used exclusively by the Fourier Series result modal to display the approximation graph.

**Lines 19–22** — Build the tuple `_PARSE_TRANSFORMS` by concatenating the standard parsing rules with the two implicit-notation rules. This combined tuple is passed to every call to `parse_expr` throughout the program so that all modules benefit from shorthand input support uniformly.

---

**Unit Step Helper — Lines 24 to 27**

```python
24  def _unit_step(x):
25      # Use Heaviside(x, 1) so u(0)=1, matching common engineering convention.
26      return sp.Heaviside(x, 1)
```

**Line 24** — Defines a module-level helper function `_unit_step` that wraps SymPy's Heaviside function. This wrapper exists because SymPy's `Heaviside` by default leaves the value at zero undefined, whereas engineering convention defines `u(0) = 1`.

**Line 26** — Calls `sp.Heaviside(x, 1)`, passing the second argument `1` to set `Heaviside(0) = 1`. This function is registered in `_SAFE_LOCALS` under five aliases — `u`, `U`, `H`, `step`, and `heaviside` — so any of those names typed by the user maps to the same behavior.

---

**Safe Locals Whitelist — Lines 29 to 50**

```python
29  _SAFE_LOCALS = {
30      'pi': sp.pi, 'e': sp.E, 'E': sp.E, 'I': sp.I,
31      'inf': sp.oo, 'oo': sp.oo,
32      'sqrt': sp.sqrt, 'cbrt': lambda x: sp.Rational(1,3)**x,
33      'exp':  sp.exp,  'log': sp.log, 'ln': sp.log, 'log10': lambda x: sp.log(x, 10),
34      'sin':  sp.sin,  'cos': sp.cos,  'tan': sp.tan,
35      'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan, 'atan2': sp.atan2,
36      'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
37      'abs':  sp.Abs,  'Abs': sp.Abs,  'sign': sp.sign,
38      'floor': sp.floor, 'ceil': sp.ceiling,
39      're': sp.re, 'im': sp.im, 'arg': sp.arg, 'conj': sp.conjugate,
40      'u': _unit_step, 'U': _unit_step, 'H': _unit_step,
41      'step': _unit_step, 'heaviside': _unit_step,
42      'delta': sp.DiracDelta, 'dirac': sp.DiracDelta, 'impulse': sp.DiracDelta,
43      'DiracDelta': sp.DiracDelta, 'δ': sp.DiracDelta,
44  }
```

**Line 29** — Opens the `_SAFE_LOCALS` dictionary, which serves as the controlled namespace for expression evaluation. Only names explicitly listed here can be resolved during parsing; any other identifier in the user's input will cause a parse error rather than being silently executed.

**Line 30** — Maps mathematical constants: `pi` and `e`/`E` map to SymPy's exact symbolic values `sp.pi` and `sp.E`. The imaginary unit `I` maps to `sp.I`. These are symbolic objects, not floating-point approximations.

**Line 31** — Maps `inf` and `oo` to SymPy's symbolic infinity `sp.oo`, allowing users to write limits or unbounded expressions.

**Line 32** — Maps `sqrt` to SymPy's exact square root function. Maps `cbrt` (cube root) to a lambda that raises x to the power one-third using `sp.Rational(1,3)` for an exact symbolic exponent rather than the floating-point `0.333...`.

**Line 33** — Maps `exp`, `log`, `ln` (all to SymPy's natural logarithm), and `log10` (to a lambda that calls `sp.log(x, 10)` for the base-ten logarithm).

**Line 34** — Maps the three primary trigonometric functions to their SymPy symbolic counterparts, enabling exact evaluation such as `sin(pi/6) = 1/2`.

**Line 35** — Maps inverse trigonometric functions. `atan2` is included because it computes the four-quadrant inverse tangent needed for complex number phase calculations.

**Line 36** — Maps hyperbolic trigonometric functions, needed for Laplace pairs involving hyperbolic signals.

**Line 37** — Maps `abs` and `Abs` both to `sp.Abs` (symbolic absolute value) and `sign` to `sp.sign` (signum function). Mapping `abs` is important because Python's built-in `abs` is not in the SymPy namespace.

**Line 38** — Maps floor and ceiling functions. Note that SymPy uses `sp.ceiling`, not `sp.ceil`, so the alias corrects that naming difference transparently for the user.

**Line 39** — Maps complex number component extractors: `re` for real part, `im` for imaginary part, `arg` for principal argument (phase angle), and `conj` for complex conjugate.

**Lines 40–41** — Map five different aliases for the unit step signal all to `_unit_step`, ensuring that users can type `u(t)`, `U(t)`, `H(t)`, `step(t)`, or `heaviside(t)` interchangeably and always receive the same Heaviside-with-engineering-convention result.

**Lines 42–43** — Map four aliases for the Dirac delta impulse function to `sp.DiracDelta`. The Greek character δ is also mapped directly so users can paste or type the actual Unicode character. This is critical for the Laplace transform module because SymPy only recognizes `DiracDelta` by its exact class name during symbolic integration.

---

**The `_normalize` Function — Lines 51 to 86**

```python
51  def _normalize(raw):
52      s = raw.strip()
53      s = s.replace('\u00d7', '*').replace('\u00f7', '/').replace('^', '**')
54      s = s.replace('δ', 'delta')
55      s = _re.sub(r'(?<![A-Za-z_])j(?![A-Za-z_0-9])', 'I', s)
56      s = _re.sub(r'(?<![A-Za-z_])i(?![A-Za-z_0-9])', 'I', s)
57      s = _re.sub(r'(\d)(I\b)',  r'\1*\2', s)
58      s = _re.sub(r'(\d)(pi\b)', r'\1*\2', s)
59      s = _re.sub(r'(?<=[\d\)])(pi|e|I)\b', r'*\1', s)
60      s = _re.sub(
61          r'\b(sin|cos|tan|sinh|cosh|tanh)\s*([+-]?\d+(?:\.\d+)?)\s*\*?\s*t\b',
62          lambda m: f"{m.group(1)}({m.group(2)}*t)",
63          s,
64      )
65      s = _re.sub(
66          r'\b(sin|cos|tan|sinh|cosh|tanh)\s*t\b',
67          lambda m: f"{m.group(1)}(t)",
68          s,
69      )
70      s = _re.sub(r'\be\*\*-\s*t\b', 'exp(-t)', s)
71      s = _re.sub(r'\be\*\*-\s*([0-9]+(?:\.[0-9]+)?)\s*\*?\s*t\b', r'exp(-\1*t)', s)
72      return s
```

**Line 51** — Defines `_normalize`, the first-stage input processor called by every parsing function before any symbolic evaluation occurs.

**Line 52** — Strips leading and trailing whitespace from the raw string to prevent false parse errors from accidental spaces.

**Line 53** — Performs three simultaneous character substitutions: replaces the Unicode multiplication cross `×` with `*`, the Unicode division sign `÷` with `/`, and the common calculator exponent caret `^` with Python's `**` operator. All three are single-pass replacements.

**Line 54** — Replaces the Greek lowercase delta character δ with the ASCII word `delta` so that the symbol can later be resolved to `sp.DiracDelta` through `_SAFE_LOCALS`.

**Line 55** — Uses a negative lookbehind `(?<![A-Za-z_])` and negative lookahead `(?![A-Za-z_0-9])` to replace standalone `j` with `I`. The lookbehind ensures the `j` is not part of a longer word, and the lookahead ensures it is not followed by alphanumeric characters. This converts engineering imaginary notation `j` to SymPy's `I` without touching the letter `j` inside identifiers.

**Line 56** — Applies the same lookbehind–lookahead pattern to standalone `i`, converting it to `I`. This handles the mathematics convention of using lowercase `i` for the imaginary unit without altering characters inside words like `sin`, `pi`, `imag`, or `signal`.

**Line 57** — Inserts an explicit multiplication operator when a digit is directly followed by `I` (the imaginary unit). For example `3I` becomes `3*I`. The `\b` word boundary ensures only the capital `I` as an isolated token is matched.

**Line 58** — Inserts multiplication between a digit and the word `pi`. This converts `2pi` to `2*pi` automatically.

**Line 59** — Uses a positive lookbehind for a digit or closing parenthesis to insert multiplication before any of the three tokens `pi`, `e`, or `I`. This handles expressions like `(x+1)pi` or `2e` by inserting the implied multiplication operator that Python requires.

**Lines 60–64** — Matches trig shorthand where a function name like `cos` or `sin` is followed by an optional sign, a number, optional whitespace, and the variable `t`. The lambda replacement wraps the number and `t` in proper function-call notation. For example `cos2t` is rewritten to `cos(2*t)` and `sin-3t` to `sin(-3*t)`.

**Lines 65–69** — Handles the simpler case where a trig function name is followed directly by `t` with no coefficient, converting `sint` to `sin(t)` and `cosh t` to `cosh(t)`. This uses a separate pattern because the previous substitution only matches when a numeric coefficient is present.

**Line 70** — Converts the Laplace shorthand `e**-t` (produced by the earlier caret replacement) to `exp(-t)`, which is the unambiguous SymPy form for a decaying exponential.

**Line 71** — Handles the general case `e**-5t` or `e**-2.5t`, extracting the coefficient into capture group 1 and building `exp(-5*t)` or `exp(-2.5*t)`. The backreference `\1` in the replacement string inserts the captured coefficient.

**Line 72** — Returns the fully cleaned string, ready to be passed into SymPy's parser.

---

**The `_parse_symbolic` and `_parse_num` Functions — Lines 74 to 88**

```python
74  def _parse_symbolic(raw, locs):
75      return parse_expr(
76          _normalize(raw),
77          local_dict=locs,
78          transformations=_PARSE_TRANSFORMS,
79          evaluate=True,
80      )
81
82  def _parse_num(raw):
83      s = _normalize(raw) or '0'
84      val = sp.sympify(s, locals=_SAFE_LOCALS, evaluate=True)
85      return complex(val.evalf())
```

**Line 74** — Defines `_parse_symbolic`, the function that converts a cleaned string into a SymPy symbolic expression. It accepts both the raw string and a caller-supplied `locs` dictionary so each module can extend the base whitelist with its own variable symbols.

**Lines 75–80** — Calls `parse_expr` with four arguments: the normalized string, the local namespace dictionary, the combined transformation tuple from line 19, and `evaluate=True` to immediately simplify constant sub-expressions during parsing.

**Line 82** — Defines `_parse_num`, used when a concrete numerical result is needed rather than a symbolic expression. This is the parser used by the Complex Numbers calculator and each matrix cell reader.

**Line 83** — Normalizes the input string and falls back to the string `'0'` if the result is empty, preventing a parse error on blank input.

**Line 84** — Calls `sp.sympify` with the safe whitelist to parse the cleaned string into a SymPy expression. Unlike `parse_expr`, `sympify` is faster for purely numeric expressions because it does not apply the implicit-multiplication transformations.

**Line 85** — Calls `evalf()` to evaluate the symbolic expression to a high-precision floating-point value, then casts it to a Python `complex` object. This final cast is essential because NumPy matrix operations and Python's `cmath` functions require standard Python or NumPy numeric types, not SymPy number objects.

---

**The Laplace Preprocessor and Display Helpers — Lines 87 to 165**

```python
 87  def _laplace_preprocess(raw):
 88      expr_str = _normalize(raw).strip()
 89      expr_str = _re.sub(r'\bu\s*\(\s*t\s*\)', '1', expr_str)
 90      expr_str = _re.sub(r'\*\s*u\s*\(\s*t\s*\)', '', expr_str)
 91      expr_str = _re.sub(r'u\s*\(\s*t\s*\)\s*\*', '', expr_str)
 92      expr_str = _re.sub(r'\bdelta\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
 93      expr_str = _re.sub(r'\bimpulse\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
 94      expr_str = _re.sub(r'\bdirac\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
 95      expr_str = _re.sub(r'\bdelta\b', 'DiracDelta(t)', expr_str)
 96      expr_str = _re.sub(r'\bimpulse\b', 'DiracDelta(t)', expr_str)
 97      expr_str = _re.sub(r'\bdirac\b', 'DiracDelta(t)', expr_str)
 98      if not expr_str:
 99          expr_str = '0'
100      return expr_str

102  def _laplace_clean_text(text):
103      return (
104          str(text)
105          .replace("**", "^")
106          .replace("DiracDelta(t)", "delta(t)")
107          .replace("Heaviside(t, 1)", "u(t)")
108          .replace("Heaviside(t)", "u(t)")
109      )

111  def _laplace_format_parts(result, s_sym):
112      result = sp.simplify(sp.apart(result, s_sym))
113      terms = sp.Add.make_args(result)
114      parts = []
115      for term in terms:
116          numer, denom = sp.fraction(term)
117          numer = sp.expand(numer)
118          denom = sp.expand(denom)
119          if denom == 1:
120              parts.append(("whole", _laplace_clean_text(numer), None))
121          else:
122              parts.append(("frac", _laplace_clean_text(numer), _laplace_clean_text(denom)))
123      return parts

125  def _laplace_render_parts(parts):
126      lines_num, lines_bar, lines_den = [], [], []
127      pad = 3
128      for i, part in enumerate(parts):
129          sign = "   "
130          if i > 0:
131              raw = part[1]
132              sign = " - " if raw.startswith("-") else " + "
133          if part[0] == "whole":
134              val = part[1].lstrip("-") if (i > 0 and part[1].startswith("-")) else part[1]
135              width = len(sign) + len(val)
136              lines_num.append(sign + val)
137              lines_bar.append(" " * width)
138              lines_den.append(" " * width)
139          else:
140              n_str, d_str = part[1], part[2]
141              inner_w = max(len(n_str), len(d_str)) + pad
142              lines_num.append(sign + n_str.center(inner_w))
143              lines_bar.append(" " * len(sign) + ("─" * inner_w))
144              lines_den.append(" " * len(sign) + d_str.center(inner_w))
145      row1 = "".join(lines_num).rstrip()
146      row2 = "".join(lines_bar).rstrip()
147      row3 = "".join(lines_den).rstrip()
148      if row2.strip():
149          return f"{row1}\n{row2}\n{row3}"
150      return row1
```

**Line 87** — Defines `_laplace_preprocess`, a secondary normalization pass applied only before forward Laplace transforms. The standard `_normalize` handles general expression cleaning; this function handles Laplace-domain signal conventions.

**Line 88** — Runs the general `_normalize` first, then strips any remaining whitespace from the result.

**Line 89** — Replaces `u(t)` and its whitespace variants with the literal `1`. This is mathematically valid because the Laplace transform of `f(t)*u(t)` over the positive half-line is identical to the Laplace transform of `f(t)` alone, since the integration already starts at zero.

**Lines 90–91** — Remove the unit step when it appears multiplicatively: `f(t) * u(t)` has the `* u(t)` stripped, and `u(t) * f(t)` has the `u(t) *` stripped. This preserves the mathematical identity without requiring the parser to evaluate `Heaviside` during integration.

**Lines 92–94** — Replace three explicit impulse function call forms — `delta(t)`, `impulse(t)`, and `dirac(t)` — with `DiracDelta(t)`, the exact class name SymPy requires to correctly handle the impulse during Laplace integration.

**Lines 95–97** — Handle the bare-word aliases `delta`, `impulse`, and `dirac` without parentheses, in case the user typed just the word without calling it as a function. These are replaced with the fully parenthesized `DiracDelta(t)` form.

**Lines 98–99** — Guard against an empty string after all substitutions by defaulting to `'0'`, preventing a parse error if the user's expression collapses entirely to nothing after stripping.

**Line 102** — Defines `_laplace_clean_text`, which performs the reverse translation for display: it converts SymPy's internal Python-syntax representations back into human-readable form.

**Lines 104–108** — Chain four string replacements: `**` becomes `^`, `DiracDelta(t)` becomes `delta(t)`, and both forms of Heaviside become `u(t)`. This ensures the result shown to the user matches standard engineering textbook notation rather than Python or SymPy syntax.

**Line 111** — Defines `_laplace_format_parts`, which decomposes a rational s-domain expression for display in stacked fraction form.

**Line 112** — Applies `sp.apart` for partial fraction decomposition relative to the variable `s_sym`, then simplifies. This converts a complex rational expression like `(s+7)/(s^2+5s)` into a sum of simpler fractions, each corresponding to a standard Laplace table entry.

**Line 113** — Calls `sp.Add.make_args` to extract the list of individual additive terms. If the expression is not a sum, this returns a single-element tuple containing the whole expression, making the loop on line 115 handle both cases uniformly.

**Lines 115–122** — Iterate over each term, extract numerator and denominator using `sp.fraction`, expand both to their polynomial forms, and classify each term as either `"whole"` (denominator equals 1) or `"frac"` (has a denominator). Both forms are converted to display strings via `_laplace_clean_text` before being stored.

**Line 125** — Defines `_laplace_render_parts`, which arranges the classified terms into three parallel string rows that simulate stacked typeset fractions in plain text.

**Line 126** — Initializes three lists to accumulate the top row (numerators), middle row (fraction bars), and bottom row (denominators) independently before joining them.

**Line 127** — Sets a padding constant of 3 characters added to both sides of each fraction's inner column width to prevent numerators and denominators from visually touching the fraction bar edges.

**Lines 128–132** — For each term, the sign prefix defaults to three spaces for the first term. For subsequent terms, it reads whether the numerator string starts with a minus sign and selects either ` - ` or ` + ` accordingly. This ensures the assembled expression reads correctly as an algebraic sum.

**Lines 133–138** — For whole-number terms: strips the leading minus sign from the displayed value if the sign has already been captured in the prefix, computes the column width, and appends the value to the numerator row with matching blank strings to the bar and denominator rows so column alignment is preserved.

**Lines 139–144** — For fraction terms: determines the inner column width as the maximum of the numerator and denominator string lengths plus the padding constant. Centers both strings within that width, appends them to their respective rows, and fills the bar row with the Unicode box-drawing horizontal character `─` repeated to the same width.

**Lines 145–150** — Joins each row's list into a single string, strips trailing whitespace, then checks if the bar row contains any non-space characters. If it does, the three rows are joined with newlines to form a visually stacked fraction. If no fraction bars exist (all terms were whole numbers), only the numerator row is returned.

---

**Window Dimensions, Color Palette, and Drawing Helpers — Lines 152 to 240**

```python
152  W, H = 1280, 720

153  SKY    = "#29ABE2"
154  RAY    = "#55CCFF"
155  PURPLE = "#5C3E9E"
156  GREEN  = "#6DD820"
157  GRN_DK = "#3A8A00"
158  RED    = "#E84040"
159  RED_DK = "#A01010"
160  YELLOW = "#F5C518"
161  YEL_DK = "#B08800"
162  NAVY   = "#1B2A72"
163  WHITE  = "#FFFFFF"
164  CARD   = "#5ABDE8"

166  def rr(cv, x1, y1, x2, y2, r=22, **kw):
167      p = [
168          x1+r, y1,  x2-r, y1,
169          x2,   y1,  x2,   y1+r,
170          x2,   y2-r, x2,  y2,
171          x2-r, y2,  x1+r, y2,
172          x1,   y2,  x1,   y2-r,
173          x1,   y1+r, x1,  y1,
174          x1+r, y1,
175      ]
176      return cv.create_polygon(p, smooth=True, **kw)

178  def otxt(cv, x, y, text, font, fill=WHITE, ol=NAVY, ow=3, **kw):
179      for dx in range(-ow, ow + 1):
180          for dy in range(-ow, ow + 1):
181              if dx or dy:
182                  cv.create_text(x + dx, y + dy, text=text, font=font, fill=ol, **kw)
183      return cv.create_text(x, y, text=text, font=font, fill=fill, **kw)

185  def cbtn(cv, x1, y1, x2, y2, label, font, color, dark, cmd, r=20):
186      rr(cv, x1+4, y1+4, x2+4, y2+4, r=r, fill=dark, outline="")
187      b = rr(cv, x1, y1, x2, y2, r=r, fill=color, outline="")
188      t = cv.create_text((x1+x2)//2, (y1+y2)//2, text=label, font=font, fill=WHITE)
189      for tag in (b, t):
190          cv.tag_bind(tag, "<Button-1>", lambda e, c=cmd: c())
191      return b, t
```

**Line 152** — Defines the fixed window dimensions as two module-level constants. Every coordinate calculation, canvas placement, and widget sizing throughout the program uses `W` and `H` as references, meaning the entire layout can be rescaled by changing these two values.

**Lines 153–164** — Define twelve named color constants as hex strings. Centralizing colors here means the entire visual theme can be modified in one place without searching through drawing code. Each constant is named for its semantic role rather than its literal color, for example `CARD` describes the card panel background, `GRN_DK` is the drop-shadow variant of `GREEN`.

**Line 166** — Defines `rr`, the rounded rectangle drawing function. It takes the four corner coordinates and a corner radius `r`, then constructs a flat list of polygon points.

**Lines 167–175** — Build the point list `p` so that each corner is represented by three sequential points: one point on each adjacent edge and one at the actual corner. Tkinter's `smooth=True` option on `create_polygon` interprets this as a Bézier spline, rounding each corner to the specified radius.

**Line 176** — Calls `create_polygon` with `smooth=True` and forwards any additional keyword arguments, such as `fill` and `outline`, directly to the canvas. Returns the canvas item ID so callers can bind events or configure the shape later.

**Line 178** — Defines `otxt`, the outlined text function. It accepts an outline color `ol` and an outline width `ow` in addition to the standard text parameters.

**Lines 179–182** — Iterate over a grid of offsets ranging from negative `ow` to positive `ow` in both x and y directions. For every offset except (0, 0), which would overwrite the actual text position, a copy of the text is drawn in the outline color. This produces a solid outline effect by painting the background copies in all directions before the foreground text is drawn on top.

**Line 183** — Draws the actual text in the foreground fill color at the exact target position and returns its canvas ID.

**Line 185** — Defines `cbtn`, the canvas button factory. It creates a complete button with a drop-shadow, a face, and a centered label, all bound to the same callback command.

**Line 186** — Draws the shadow by calling `rr` offset by four pixels down and to the right, filled with the darker shade color `dark` and no outline. Since it is drawn first, it sits beneath the main button face.

**Line 187** — Draws the button face at the actual coordinates using `rr`, filling with the primary `color`. The return value `b` is the canvas polygon ID for the button shape.

**Line 188** — Draws the label text centered at the midpoint of the button rectangle, using integer division to find the center coordinates. The variable `t` holds the canvas text item ID.

**Lines 189–190** — Binds the mouse click event `<Button-1>` to both the polygon `b` and the text `t`. The lambda captures `cmd` by default argument `c=cmd` to avoid closure issues in loops. Without this capture, all buttons created in a loop would share the last value of `cmd`.

**Line 191** — Returns both canvas IDs so callers can add additional bindings, such as hover cursor changes, if needed.

---

**The `App` Class — Lines 193 to 218**

```python
193  class App(tk.Tk):
194      def __init__(self):
195          super().__init__()
196          self.title("ECETHON")
197          self.geometry(f"{W}x{H}")
198          self.resizable(False, False)
199          self._pages = {}
200          for name, cls in [
201              ("home",    HomePage),
202              ("topics",  TopicsPage),
203              ("about",   AboutPage),
204              ("creator", CreatorPage),
205              ("complex", ComplexPage),
206              ("linear",  LinearPage),
207              ("fourier", FourierPage),
208              ("laplace", LaplacePage),
209          ]:
210              p = cls(self)
211              p.place(x=0, y=0, width=W, height=H)
212              self._pages[name] = p
213          self.go("home")
214
215      def go(self, name):
216          for p in self._pages.values():
217              p.lower()
218          page = self._pages[name]
219          if hasattr(page, "on_show"):
220              page.on_show()
221          page.lift()
```

**Line 193** — Declares `App` as a subclass of `tk.Tk`, making it the root window of the Tkinter application. There can only be one `tk.Tk` instance in any Tkinter program; all other windows must be `Toplevel` instances.

**Line 195** — Calls `super().__init__()` to initialize the root window and the underlying Tcl/Tk interpreter. This must happen before any Tkinter widgets or canvas operations can be performed.

**Lines 196–198** — Set the window title, apply the fixed geometry string, and disable resizing in both horizontal and vertical directions. Locking the size prevents layout calculations from becoming invalid when the user drags the window edges.

**Line 199** — Initializes `_pages` as an empty dictionary. This will map each string name to the corresponding instantiated page frame.

**Lines 200–209** — Define the ordered list of (name, class) pairs for every page in the application. The order matters because pages are instantiated and stacked in this sequence, with later pages initially on top until `self.go("home")` is called.

**Line 210** — Instantiates each page class, passing `self` (the `App` window) as the parent. Each page calls `super().__init__(app, ...)` in its own constructor and registers itself as a child widget of the root window.

**Line 211** — Places each page at pixel position (0, 0) with the full window dimensions using Tkinter's `place` geometry manager. All pages now physically overlap each other; only their z-order (stacking depth) determines which one is visible.

**Line 212** — Stores the instantiated page in `_pages` under its string name key, enabling navigation by name string.

**Line 213** — Calls `self.go("home")` immediately after all pages are built to bring the home page to the top of the stack, making it the first visible page when the application starts.

**Line 215** — Defines the `go` navigation method, which accepts a page name string and switches the visible page.

**Lines 216–217** — Iterates over every page and calls `.lower()` on each one, pushing them all to the bottom of the canvas stacking order simultaneously.

**Lines 218–221** — Looks up the target page, checks for the optional `on_show` hook and calls it if present (used by `AboutPage` to reset its slide index), then calls `.lift()` to bring the target page to the top of the stack, making it the only visually exposed frame.

---

**The `Page` Base Class — Lines 223 to 240**

```python
223  class Page(tk.Frame):
224      def __init__(self, app):
225          super().__init__(app, width=W, height=H, bg=SKY)
226          self._app = app
227
228      def go(self, name):
229          self._app.go(name)
230
231      def _topbar(self, cv, back="home"):
232          cbtn(cv, 30, 18, 180, 68, "BACK",
233               ("OPTIVagRound-Bold", 20), RED, RED_DK, lambda: self.go(back), r=18)
234          otxt(cv, W//2, 44, "ECETHON",
235               ("OPTIVagRound-Bold", 26), fill=GREEN, ol=NAVY, ow=2)
236          cbtn(cv, W-180, 18, W-30, 68, "HOME",
237               ("OPTIVagRound-Bold", 20), YELLOW, YEL_DK, lambda: self.go("home"), r=18)
238
239      @staticmethod
240      def _purplebar(cv):
241          cv.create_rectangle(0, H-70, W, H, fill=PURPLE, outline="")
```

**Line 223** — Declares `Page` as a subclass of `tk.Frame`. Every topic page inherits from this class, inheriting its coordinate system, background color, and shared navigation methods.

**Line 225** — Creates a full-size frame matching the window dimensions with the sky-blue background. Setting an explicit size is required because `place` does not shrink or expand frames automatically.

**Line 226** — Stores `app` as `self._app` so that any subclass method can call navigation or access the root window without needing a global reference.

**Lines 228–229** — Define `go` as a shortcut wrapper. Subclasses can call `self.go("topics")` instead of `self._app.go("topics")`, reducing verbosity and hiding the implementation detail.

**Lines 231–237** — Draw the top navigation bar shared by every topic page. The BACK button is positioned 30 pixels from the left edge and navigates to whichever destination was passed as the `back` argument when the bar was drawn. The centered ECETHON label is drawn in green with a navy outline. The HOME button is positioned 30 pixels from the right edge and always navigates to the home page regardless of the current page.

**Lines 239–241** — Define the purple footer bar as a `@staticmethod` because it requires only the canvas reference and no instance state. A filled rectangle from x=0, y=H−70 to x=W, y=H draws the solid purple strip that anchors every page visually.

---

**The `ComplexPage` Class — Calculation Flow**

```python
  def _calc(self):
      raw = self.expr.get()
      if not raw.strip():
          self._result_modal(error="⚠  Please enter an expression")
          return
      try:
          res = _parse_num(raw)
      except ZeroDivisionError:
          self._result_modal(error="⚠  Division by zero")
          return
      except Exception:
          self._result_modal(
              error="⚠  Invalid expression\n"
                    "Examples: (3+2i)*(1-i)  |  1/2+sqrt(3)*i  |  2^4  |  pi+e*i")
          return

      r, i  = res.real, res.imag
      sign  = "+" if i >= 0 else "-"
      r_str = f"{r:g}{sign}{abs(i):g}j"
      mag   = abs(res)
      phase = math.degrees(cmath.phase(res))
      self._result_modal(r_str=r_str, r=r, i=i, mag=mag, phase=phase)
```

**`raw = self.expr.get()`** — Reads the raw string from the Tkinter entry widget. This is the only point of contact between the user's keyboard input and the computation engine.

**`if not raw.strip()`** — Checks for a blank or whitespace-only input before attempting any parsing. Passing an empty string to `_parse_num` would return zero without error, which would silently produce a misleading result, so the guard shows an explicit warning instead.

**`res = _parse_num(raw)`** — Passes the raw string through the full normalization-and-parsing pipeline and returns a Python `complex` number. This single call handles all shorthand notations.

**`except ZeroDivisionError`** — Catches the specific case of division by zero, such as `1/(1-1)`, and shows a targeted message rather than the generic invalid-expression error.

**`except Exception`** — Catches all other parse failures, including unrecognized function names, mismatched parentheses, or completely unparseable strings, and shows a helpful message with concrete valid examples.

**`r, i = res.real, res.imag`** — Decomposes the complex result into its real and imaginary components using Python's built-in `.real` and `.imag` attributes on the `complex` type.

**`sign = "+" if i >= 0 else "-"`** — Determines the display sign character. The imaginary component can be zero (yielding a real number), positive, or negative. This sign will appear between the real and imaginary parts in the result string.

**`r_str = f"{r:g}{sign}{abs(i):g}j"`** — Formats the full complex number as a compact string. The `:g` format code removes trailing zeros and uses scientific notation automatically for very large or very small values. `abs(i)` is used so the sign character handles the negative display, not the number itself.

**`mag = abs(res)`** — Computes the magnitude using Python's built-in `abs` on a `complex` type, which internally evaluates √(real² + imaginary²).

**`phase = math.degrees(cmath.phase(res))`** — Computes the phase angle: `cmath.phase` returns the angle in radians in the range (−π, π], then `math.degrees` converts to degrees for display.

---

**The `LinearPage` Class — Matrix Reading and Operations**

```python
  @staticmethod
  def _parse_cell(s):
      s = s.strip() or "0"
      return _parse_num(s)

  def _read_grid(self, cells):
      arr = np.array([[self._parse_cell(cells[r][c].get())
                       for c in range(len(cells[r]))]
                      for r in range(len(cells))], dtype=complex)
      if not np.any(arr.imag):
          return arr.real
      return arr

  def _calc(self):
      ...
      if op == "Addition (A+B)":
          C, title = A + B, "A + B"
      elif op == "Subtraction (A-B)":
          C, title = A - B, "A − B"
      elif op == "Multiplication (A×B)":
          C, title = A @ B, "A × B"
      elif op == "Division (A×B⁻¹)":
          C, title = A @ np.linalg.inv(B), "A × B⁻¹"
```

**`s.strip() or "0"`** — Strips whitespace and falls back to `"0"` for blank cells. This prevents the user from having to fill every cell manually; untouched cells behave as zeros.

**`return _parse_num(s)`** — Routes the cell string through the full shared parsing pipeline, meaning cells can contain complex values like `3+4j`, fractions like `1/2`, constants like `pi`, or expressions like `sqrt(2)`.

**`np.array([...], dtype=complex)`** — Assembles the entire grid into a NumPy array with `complex` dtype using a nested list comprehension. The `dtype=complex` ensures all arithmetic involving the array preserves complex values even when individual cells are real-valued.

**`if not np.any(arr.imag): return arr.real`** — Checks whether any imaginary component in the entire array is non-zero. If all imaginary parts are zero, the real part is returned as a pure real array, which produces cleaner numeric output without trailing `.0+0.0j` notation.

**`A + B`** — NumPy element-wise addition. NumPy automatically validates that A and B have the same shape and raises a `ValueError` if they do not, which is caught by the surrounding `try/except`.

**`A - B`** — NumPy element-wise subtraction with the same shape validation.

**`A @ B`** — NumPy matrix multiplication (dot product), requiring that the number of columns in A equals the number of rows in B. This is distinct from `A * B`, which would perform element-wise multiplication.

**`A @ np.linalg.inv(B)`** — Computes matrix division as multiplication by the inverse of B. `np.linalg.inv` raises a `LinAlgError` if B is singular (non-invertible), which the surrounding exception handler catches and displays as an error message.

---

**The `LinearPage` Class — Equation Solving**

```python
  def _calc_linear_equations(self):
      lines = [ln.strip() for ln in self._eq_text.get("1.0", "end").splitlines() if ln.strip()]
      ...
      for line in lines:
          if "=" in line:
              left, right = line.split("=", 1)
          else:
              left, right = line, "0"
          lhs = self._parse_linear_expr(left, locs)
          rhs = self._parse_linear_expr(right, locs)
          equations.append(sp.Eq(lhs, rhs))
      ...
      linear_eqs = [eq.lhs - eq.rhs for eq in equations]
      A, b = sp.linear_eq_to_matrix(linear_eqs, vars_list)
      sol_set = sp.linsolve((A, b), *vars_list)
```

**`self._eq_text.get("1.0", "end").splitlines()`** — Reads the entire content of the multi-line Text widget from position `"1.0"` (line 1, character 0) to `"end"`, then splits it at every newline. The `if ln.strip()` filter removes blank lines from the list.

**`line.split("=", 1)`** — Splits each equation string at the first `=` sign only, using `maxsplit=1`. This preserves any `=` characters that might appear inside an expression, though in practice linear equations have exactly one equality.

**`left, right = line, "0"`** — If no `=` is found, the entire line is treated as a left-hand side equal to zero, which handles input like `3x + y` as the equation `3x + y = 0`.

**`sp.Eq(lhs, rhs)`** — Creates a SymPy symbolic equation object. This is preferred over a raw expression because SymPy's `linsolve` and `linear_eq_to_matrix` functions require `Eq` objects to identify the equality structure.

**`eq.lhs - eq.rhs`** — Moves all terms to one side, producing the form `f(vars) = 0` needed by `linear_eq_to_matrix`.

**`sp.linear_eq_to_matrix(linear_eqs, vars_list)`** — Extracts the coefficient matrix A and constant vector b from the list of left-hand-side expressions. This function performs symbolic analysis of each expression to identify coefficients belonging to each variable.

**`sp.linsolve((A, b), *vars_list)`** — Solves the linear system exactly using symbolic Gaussian elimination. Returns a `FiniteSet` of solution tuples, or `EmptySet` if no solution exists, or a parametric set if the system is underdetermined.

---

**The `FourierPage` Class — Coefficient Computation**

```python
  def _calc(self):
      ...
      pw_args = [(f, (x_sym >= xa) & (x_sym <= xb)) for f, xa, xb in pieces_sym]
      pw_args.append((sp.Integer(0), True))
      f_full = sp.Piecewise(*pw_args)

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

      series = a0_sym
      for k in range(1, N + 1):
          ak = an_sym.subs(n_sym, k)
          bk = bn_sym.subs(n_sym, k)
          series += ak * sp.cos(k * sp.pi * x_sym / L_sym)
          series += bk * sp.sin(k * sp.pi * x_sym / L_sym)
      series = sp.simplify(series)
```

**`(x_sym >= xa) & (x_sym <= xb)`** — Creates a SymPy boolean condition using the symbolic comparison operators. The `&` operator creates a logical `And`, meaning the piece applies when x is within the closed interval [xa, xb].

**`pw_args.append((sp.Integer(0), True))`** — Adds a final fallback piece that evaluates to zero everywhere. SymPy's `Piecewise` requires at least one unconditional `True` clause; without it, the expression is undefined outside all defined intervals, which would cause integration to fail.

**`sp.Piecewise(*pw_args)`** — Constructs the combined piecewise function. SymPy evaluates each condition in order and returns the value from the first matching piece, exactly as mathematical piecewise notation specifies.

**`sp.Rational(1, 2) / L_sym * sp.integrate(f_full, (x_sym, a_sym, b_sym))`** — Computes the Fourier constant term a₀ symbolically. `sp.Rational(1, 2)` is an exact fraction rather than the floating-point `0.5`, preserving exactness throughout the symbolic computation. The integration is performed over the full period from a to b.

**`sp.Integer(1) / L_sym * sp.integrate(f_full * sp.cos(n_sym * sp.pi * x_sym / L_sym), ...)`** — Computes the general cosine coefficient aₙ. The symbol `n_sym` remains symbolic at this stage, so the integral is computed once in closed form as a function of n, not repeated for every value of n.

**`sp.Integer(1) / L_sym * sp.integrate(f_full * sp.sin(n_sym * sp.pi * x_sym / L_sym), ...)`** — Computes the general sine coefficient bₙ by the same approach, integrating the product of the piecewise function with the sine harmonic basis function.

**`for k in range(1, N + 1):`** — Iterates from n=1 to the user-specified harmonic count N inclusive.

**`an_sym.subs(n_sym, k)`** — Substitutes the concrete integer k for the symbolic n in the general coefficient expression, producing the specific numeric or simplified symbolic coefficient for harmonic k.

**`series += ak * sp.cos(...) + bk * sp.sin(...)`** — Accumulates the k-th harmonic term into the series. Each iteration adds one cosine term and one sine term weighted by their respective coefficients.

**`series = sp.simplify(series)`** — Applies a final simplification pass over the fully accumulated series to reduce redundant terms, collect like terms, and present the result in its most compact symbolic form.

---

**The `FourierPage` Result Modal — Graph Rendering**

```python
  f_lamb = sp.lambdify(x_sym, f_expr, "numpy")
  s_lamb = sp.lambdify(x_sym, series, "numpy")
  y_orig = np.array(f_lamb(x_vals), dtype=float)
  y_ser  = np.real(np.array(s_lamb(x_vals), dtype=complex)).astype(float)

  fig, ax = plt.subplots(figsize=(GW / 100, GH / 100), dpi=100)
  ax.plot(x_vals, y_orig, color="white", lw=1.5, ls="--", label="Original  f(x)")
  ax.plot(x_vals, y_ser,  color=self._ORG, lw=2, label=f"Fourier approx  N={N}")
```

**`sp.lambdify(x_sym, f_expr, "numpy")`** — Converts the symbolic piecewise expression into a fast NumPy-compatible function. Without `lambdify`, evaluating the SymPy expression at 1000 points would call SymPy's symbolic evaluator 1000 times, which would be prohibitively slow for interactive use.

**`np.array(f_lamb(x_vals), dtype=float)`** — Evaluates the lambdified original function over all 1000 x values at once as a NumPy vectorized operation and casts to float, discarding any negligible imaginary parts that might appear due to floating-point rounding in piecewise boundaries.

**`np.real(np.array(s_lamb(x_vals), dtype=complex)).astype(float)`** — The Fourier series may produce tiny imaginary components from accumulated floating-point operations on trigonometric terms. Casting to `complex` first then extracting only the real part with `np.real` before converting to `float` ensures the plot y-values are always purely real.

**`plt.subplots(figsize=(GW / 100, GH / 100), dpi=100)`** — Creates a figure sized exactly to the allocated graph frame. Dividing the pixel dimensions by the DPI (100) gives the figure size in inches that Matplotlib requires.

**`ax.plot(x_vals, y_orig, ...)`** — Plots the original piecewise function as a white dashed line. Using a dashed style visually distinguishes the target signal from the approximation without overlapping or obscuring either line.

**`ax.plot(x_vals, y_ser, ...)`** — Plots the Fourier series approximation as a solid orange line. As N increases and the user recalculates, this line converges visually toward the dashed white original, providing an immediate graphical verification of the theoretical convergence property.

---

**The `LaplacePage` Class — Transform Execution**

```python
  def _calc(self):
      t, s = sp.Symbol("t", positive=True), sp.Symbol("s")
      op   = self.op_var.get()
      locs = {**_SAFE_LOCALS, 't': t, 's': s}
      if op == "Laplace Transform":
          preprocessed = _laplace_preprocess(raw)
          expr = _parse_symbolic(preprocessed, locs)
          result = sp.simplify(sp.laplace_transform(expr, t, s, noconds=True))
          expr_display = _laplace_clean_text(sp.simplify(expr))
          fs_display = _laplace_clean_text(sp.simplify(sp.apart(result, s)))
          rows = [("f(t) =", expr_display), ("F(s) =", fs_display)]
      else:
          expr = _parse_symbolic(raw, locs)
          result = sp.inverse_laplace_transform(expr, s, t, noconds=True)
          expr_display = _laplace_clean_text(sp.simplify(expr))
          result_display = _laplace_clean_text(sp.simplify(result))
          rows = [("F(s) =", expr_display), ("f(t) =", result_display)]
```

**`sp.Symbol("t", positive=True)`** — Creates the time-domain variable t with the `positive=True` assumption. This is required for SymPy's Laplace transform engine to correctly evaluate integrals of the form ∫₀^∞ f(t) e^(−st) dt, because the assumption on t allows SymPy to simplify expressions that would otherwise require absolute values or case analysis.

**`sp.Symbol("s")`** — Creates the complex frequency variable s without assumptions. The s-domain variable must be unrestricted because s is a complex number in general.

**`{**_SAFE_LOCALS, 't': t, 's': s}`** — Extends the base whitelist by merging the two transform variables into it. The double-asterisk unpacking copies all entries from `_SAFE_LOCALS` first, then the two new keys override or add `t` and `s`, making them available to the expression parser.

**`_laplace_preprocess(raw)`** — Applies the Laplace-specific preprocessing before symbolic parsing, stripping unit step functions and normalizing all impulse aliases to `DiracDelta(t)`.

**`sp.laplace_transform(expr, t, s, noconds=True)`** — Calls SymPy's built-in Laplace transform integrator. The `noconds=True` flag suppresses the convergence condition tuple that SymPy would otherwise return alongside the result, keeping the output clean for display.

**`sp.apart(result, s)`** — Applies partial fraction decomposition to the s-domain result before display. This decomposes a rational expression like `(2s+1)/(s²+3s+2)` into `1/(s+1) + 1/(s+2)`, a form directly comparable to standard Laplace transform tables and more interpretable for engineering analysis.

**`sp.inverse_laplace_transform(expr, s, t, noconds=True)`** — Computes the time-domain inverse by recognizing the s-domain expression as a known transform pair and returning the corresponding f(t). SymPy handles common pairs including exponentials, sinusoids, polynomials, and their combinations.

**`_laplace_clean_text(sp.simplify(result))`** — Runs simplify first to reduce the expression, then converts all SymPy internal notation back to human-readable form for the result modal display.

---

**Entry Point — Final Line**

```python
  if __name__ == "__main__":
      App().mainloop()
```

**`if __name__ == "__main__":`** — The standard Python guard that ensures the application only launches when this file is executed directly. If the file were imported as a module by another script, this block would be skipped, preventing an unintended window from opening.

**`App().mainloop()`** — Instantiates the `App` class, which builds all pages, then calls `mainloop()` to start the Tkinter event loop. The event loop runs indefinitely, processing user clicks, key presses, and window events, until the user closes the window.

