import re
import sympy as sp

s = sp.Symbol('s')

LAPLACE_PAIRS = {
    'delta': 1,
    'dirac': 1,
    'impulse': 1,
}

def parse_expression(expr_str):
    expr_str = expr_str.strip()
    expr_str = re.sub(r'\bu\s*\(\s*t\s*\)', '', expr_str)
    expr_str = re.sub(r'\*u\s*\(\s*t\s*\)', '', expr_str)
    expr_str = re.sub(r'u\s*\(\s*t\s*\)\s*\*', '', expr_str)
    expr_str = re.sub(r'\bdelta\s*\(\s*t\s*\)', '1', expr_str)
    expr_str = re.sub(r'\bdirac\s*\(\s*t\s*\)', '1', expr_str)
    expr_str = re.sub(r'\bimpulse\s*\(\s*t\s*\)', '1', expr_str)
    expr_str = re.sub(r'\bdelta\b', '1', expr_str)
    expr_str = re.sub(r'\bimpulse\b', '1', expr_str)
    expr_str = expr_str.strip()
    if not expr_str:
        expr_str = '0'
    return expr_str

def compute_laplace(time_expr_str):
    t = sp.Symbol('t', positive=True)
    s = sp.Symbol('s')

    # preprocess
    expr_str = time_expr_str.strip()
    expr_str = re.sub(r'\bu\s*\(\s*t\s*\)', '1', expr_str)
    expr_str = re.sub(r'\*\s*u\s*\(\s*t\s*\)', '', expr_str)
    expr_str = re.sub(r'u\s*\(\s*t\s*\)\s*\*', '', expr_str)
    expr_str = re.sub(r'\bdelta\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
    expr_str = re.sub(r'\bimpulse\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)
    expr_str = re.sub(r'\bdirac\s*\(\s*t\s*\)', 'DiracDelta(t)', expr_str)

    local_dict = {
        't': t, 's': s,
        'sin': sp.sin, 'cos': sp.cos,
        'exp': sp.exp, 'e': sp.E,
        'sqrt': sp.sqrt, 'pi': sp.pi,
        'DiracDelta': sp.DiracDelta,
    }

    expr = sp.sympify(expr_str, locals=local_dict)
    result = sp.laplace_transform(expr, t, s, noconds=True)
    result = sp.simplify(result)
    return result

def fraction_box(numerator, denominator, label=None):
    n_str = str(numerator)
    d_str = str(denominator)
    width = max(len(n_str), len(d_str)) + 2
    lines = []
    if label:
        lines.append(f"  {label}")
    lines.append(f"  {n_str.center(width)}")
    lines.append(f"  {'─' * width}")
    lines.append(f"  {d_str.center(width)}")
    return '\n'.join(lines)

def format_laplace_result(result):
    result = sp.simplify(result)
    result = sp.apart(result, s)

    terms = sp.Add.make_args(result)
    output_parts = []

    for term in terms:
        numer, denom = sp.fraction(term)
        numer = sp.expand(numer)
        denom = sp.expand(denom)

        if denom == 1:
            output_parts.append(('whole', str(numer), None))
        else:
            output_parts.append(('frac', str(numer), str(denom)))

    return output_parts

def render_output(parts):
    whole_terms = [p for p in parts if p[0] == 'whole']
    frac_terms  = [p for p in parts if p[0] == 'frac']

    lines_num = []
    lines_bar = []
    lines_den = []

    PAD = 3

    for i, p in enumerate(parts):
        if i == 0:
            sign = "   "
        else:
            raw = p[1] if p[0] == 'whole' else p[1]
            if raw.startswith('-'):
                sign = " - "
            else:
                sign = " + "

        if p[0] == 'whole':
            val = p[1].lstrip('-') if (i > 0 and p[1].startswith('-')) else p[1]
            w = len(sign) + len(val)
            lines_num.append(sign + val)
            lines_bar.append(' ' * w)
            lines_den.append(' ' * w)
        else:
            n_str = p[1]
            d_str = p[2]
            inner_w = max(len(n_str), len(d_str)) + PAD
            n_padded = n_str.center(inner_w)
            d_padded = d_str.center(inner_w)
            bar      = '─' * inner_w
            lines_num.append(sign + n_padded)
            lines_bar.append(' ' * len(sign) + bar)
            lines_den.append(' ' * len(sign) + d_padded)

    row1 = ''.join(lines_num).rstrip()
    row2 = ''.join(lines_bar).rstrip()
    row3 = ''.join(lines_den).rstrip()

    if row2.strip():
        return f"{row1}\n{row2}\n{row3}"
    else:
        return row1

def draw_box(text):
    lines = text.split('\n')
    width = max(len(l) for l in lines) + 4
    top    = '┌' + '─' * width + '┐'
    bottom = '└' + '─' * width + '┘'
    mid    = ['│  ' + l.ljust(width - 2) + '  │' for l in lines]
    return '\n'.join([top] + mid + [bottom])

def main():
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║       Laplace Transform Calculator               ║")
    print("╠══════════════════════════════════════════════════╣")
    print("║  Enter a time-domain expression f(t).            ║")
    print("║  u(t) is assumed — just write the signal.        ║")
    print("║  Examples:                                       ║")
    print("║    delta(t) + 7 - 6*exp(-5*t)                   ║")
    print("║    12*cos(2*t) + 3*sin(3*t)                     ║")
    print("║    t**3 + 3*exp(-t)                              ║")
    print("║  Type 'exit' to quit.                            ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    while True:
        try:
            user_input = input("  f(t) = ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if user_input.lower() in ('exit', 'quit', 'q'):
            print("  Goodbye!")
            break

        if not user_input:
            continue

        try:
            result = compute_laplace(user_input)
            parts  = format_laplace_result(result)
            rendered = render_output(parts)
            boxed = draw_box(rendered)

            print()
            print("  ─────────────────────────────────────────")
            print(f"  f(t)  =  {user_input}")
            print()
            print("  F(s)  =")
            print()
            for line in boxed.split('\n'):
                print("    " + line)
            print()

        except Exception as e:
            print(f"\n  [Error] Could not compute: {e}")
            print("  Check your input syntax and try again.\n")

if __name__ == '__main__':
    main()