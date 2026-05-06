# ECETHON — Accepted Inputs

---

## Shared (all pages)

| Category | Accepted |
|----------|---------|
| **Numbers** | `5`, `-3`, `3.14`, `1/2`, `1e3`, `2.5e-4` |
| **Exponents** | `2^4`, `x^2` · `2**4`, `x**2` |
| **Operators** | `+` `-` `*` `/` `^` `**` `×` `÷` |
| **Constants** | `pi`, `e` / `E`, `inf` / `oo` |
| **Imaginary unit** | `i`, `j`, `I` (all equivalent) |

| Function | Shorthand / aliases |
|----------|---------------------|
| `sqrt(x)` | — |
| `cbrt(x)` | — |
| `exp(x)` | — |
| `log(x)` | `ln(x)` |
| `log10(x)` | — |
| `sin` `cos` `tan` | radians only |
| `asin` `acos` `atan` `atan2` | — |
| `sinh` `cosh` `tanh` | — |
| `abs(x)` | `Abs(x)` |
| `floor(x)` `ceil(x)` `sign(x)` | — |
| `re(z)` `im(z)` `arg(z)` `conj(z)` | — |

---

## Complex Numbers

**Variable:** any expression (no fixed variable)
**Output:** `a + bj`, real, imaginary, magnitude, phase

| Input format | Example |
|--------------|---------|
| Using i / j / I | `3+2i` · `1-4j` · `3+2*I` |
| Implicit form | `2I` · `3I` |
| With functions | `sqrt(2)+pi*i` · `exp(pi*i)` |
| With fractions | `1/2+3i` · `(2/3)-(1/4)i` |
| Full expression | `(3+2i)*(1-i)` · `abs(3+4i)` |

---

## Linear Algebra

**Variable:** matrix cell values (Matrix A and Matrix B, up to 5×5)
**Operations:** `A+B` · `A-B` · `A×B` · `A×B⁻¹`

Matrix cells accept any numeric expression — integers, decimals, fractions, or complex numbers using the shared syntax above.

**Solve X,Y,Z (A·X = B)**
- Place coefficients in Matrix A, constants in Matrix B (column vector)
- Or use Matrix A as an augmented matrix `[coefficients | constants]`
- Variables default to `x, y, z, w, v, u`

---

## System of Linear Equations

**Variable:** any identifier — auto-detected or listed manually

| Input | Example |
|-------|---------|
| One equation per line | `3x + y = 9` |
| No `=` sign | treated as `= 0` |
| Implicit multiplication | `3x`, `2y`, `5z` |
| Fractions / decimals | `(1/3)x - z = 7` · `0.5x + y = 2` |
| Custom variable list | `x, y, z` (comma-separated in the vars field) |

- Variables are auto-detected when the variable field is left blank
- Variable names must be valid identifiers: `x`, `y1`, `z_var`

---

## Fourier Series

**Variable:** `x`
**Interval bounds:** any numeric expression (`pi`, `-pi`, `0`, `2`, …)
**Harmonics:** N = 10 (fixed)

| Input | Example |
|-------|---------|
| Constant | `0`, `1`, `-3` |
| Polynomial | `x`, `x^2`, `x+1` |
| Trig | `sin(x)`, `cos(2*x)` |
| Mixed | `x*sin(x)`, `exp(-x)` |

Each piece row defines `f(x)` over `from ≤ x ≤ to`. Add up to 6 pieces.

---

## Laplace Transform

**Forward variable:** `t` → outputs `F(s)`
**Inverse variable:** `s` → outputs `f(t)`

| Signal | Accepted inputs |
|--------|----------------|
| Unit step | `u(t)` · `U(t)` · `H(t)` · `step(t)` · `heaviside(t)` |
| Dirac delta | `delta(t)` · `δ(t)` · `dirac(t)` · `impulse(t)` · `DiracDelta(t)` |
| Exponential | `exp(-3*t)` · `e^-3t` · `e^-2.5t` |
| Trig shorthand | `sin2t` → `sin(2*t)` · `cos t` → `cos(t)` · `tanh3t` → `tanh(3*t)` |

**Exponential shorthand:** `e^-5t` expands to `exp(-5*t)` automatically.
**Trig shorthand:** `sin`/`cos`/`tan`/`sinh`/`cosh`/`tanh` followed by a number and `t`.

| Example input | Result |
|---------------|--------|
| `delta(t) + 7*u(t) - 6*exp(-5*t)` | `1 + 7/s - 6/(s+5)` |
| `sin2t * u(t)` | `2/(s^2+4)` |
| `e^-t` | `1/(s+1)` |