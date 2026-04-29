# ECETHON — Accepted Input Formats

All input fields across every page (Complex Numbers, Linear Algebra, Fourier Series, Laplace Transform) use the same shared parser. The following formats are supported.

---

## Numbers

| Format | Examples |
|--------|---------|
| Integer | `5`, `-3`, `100` |
| Decimal | `3.14`, `-0.5`, `2.718` |
| Fraction | `1/2`, `3/4`, `22/7` |
| Scientific notation | `1e3`, `2.5e-4` |

---

## Exponents

| Format | Examples |
|--------|---------|
| Caret (MATLAB-style) | `2^4`, `x^2`, `e^x` |
| Double asterisk (Python-style) | `2**4`, `x**2` |

---

## Complex Numbers

| Format | Examples |
|--------|---------|
| Using `i` | `3+2i`, `1-4i`, `5i` |
| Using `j` | `3+2j`, `1-4j`, `5j` |
| Using `I` (SymPy) | `3+2*I` |
| With fractions | `1/2 + 3i`, `(2/3) - (1/4)i` |
| With expressions | `sqrt(2) + pi*i`, `exp(pi*i)` |
| Multiplication form | `2*i`, `3*j` |
| Implicit form | `2I`, `3I` |

---

## Constants

| Input | Value |
|-------|-------|
| `pi` | π ≈ 3.14159 |
| `e` | Euler's number ≈ 2.71828 |
| `E` | Same as `e` |

---

## Mathematical Functions

| Function | Description | Example |
|----------|-------------|---------|
| `sqrt(x)` | Square root | `sqrt(16)` → 4 |
| `exp(x)` | Exponential eˣ | `exp(1)` → e |
| `log(x)` | Natural log (ln) | `log(e)` → 1 |
| `ln(x)` | Natural log | `ln(e)` → 1 |
| `log10(x)` | Base-10 log | `log10(100)` → 2 |
| `sin(x)` | Sine (radians) | `sin(pi/2)` → 1 |
| `cos(x)` | Cosine (radians) | `cos(0)` → 1 |
| `tan(x)` | Tangent (radians) | `tan(pi/4)` → 1 |
| `asin(x)` | Arcsine | `asin(1)` → π/2 |
| `acos(x)` | Arccosine | `acos(1)` → 0 |
| `atan(x)` | Arctangent | `atan(1)` → π/4 |
| `atan2(y, x)` | Two-argument arctangent | `atan2(1, 1)` |
| `sinh(x)` | Hyperbolic sine | `sinh(0)` → 0 |
| `cosh(x)` | Hyperbolic cosine | `cosh(0)` → 1 |
| `tanh(x)` | Hyperbolic tangent | `tanh(0)` → 0 |
| `abs(x)` | Absolute value / modulus | `abs(-5)` → 5 |
| `floor(x)` | Round down | `floor(2.9)` → 2 |
| `ceil(x)` | Round up | `ceil(2.1)` → 3 |
| `sign(x)` | Sign of x | `sign(-3)` → -1 |
| `re(z)` | Real part | `re(3+2i)` → 3 |
| `im(z)` | Imaginary part | `im(3+2i)` → 2 |
| `arg(z)` | Argument (angle) | `arg(1+i)` → π/4 |
| `conj(z)` | Complex conjugate | `conj(3+2i)` → 3-2i |

---

## Operators

| Symbol | Operation | Example |
|--------|-----------|---------|
| `+` | Addition | `3 + 2i` |
| `-` | Subtraction | `5 - 3` |
| `*` | Multiplication | `2 * pi` |
| `/` | Division | `1/2` |
| `^` or `**` | Exponentiation | `2^3` or `2**3` |
| `×` | Multiplication (unicode) | `3 × 4` |
| `÷` | Division (unicode) | `6 ÷ 2` |

---

## Page-Specific Variables

| Page | Variable | Meaning |
|------|----------|---------|
| Fourier Series | `x` | Independent variable in f(x) expressions |
| Laplace Transform | `t` | Time-domain variable |
| Laplace Inverse | `s` | Frequency-domain variable |

---

## Combined Examples

```
(3 + 2i) * (1 - i)
(1/2 + sqrt(3)*i)^2
exp(pi * i) + 1
sin(pi/4) + cos(pi/4)*i
2^8 - 1
log(e^3)
abs(3 + 4i)
(2/3) / (1 + i)
```

---

## Notes

- Angles in trigonometric functions are in **radians**. Use `pi` for π.
- Fractions like `1/2` are evaluated exactly (e.g. `1/2 + 1/3` = `5/6`).
- Spaces are allowed anywhere in expressions.
- Both `i` and `j` are treated as the imaginary unit.
