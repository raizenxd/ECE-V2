import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


x = sp.symbols("x")
n = sp.symbols("n", integer=True, positive=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FourierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADMATHRIX - Fourier Series Solver")
        self.root.geometry("1250x720")
        self.root.minsize(1100, 650)

        self.build_ui()

    def build_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=230, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        title = ctk.CTkLabel(
            sidebar,
            text="AD MATHRIX",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=(30, 10))

        subtitle = ctk.CTkLabel(
            sidebar,
            text="Engineering Math Solver",
            font=("Arial", 13),
            text_color="#9ca3af"
        )
        subtitle.pack(pady=(0, 30))

        menu_items = [
            "Overview",
            "Linear Algebra",
            "Complex Numbers",
            "Fourier Series",
            "Laplace Transform",
            "About"
        ]

        for item in menu_items:
            color = "#2563eb" if item == "Fourier Series" else "transparent"

            btn = ctk.CTkButton(
                sidebar,
                text=item,
                height=42,
                corner_radius=12,
                fg_color=color,
                hover_color="#1d4ed8",
                anchor="w",
                font=("Arial", 14)
            )
            btn.pack(fill="x", padx=18, pady=6)

        # Main Area
        main = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#0f172a")
        main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=25, pady=(25, 10))

        ctk.CTkLabel(
            header,
            text="Fourier Series Analysis",
            font=("Arial", 30, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Python-Based Computational Tool for Fourier Series Analysis and Approximation of Non-Sinusoidal Waveforms",
            font=("Arial", 14),
            text_color="#94a3b8"
        ).pack(anchor="w", pady=(5, 0))

        # Input Card
        input_card = ctk.CTkFrame(main, corner_radius=22, fg_color="#111827")
        input_card.grid(row=1, column=0, sticky="nsew", padx=(25, 12), pady=15)

        ctk.CTkLabel(
            input_card,
            text="Input Function",
            font=("Arial", 21, "bold")
        ).pack(anchor="w", padx=22, pady=(22, 8))

        ctk.CTkLabel(
            input_card,
            text="Use SymPy format. Example below is a piecewise waveform. Piecewise((1, (x>=-pi)&(x<=0)), (0, (x>0)&(x<=pi)))",
            font=("Arial", 12),
            text_color="#9ca3af"
        ).pack(anchor="w", padx=22)

        self.function_box = ctk.CTkTextbox(
            input_card,
            height=100,
            corner_radius=14,
            font=("Consolas", 13),
            fg_color="#020617"
        )
        self.function_box.pack(fill="x", padx=22, pady=15)

        self.function_box.insert(
            "1.0",
            "Piecewise((1, (x>=-pi)&(x<=0)), (0, (x>0)&(x<=pi)))"
        )

        row = ctk.CTkFrame(input_card, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=5)

        self.lower_entry = self.entry_field(row, "Lower Limit", "-pi")
        self.upper_entry = self.entry_field(row, "Upper Limit", "pi")
        self.n_entry = self.entry_field(row, "Terms N", "10")

        solve_btn = ctk.CTkButton(
            input_card,
            text="SOLVE FOURIER SERIES",
            height=45,
            corner_radius=18,
            font=("Arial", 14, "bold"),
            fg_color="#2563eb",
            hover_color="#7c3aed",
            command=self.solve
        )
        solve_btn.pack(fill="x", padx=22, pady=(20, 12))

        clear_btn = ctk.CTkButton(
            input_card,
            text="CLEAR OUTPUT",
            height=38,
            corner_radius=15,
            font=("Arial", 13),
            fg_color="#334155",
            hover_color="#475569",
            command=self.clear_output
        )
        clear_btn.pack(fill="x", padx=22, pady=(0, 20))

        ctk.CTkLabel(
            input_card,
            text="Results",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=22, pady=(5, 5))

        self.output_box = ctk.CTkTextbox(
            input_card,
            height=210,
            corner_radius=15,
            font=("Consolas", 12),
            fg_color="#020617"
        )
        self.output_box.pack(fill="both", expand=True, padx=22, pady=(5, 22))

        # Graph Card
        graph_card = ctk.CTkFrame(main, corner_radius=22, fg_color="#111827")
        graph_card.grid(row=1, column=1, sticky="nsew", padx=(12, 25), pady=15)

        graph_header = ctk.CTkFrame(graph_card, fg_color="transparent")
        graph_header.pack(fill="x", padx=22, pady=(22, 10))

        ctk.CTkLabel(
            graph_header,
            text="Waveform Visualization",
            font=("Arial", 21, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            graph_header,
            text="Original function vs Fourier approximation",
            font=("Arial", 12),
            text_color="#9ca3af"
        ).pack(anchor="w")

        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.fig.patch.set_facecolor("#111827")
        self.ax.set_facecolor("#020617")

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=22, pady=22)

        self.default_graph()

    def entry_field(self, parent, label, default):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 12),
            text_color="#cbd5e1"
        ).pack(anchor="w")

        entry = ctk.CTkEntry(
            frame,
            height=38,
            corner_radius=12,
            font=("Arial", 13),
            fg_color="#020617"
        )
        entry.pack(fill="x", pady=(5, 0))
        entry.insert(0, default)

        return entry

    def default_graph(self):
        self.ax.clear()
        self.ax.set_title("Fourier Series Graph", color="white", fontsize=14)
        self.ax.set_xlabel("x", color="white")
        self.ax.set_ylabel("f(x)", color="white")
        self.ax.grid(True, alpha=0.25)
        self.ax.tick_params(colors="white")

        for spine in self.ax.spines.values():
            spine.set_color("#64748b")

        self.canvas.draw()

    def clear_output(self):
        self.output_box.delete("1.0", "end")
        self.default_graph()

    def solve(self):
        try:
            self.output_box.delete("1.0", "end")
            self.ax.clear()

            user_function = self.function_box.get("1.0", "end").strip()
            lower = self.lower_entry.get().strip()
            upper = self.upper_entry.get().strip()
            N = int(self.n_entry.get())

            local_dict = {
                "x": x,
                "pi": sp.pi,
                "sin": sp.sin,
                "cos": sp.cos,
                "tan": sp.tan,
                "exp": sp.exp,
                "sqrt": sp.sqrt,
                "Piecewise": sp.Piecewise
            }

            f = sp.sympify(user_function, locals=local_dict)
            a = sp.sympify(lower, locals=local_dict)
            b = sp.sympify(upper, locals=local_dict)

            L = (b - a) / 2

            a0 = (1 / (2 * L)) * sp.integrate(f, (x, a, b))

            an = (1 / L) * sp.integrate(
                f * sp.cos(n * sp.pi * x / L),
                (x, a, b)
            )

            bn = (1 / L) * sp.integrate(
                f * sp.sin(n * sp.pi * x / L),
                (x, a, b)
            )

            series = a0

            for k in range(1, N + 1):
                ak = an.subs(n, k)
                bk = bn.subs(n, k)

                series += ak * sp.cos(k * sp.pi * x / L)
                series += bk * sp.sin(k * sp.pi * x / L)

            series = sp.simplify(series)

            self.output_box.insert("end", "FOURIER COEFFICIENTS\n")
            self.output_box.insert("end", "====================\n\n")
            self.output_box.insert("end", f"a₀ = {sp.simplify(a0)}\n\n")
            self.output_box.insert("end", f"aₙ = {sp.simplify(an)}\n\n")
            self.output_box.insert("end", f"bₙ = {sp.simplify(bn)}\n\n")
            self.output_box.insert("end", "FINAL FOURIER SERIES\n")
            self.output_box.insert("end", "====================\n\n")
            self.output_box.insert("end", str(series))

            f_lamb = sp.lambdify(x, f, "numpy")
            series_lamb = sp.lambdify(x, series, "numpy")

            x_vals = np.linspace(float(a.evalf()), float(b.evalf()), 1000)
            y_original = f_lamb(x_vals)
            y_series = series_lamb(x_vals)

            self.ax.plot(x_vals, y_original, label="Original Function", linewidth=2)
            self.ax.plot(x_vals, y_series, label=f"Fourier Approximation N={N}", linewidth=2)

            self.ax.axhline(0, linewidth=0.8)
            self.ax.axvline(0, linewidth=0.8)

            self.ax.set_facecolor("#020617")
            self.ax.set_title("Fourier Series Approximation", color="white", fontsize=14)
            self.ax.set_xlabel("x", color="white")
            self.ax.set_ylabel("f(x)", color="white")
            self.ax.tick_params(colors="white")
            self.ax.grid(True, alpha=0.25)

            for spine in self.ax.spines.values():
                spine.set_color("#64748b")

            legend = self.ax.legend()
            legend.get_frame().set_facecolor("#111827")
            legend.get_frame().set_edgecolor("#64748b")

            for text in legend.get_texts():
                text.set_color("white")

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = ctk.CTk()
    app = FourierApp(root)
    root.mainloop()