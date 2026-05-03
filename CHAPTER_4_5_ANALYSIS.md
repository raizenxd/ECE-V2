# Chapter 4 and Chapter 5 Draft

This file is prepared for the project report sections:
- Chapter 4: Data Analysis and Presentation
- Chapter 5: Analysis

Project scope covered in this write-up:
- Complex Numbers
- Linear Algebra
- System of Linear Equation
- Fourier Series
- Laplace Transform

## Chapter 4 - Data Analysis and Presentation

### 4.1 Purpose of Chapter 4
The Data Analysis and Presentation section is the analytical core of this project. It explains how outputs produced by the Python-based ECETHON system are validated against manual mathematical derivations. The comparison is done for complex numbers, linear algebra operations, system of linear equations, Fourier series, and Laplace transforms.

The main objective is to show that the implemented algorithms are mathematically correct, numerically stable for typical engineering inputs, and useful for solving electronics engineering problems.

### 4.2 Comparative Analysis Method
For each topic, use the same 5-step flow:
1. Define a manual benchmark solution from standard formulas.
2. Run the same input in the ECETHON UI.
3. Record machine output (numeric and symbolic).
4. Compute discrepancy metrics:
   - absolute error = |manual - computed|
   - relative error = |manual - computed| / max(|manual|, epsilon)
5. Present result in table and figure form.

Recommended data tables:
- Complex number operation table (real part, imaginary part, magnitude, phase)
- Linear algebra transformation table (A, B, operation, output matrix)
- System-of-equations table (augmented matrix, interpreted equations, solved variables)
- Fourier coefficient table (a0, an, bn, N, approximation quality)
- Laplace transform table (input expression, transformed expression, simplified form)

### 4.3 Data Presentation per Topic

#### 4.3.1 Complex Numbers
Present side-by-side values for:
- Manual result of arithmetic operation
- App output: Result, Real part, Imaginary part, Magnitude, Phase

Key interpretation:
- Magnitude and phase values should match polar form conversion.
- Small decimal differences are expected due to floating-point evaluation.

#### 4.3.2 Linear Algebra
Present matrix operation outputs for:
- Addition
- Subtraction
- Multiplication
- Division via inverse (A * B^-1)

Key interpretation:
- Shape mismatch and singular matrix cases should be documented as controlled failure cases.
- For valid dimensions, matrix outputs should match manual matrix algebra.

#### 4.3.3 System of Linear Equation
For v3 behavior, show both user input styles:
- Standard A and B mode: solve A * X = B
- Augmented matrix mode in Matrix A only

Example (augmented matrix):

    [ 6  7  8 ]
    [ 7  8  9 ]

Interpreted equations:

    6x + 7y = 8
    7x + 8y = 9

Expected solution:

    x = -1
    y = 2

Key interpretation:
- The program correctly maps each row of the augmented matrix into one linear equation.
- This supports fast equation setup during demonstrations.

#### 4.3.4 Fourier Series
Present the following:
- Piecewise input function and interval bounds
- Symbolic coefficients a0, an, bn
- Approximation order N
- Overlay plot: original function vs Fourier approximation

Key interpretation:
- Increasing N improves approximation except near discontinuities (Gibbs effect).
- Coefficient expressions demonstrate correctness of integral-based implementation.

#### 4.3.5 Laplace Transform
Present both modes:
- Forward Laplace transform: f(t) -> F(s)
- Inverse Laplace transform: F(s) -> f(t)

Key interpretation:
- Simplified symbolic outputs should match known transform pairs.
- Inverse transform results validate the correctness of symbolic manipulation.

### 4.4 Visualizations Required in Chapter 4
Use clear, labeled visuals:
- Frequency-response style Fourier approximation curves
- s-domain expression outputs and optional pole-zero plots
- Matrix transformation tables
- Equation interpretation table for augmented matrix mode

If you want an explicit pole-zero graph, generate it from the denominator roots of F(s) and include it as a supplemental figure.

### 4.5 Where to Put UI Screenshots
Store screenshots in these folders:
- front/screenshots/chapter4
- front/screenshots/chapter5

Recommended screenshot file names for Chapter 4:
- front/screenshots/chapter4/fig4_1_complex_ui.png
- front/screenshots/chapter4/fig4_2_linear_matrix_ui.png
- front/screenshots/chapter4/fig4_3_linear_augmented_ui.png
- front/screenshots/chapter4/fig4_4_fourier_result_ui.png
- front/screenshots/chapter4/fig4_5_laplace_result_ui.png

Recommended screenshot file names for Chapter 5:
- front/screenshots/chapter5/fig5_1_complex_analysis.png
- front/screenshots/chapter5/fig5_2_linear_error_cases.png
- front/screenshots/chapter5/fig5_3_fourier_n_comparison.png
- front/screenshots/chapter5/fig5_4_laplace_validation.png

