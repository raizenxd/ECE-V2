# HOW TO USE — ECETHON

A simple step-by-step guide for students. All examples use basic numbers only.

---

## Starting the App

1. Open a terminal in the project folder
2. Run:
   ```
   python ECETHON.py
   ```
3. A window titled **ECETHON** will open

---

## Home Screen

You will see the **ECETHON** title with three buttons:

| Button | What it does |
|---|---|
| **START** | Go to the topic selection screen |
| **ABOUT** | Learn about the project and each topic |
| **CREATOR** | See the creator profile page |

Click **START** to begin.

---

## Selecting a Topic

You will see five colored cards. Click any one to open its calculator.

| Card | Color |
|---|---|
| Complex Numbers | Green |
| Linear Algebra | Purple |
| System of Linear Equation | Violet |
| Fourier Series | Orange |
| Laplace Transform | Pink |

---

## 1. Complex Numbers

### How to Use

1. Click **Complex Numbers** from the topic screen
2. Click the input box in the middle of the screen
3. Type your expression
4. Press **CALCULATE** or hit **Enter**
5. A result window will pop up

### Simple Examples

| You type | What you are computing |
|---|---|
| `3+2i` | A complex number with real part 3 and imaginary part 2 |
| `(3+2i)+(1+4i)` | Addition of two complex numbers |
| `(3+2i)*(1-i)` | Multiplication of two complex numbers |
| `(4+2i)/(2+0i)` | Division of two complex numbers |

### Example — Try This

Type: `3+4i`

**Expected Output:**

| Field | Value |
|---|---|
| Result | `(3+4j)` |
| Real part | `3.0` |
| Imaginary part | `4.0` |
| Magnitude | `5.000000` |
| Phase | `53.13°` |

> **Magnitude** = the distance from the origin = √(3² + 4²) = √25 = 5  
> **Phase** = the angle = tan⁻¹(4/3) ≈ 53.13°

### Another Example

Type: `(3+4i)*(1+2i)`

**Expected Output:**

| Field | Value |
|---|---|
| Result | `(-5+10j)` |
| Real part | `-5.0` |
| Imaginary part | `10.0` |
| Magnitude | `11.180340` |
| Phase | `116.57°` |

### Error Messages

| Message | Cause | Fix |
|---|---|---|
| Please enter an expression | Empty input field | Type something before clicking CALCULATE |
| Division by zero | Dividing by 0 | Check your denominator |
| Invalid expression | Unrecognized input | Use only numbers, `i`, `+`, `-`, `*`, `/`, `(` `)` |

---

## 2. Linear Algebra

### How to Use

1. Click **Linear Algebra** from the topic screen
2. Choose an **Operation** from the dropdown at the top:
   - `Addition (A+B)`
   - `Subtraction (A-B)`
   - `Multiplication (A×B)`
   - `Division (A×B⁻¹)`
3. Set the number of rows and columns for Matrix A and Matrix B using the spinboxes
4. Click **SET** to build the grids
5. Click each cell and type your numbers
6. Click **CALCULATE**

### Matrix Size Rules

| Operation | Requirement |
|---|---|
| Addition | A and B must be the same size |
| Subtraction | A and B must be the same size |
| Multiplication | Columns of A must equal Rows of B |
| Division | B must be a square matrix (e.g. 2×2, 3×3) |

### Example — Addition (2×2)

Set both A and B to **2 rows, 2 cols**. Select **Addition (A+B)**.

**Matrix A:**
```
1   2
3   4
```

**Matrix B:**
```
5   6
7   8
```

**Expected Output:**
```
Row 1:   6    8
Row 2:   10   12
```

### Example — Multiplication (2×2)

Select **Multiplication (A×B)** with both matrices **2×2**.

**Matrix A:**
```
1   2
3   4
```

**Matrix B:**
```
2   0
1   3
```

**Expected Output:**
```
Row 1:   4    6
Row 2:   10   12
```

### Example — Division (2×2)

Select **Division (A×B⁻¹)**. The app computes A × (inverse of B).

**Matrix A:**
```
1   0
0   1
```

**Matrix B:**
```
2   0
0   2
```

**Expected Output:**
```
Row 1:   0.5    0
Row 2:   0      0.5
```

### Error Messages

| Message | Cause | Fix |
|---|---|---|
| Invalid value in a cell | A cell has non-numeric text | Check all cells contain numbers |
| Shape mismatch | Wrong matrix sizes for the operation | Re-read the size rules above |
| Singular matrix | B cannot be inverted (its determinant is 0) | Use a different Matrix B |

---

## 3. System of Linear Equation

### How to Use

1. Click **System of Linear Equation** from the topic screen
2. Enter one equation per line (for example: `3x + y = 9`)
3. Optionally enter variable names in the variables box (example: `x, y`)
4. Click **CALCULATE**

### Simple Example

Enter:

```text
3x + y = 9
x + 2y = 8
```

**Expected Output:**

| Field | Value |
|---|---|
| Variables | `x, y` |
| Solution vector | `[2. 3.]` |
| x | `2` |
| y | `3` |

### Notes

- You can use additional variables like `x, y, z, a, b, c, ...`
- Implicit multiplication is supported here, so `3x` is valid
- If variable box is blank, the app auto-detects variables from equations

### Error Messages

