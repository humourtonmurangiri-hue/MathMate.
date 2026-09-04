import streamlit as st
import math
import statistics
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
st.set_page_config(page_title="MathMate", page_icon="📚", layout="centered")

st.title("📚 MATHMATE - Mathematics Tutor")
st.write("Your online assistant for Algebra, Calculus, Matrices, Statistics, and Plotting!")

# Setup variables & functions
x, y = sp.symbols('x y')

def M(elements): return sp.Matrix(elements)
def mean(data): return statistics.mean(data)
def median(data): return statistics.median(data)
def stdev(data): return statistics.stdev(data)
def nCr(n, r): return math.comb(n, r)
def nPr(n, r): return math.perm(n, r)

math_namespace = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'pi': math.pi, 'e': math.e, 'factorial': math.factorial,
    'mean': mean, 'median': median, 'stdev': stdev, 'nCr': nCr, 'nPr': nPr,
    'M': M, 'Matrix': M, 'x': x, 'y': y
}

# User input field
query = st.text_input("Enter a problem, equation, or command:", placeholder="e.g. 2*x + 5 = 15 or plot(x**2)")

if query:
    # Graph Plotting
    if "plot(" in query:
        try:
            expr_str = query.replace("plot(", "").rstrip(")")
            expr = sp.sympify(expr_str)
            f = sp.lambdify(x, expr, "numpy")
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x_vals, y_vals, label=f"y = {expr}", color="blue")
            ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
            ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error plotting graph: {e}")

    # Equation Solving
    elif "=" in query:
        try:
            left_str, right_str = query.split("=")
            left_expr = sp.sympify(left_str)
            right_expr = sp.sympify(right_str)
            sol = sp.solve(sp.Eq(left_expr, right_expr), x)
            
            st.subheader("Solution:")
            st.write(f"**Standard Form:** {sp.simplify(left_expr - right_expr)} = 0")
            st.success(f"**x = {sol}**")
        except Exception as e:
            st.error("Couldn't solve equation. Ensure you use '*' for multiplication.")

    # General Calculations / Stats / Matrices
    else:
        try:
            result = eval(query, {"__builtins__": None}, math_namespace)
            st.subheader("Answer:")
            st.write(result)
        except Exception as e:
            st.error("Invalid expression. Try entering something like 'sqrt(144)' or 'mean([10, 20, 30])'.")