Insert images right after each corresponding subsection using markdown image syntax:

    ![Figure 4.1 Complex Numbers UI](front/screenshots/chapter4/fig4_1_complex_ui.png)
    ![Figure 4.2 Linear Algebra UI](front/screenshots/chapter4/fig4_2_linear_matrix_ui.png)
    ![Figure 4.3 Augmented Matrix to Equation UI](front/screenshots/chapter4/fig4_3_linear_augmented_ui.png)
    ![Figure 4.4 Fourier Result UI](front/screenshots/chapter4/fig4_4_fourier_result_ui.png)
    ![Figure 4.5 Laplace Result UI](front/screenshots/chapter4/fig4_5_laplace_result_ui.png)

## Chapter 5 - Analysis

### 5.1 Purpose of Chapter 5
The Analysis section critically interprets the computational behavior of the system. The focus is on how the implemented algorithm logic meets project objectives and how outputs align with mathematical theory.

This chapter is not about hardware control. It is about algorithmic execution quality, symbolic-to-numeric transitions, and correctness verification of machine-based solutions.

### 5.2 Critical Technical Analysis per Module

#### 5.2.1 Complex Numbers Module
- Parsing pipeline normalizes user expressions and safely evaluates math content.
- The result is decomposed into real/imaginary parts and converted to magnitude-phase form.
- Error handling for invalid input and division by zero improves user reliability.

#### 5.2.2 Linear Algebra Module
- Matrix operation mode supports standard algebra operators and catches dimension errors.
- New v3 solve mode supports augmented matrix interpretation and direct variable solving.
- This reduces setup friction in classroom demonstrations and practical exercises.

#### 5.2.3 System of Linear Equation Logic
- Solver uses symbolic linear system solving.
- Supports underdetermined and overdetermined structures where mathematically solvable.
- Returns exact symbolic forms when numeric reduction is not ideal.

#### 5.2.4 Fourier Series Module
- Piecewise function parser builds symbolic Piecewise model.
- Coefficients are generated by integration and then expanded by harmonic index N.
- Iterative summation structure directly reflects Fourier theorem implementation.

#### 5.2.5 Laplace Module
- Uses direct symbolic transform and inverse transform operators.
- Simplification stage improves readability and comparison with textbook forms.
- Supports quick validation of transform identity pairs.

### 5.3 Integrity and Verification Discussion
Recommended Chapter 5 checks:
1. Run known textbook examples with closed-form solutions.
2. Confirm machine output matches theoretical benchmark.
3. Document all mismatches and classify cause:
   - floating-point precision
   - symbolic simplification form difference
   - user input formatting issue
4. For Fourier, compare N=5, N=10, N=20 against the same original signal.
5. For linear systems, test:
   - unique solution
   - no solution
   - infinite solution

### 5.4 Chapter 5 Conclusion Template
The ECETHON computational pipeline demonstrates that advanced mathematics can be reliably implemented through symbolic and numeric programming methods. Across complex arithmetic, matrix algebra, linear system solving, Fourier approximation, and Laplace transformation, the system shows consistent agreement with theoretical references. Residual numeric differences are within expected computational tolerance and do not affect engineering interpretation.

## Exact Algorithm Code Snippets

The snippets below are copied from the implementation file:
- ECETHON.py

### A. Shared numeric parser (Complex, Linear, Fourier, Laplace inputs)
Source: ECETHON.py line region around _parse_num

    def _parse_num(raw):
        """Parse a numeric expression string to Python complex.

        Accepts: integers, floats, fractions (1/2), exponents (2**3 or 2^3),
        complex numbers (3+2i, 3+2j, 3+2*I), constants (pi, e),
        and functions (sqrt, sin, cos, exp, log, abs, …).
        """
        s = _normalize(raw) or '0'                                 # clean the string; default to '0' if blank
        val = sp.sympify(s, locals=_SAFE_LOCALS, evaluate=True)    # parse into a SymPy expression using the safe whitelist
        return complex(val.evalf())                                # evaluate to a numeric value and return as Python complex

### B. Complex Numbers computation
Source: ECETHON.py line region around ComplexPage._calc

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

### C. Linear Algebra matrix operations
Source: ECETHON.py line region around LinearPage._calc

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

### D. System of Linear Equation from augmented matrix (v3)
Source: ECETHON.py line region around LinearPage._equation_from_row and _solve_from_matrices

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

### E. Fourier Series algorithm
Source: ECETHON.py line region around FourierPage._calc

    def _calc(self):
        if not self._pieces:
            return

        x_sym = sp.Symbol("x")
        n_sym = self._n_sym

        try:
            N = int(self.nterms_var.get())
        except Exception:
            N = 10

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

### F. Laplace and inverse Laplace algorithm
Source: ECETHON.py line region around LaplacePage._calc

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