| Message | Cause | Fix |
|---|---|---|
| Enter at least one equation | No equation lines were entered | Add one or more equations |
| Parse error | Invalid equation format | Check operators and equation syntax |
| Invalid variable name(s) | Variable list has invalid names | Use names like `x`, `y1`, `z_var` |
| No solution | Inconsistent system | Check coefficients and constants |

---

## 4. Fourier Series

### How to Use

1. Click **Fourier Series** from the topic screen
2. Each row is one **piece** of your piecewise function
   - The first column is the function expression (use `x` as the variable)
   - The second column is the start of the interval
   - The third column is the end of the interval
3. Click **+ ADD PIECE** to add more pieces, **REMOVE LAST** to remove one
4. Set **Harmonics N** — how many terms to include (start with `3` or `5`)
5. Limits are auto-detected from your piece intervals
6. Click **CALCULATE**

### Simple Example — Constant Function

Use one piece only. Clear the second default row.

| # | f(x) | From | To |
|---|---|---|---|
| 1 | `1` | `0` | `2` |

Set **N = 3**.

**Expected Output (approximate):**

| Field | Value |
|---|---|
| a₀ | `2.0` |
| a₁ | `≈ 0` |
| b₁ | `≈ 0` |
| Formula | `f(x) ≈ 1.0` |

> A constant function has no sine or cosine terms — only a₀/2 = 1.

### Simple Example — Piecewise (Two Pieces)

| # | f(x) | From | To |
|---|---|---|---|
| 1 | `0` | `-1` | `0` |
| 2 | `1` | `0` | `1` |

Set **N = 5**.

**Expected Output:**

| Field | Value |
|---|---|
| a₀ | `1.0` |
| a₀/2 | `0.5` |
| a₁ | `≈ 0` |
| b₁ | `≈ 0.6366` |

**Graph shows:**
- White dashed line — the original step function (0 then 1)
- Orange line — the smooth Fourier approximation (wavy, getting closer with more N)

> Increasing **N** makes the orange line follow the white line more closely.

### Tip — What N to Use

| N value | Result |
|---|---|
| 1–3 | Rough approximation, very wavy |
| 5–10 | Good approximation for smooth functions |
| 15–20 | Very close, but slower to compute |

### Error Messages

| Message | Cause | Fix |
|---|---|---|
| Parse error | Invalid expression in a piece | Use only `x`, numbers, `+`, `-`, `*`, `/`, `**` |
| Integration error | SymPy could not integrate | Simplify the expression |

---

## 5. Laplace Transform

### How to Use

1. Click **Laplace Transform** from the topic screen
2. Choose the **mode** from the dropdown:
   - **Laplace Transform** — you enter `f(t)`, the app finds `F(s)`
   - **Inverse Laplace** — you enter `F(s)`, the app finds `f(t)`
3. Type your expression in the input box
   - Use `t` as the variable for Laplace mode
   - Use `s` as the variable for Inverse Laplace mode
4. Press **CALCULATE** or hit **Enter**

### Simple Examples — Laplace Transform

| You type | f(t) | Expected F(s) |
|---|---|---|
| `1` | 1 | `1/s` |
| `t` | t | `1/s²` |
| `exp(-t)` | e⁻ᵗ | `1/(s+1)` |
| `exp(-2*t)` | e⁻²ᵗ | `1/(s+2)` |
| `t*exp(-t)` | t·e⁻ᵗ | `1/(s+1)²` |
| `sin(t)` | sin(t) | `1/(s²+1)` |
| `cos(t)` | cos(t) | `s/(s²+1)` |

### Example — Try This

Select mode: **Laplace Transform**

Type: `exp(-t)`

**Expected Output:**

| Field | Value |
|---|---|
| f(t) | `exp(-t)` |
| F(s) | `1/(s + 1)` |
| F(s) simplified | `1/(s + 1)` |

---

### Simple Examples — Inverse Laplace

| You type | F(s) | Expected f(t) |
|---|---|---|
| `1/s` | 1/s | `1` (unit step) |
| `1/s**2` | 1/s² | `t` |
| `1/(s+1)` | 1/(s+1) | `exp(-t)` |
| `1/(s+3)` | 1/(s+3) | `exp(-3t)` |
| `s/(s**2+1)` | s/(s²+1) | `cos(t)` |

### Example — Try This

Select mode: **Inverse Laplace**

Type: `1/(s+3)`

**Expected Output:**

| Field | Value |
|---|---|
| F(s) | `1/(s + 3)` |
| f(t) | `exp(-3*t)` |
| f(t) simplified | `exp(-3*t)` |

### Error Messages

| Message | Cause | Fix |
|---|---|---|
| Enter an expression | Empty input | Type an expression first |
| SymPy error | The transform is not supported | Try a simpler expression |

---

## Navigation Tips

| Button | Where it appears | What it does |
|---|---|---|
| **BACK** | Top-left on every page | Go to the previous page |
| **HOME** | Top-right on every page | Go back to the home screen |
| **NEXT / BACK** | About page only | Move between the 5 info slides |
| **CLOSE** | Result popups | Dismiss the result and return to input |

---

## Quick Reference — Input Rules

- Use `i` or `j` or `I` for the imaginary unit (all are the same)
- Use `*` for multiplication in most pages: `3*x`, not `3x`
- In **System of Linear Equation**, implicit multiplication is allowed (`3x` is valid)
- Use `**` or `^` for powers: `x**2` or `x^2`
- Use `pi` for π and `e` for Euler's number
- Parentheses `( )` are supported and recommended for clarity
- Decimal numbers are fine: `1.5`, `0.25`, `3.14`
