# HOW TO USE — ECETHON

---

## Starting the App

```
python ECETHON.py
```

Click **START** → select a topic card → use its calculator.

---

## Valid Inputs (All Pages)

These work everywhere in the app:

| Type | Valid examples |
|------|---------------|
| Numbers | `5`, `-3`, `3.14`, `1/2`, `1e3` |
| Exponents | `2^4`, `x^2`, `2**4` |
| Operators | `+` `-` `*` `/` `^` `**` `×` `÷` |
| Constants | `pi`, `e`, `E`, `inf`, `oo` |
| Functions | `sqrt`, `cbrt`, `exp`, `log`, `ln`, `log10` |
| Trig | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` |
| Hyperbolic | `sinh`, `cosh`, `tanh` |
| Other | `abs`, `floor`, `ceil`, `sign`, `re`, `im`, `arg`, `conj` |

---

## 1 · Complex Numbers

**Variable:** any expression  
**Output:** result, real, imaginary, magnitude, phase

### Valid Inputs

| Format | Example |
|--------|---------|
| Using `i` / `j` / `I` | `3+2i` · `1-4j` · `3+2*I` |
| Implicit form | `2I` · `5I` |
| With constants | `pi*i` · `exp(pi*i)` |
| With functions | `sqrt(2)+pi*i` · `abs(3+4i)` |
| With fractions | `1/2+3i` · `(2/3)-(1/4)i` |
| Full expression | `(3+2i)*(1-i)` · `(1+i)^2` |

### Example

Input: `3+4i`

| Field | Value |
|-------|-------|
| Result | `(3+4j)` |
| Real part | `3.0` |
| Imaginary part | `4.0` |
| Magnitude | `5.000000` |
| Phase | `53.13°` |

Input: `(3+2i)*(1-i)`

| Field | Value |
|-------|-------|
| Result | `(5-1j)` |
| Real part | `5.0` |
| Imaginary part | `-1.0` |
| Magnitude | `5.099020` |
| Phase | `-11.31°` |

Input: `sqrt(2)+pi*i`

| Field | Value |
|-------|-------|
| Real part | `1.41421...` |
| Imaginary part | `3.14159...` |
| Magnitude | `3.44787...` |
| Phase | `65.69°` |

### Errors

| Message | Fix |
|---------|-----|
| Please enter an expression | Type something first |
| Division by zero | Check your denominator |
| Invalid expression | Use numbers, `i/j/I`, operators, parentheses |

---

## 2 · Linear Algebra

**Inputs:** matrix cells accept any numeric expression  
**Max size:** 5×5  
**Operations:** `A+B` · `A-B` · `A×B` · `A×B⁻¹`

### Valid Cell Inputs

| Type | Example |
|------|---------|
| Integer | `3`, `-7` |
| Decimal | `1.5`, `-0.25` |
| Fraction | `1/2`, `3/4` |
| Complex | `3+2i`, `1-4j` |
| Expression | `sqrt(2)`, `pi`, `exp(1)` |

### Matrix Size Rules

| Operation | Rule |
|-----------|------|
| Addition / Subtraction | A and B must be the same size |
| Multiplication | Columns of A = Rows of B |
| Division (A×B⁻¹) | B must be square |

### Example — Addition (2×2)

Matrix A: `[[1, 2], [3, 4]]`  
Matrix B: `[[5, 6], [7, 8]]`

```
Row 1:   6    8
Row 2:   10   12
```

### Example — Multiplication (2×2)

Matrix A: `[[1, 2], [3, 4]]`  
Matrix B: `[[2, 0], [1, 3]]`

```
Row 1:   4    6
Row 2:   10   12
```

### Example — Solve X,Y,Z (A·X = B)

Matrix A (coefficients): `[[3, 1], [1, 2]]`  
Matrix B (constants): `[[9], [8]]`

```
x = 2
y = 3
```

### Errors

| Message | Fix |
|---------|-----|
| Invalid value in a cell | Check all cells for valid input |
| Shape mismatch | Check matrix sizes for the operation |
| Singular matrix | Matrix B is not invertible — change it |

---

## 3 · System of Linear Equations

**Variable:** any identifier, auto-detected or listed manually  
**Format:** one equation per line

### Valid Inputs

| Format | Example |
|--------|---------|
| Standard form | `3x + y = 9` |
| No `=` sign | `x + 2y` → treated as `= 0` |
| Implicit multiplication | `3x`, `2y`, `5z` |
| Fractions / decimals | `(1/3)x - z = 7` · `0.5x + y = 2` |
| Custom variable list | `x, y, z` in the variables field |

### Example

Input:
```
3x + y = 9
x + 2y = 8
```

| Field | Value |
|-------|-------|
| Variables | `x, y` |
| Solution vector | `[2. 3.]` |
| x = | `2` |
| y = | `3` |

Another example with 3 variables:
```
x + y + z = 6
2x - y + z = 3
x + 2y - z = 2
```

| x = | `1` |
|-----|-----|
| y = | `2` |
| z = | `3` |

### Errors

| Message | Fix |
|---------|-----|
| Enter at least one equation | Add at least one equation line |
| Parse error | Check operators and syntax |
| Invalid variable name(s) | Use valid names: `x`, `y1`, `z_var` |
| No solution | Check coefficients — system may be inconsistent |

---

## 4 · Fourier Series

**Variable:** `x`  
**Interval bounds:** any numeric expression  
**Harmonics:** N = 10 (fixed)  
**Max pieces:** 6

### Valid Inputs

| Type | f(x) example | Interval example |
|------|-------------|-----------------|
| Constant | `0`, `1`, `-3` | `-pi` to `pi` |
| Polynomial | `x`, `x^2`, `x+1` | `0` to `2` |
| Trig | `sin(x)`, `cos(2*x)` | `-pi` to `pi` |
| Mixed | `x*sin(x)` · `exp(-x)` | `0` to `pi` |

Each piece row: `f(x)` expression · `from x =` · `to x =`

### Example — Piecewise Square Wave

| # | f(x) | From | To |
|---|------|------|----|
| 1 | `0` | `-pi` | `0` |
| 2 | `1` | `0` | `pi` |

**Output coefficients:**

| Coeff | Value |
|-------|-------|
| a₀ | `1/2` |
| aₙ | `0` |
| bₙ | `(1 - cos(n*pi)) / (n*pi)` |

Graph: white dashed = original step · orange = Fourier approximation (N=10)

### Example — Sawtooth Wave

| # | f(x) | From | To |
|---|------|------|----|
| 1 | `x` | `-pi` | `pi` |

**Output:**

| Coeff | Value |
|-------|-------|
| a₀ | `0` |
| aₙ | `0` |
| bₙ | `2*(-1)^(n+1) / n` |

### Errors

| Message | Fix |
|---------|-----|
| Parse error | Check expression uses `x`, numbers, operators |
| Integration error | Simplify the expression |

---

## 5 · Laplace Transform

**Variable:** `t` → outputs `F(s)`

### Valid Inputs

| Signal | Accepted forms |
|--------|---------------|
| Unit step | `u(t)` · `U(t)` · `H(t)` · `step(t)` · `heaviside(t)` |
| Dirac delta | `delta(t)` · `δ(t)` · `dirac(t)` · `impulse(t)` · `DiracDelta(t)` |
| Exponential | `exp(-3*t)` · `e^-3t` · `e^-2.5t` |
| Trig shorthand | `sin2t` = `sin(2*t)` · `cos t` = `cos(t)` · `sinh3t` = `sinh(3*t)` |
| Polynomial | `t`, `t^2`, `t^3` |
| Combined | `exp(-t)*sin(2*t)` · `t*u(t)` |

> `e^-5t` automatically expands to `exp(-5*t)`  
> `sin2t`, `cos t`, `tanh3t` etc. auto-expand to function form

### Examples

| Input | F(s) output |
|-------|------------|
| `u(t)` | `1/s` |
| `delta(t)` | `1` |
| `exp(-t)` | `1/(s+1)` |
| `e^-3t` | `1/(s+3)` |
| `sin(2*t)` | `2/(s^2+4)` |
| `sin2t` | `2/(s^2+4)` |
| `cos(t)` | `s/(s^2+1)` |
| `t*exp(-t)` | `1/(s+1)^2` |
| `exp(-2*t)*sin(3*t)` | `3/((s+2)^2+9)` |
| `delta(t) + 7*u(t) - 6*exp(-5*t)` | `1 + 7/s - 6/(s+5)` |

### Try This

Input: `delta(t) + 7*u(t) - 6*exp(-5*t)`

| Field | Value |
|-------|-------|
| f(t) = | `delta(t) + 7*u(t) - 6*exp(-5*t)` |
| F(s) = | `1 + 7/s - 6/(s+5)` |

### Errors

| Message | Fix |
|---------|-----|
| Enter an expression | Type an expression first |
| SymPy error | Simplify or check the expression |

---

## Navigation

| Button | Action |
|--------|--------|
| **BACK** | Previous page |
| **HOME** | Home screen |
| **?** | Show accepted inputs for this page |
| **CLOSE** | Dismiss result popup |
