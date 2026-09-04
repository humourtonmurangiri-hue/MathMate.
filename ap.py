import streamlit as st
import math
import statistics
import re
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

# Page configuration
st.set_page_config(page_title="Yumat MathMate", page_icon="📚", layout="centered")

st.title("📚 YUMAT MATHMATE - Smart Tutor")
st.write("Ask full conversational questions—Yumat MathMate extracts and solves the math automatically!")

# Setup variables & symbols
x, y, z = sp.symbols('x y z')

def M(elements): return sp.Matrix(elements)
def mean(data): return statistics.mean(data)
def median(data): return statistics.median(data)
def stdev(data): return statistics.stdev(data)

math_namespace = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'pi': math.pi, 'e': math.e, 'factorial': math.factorial,
    'mean': mean, 'median': median, 'stdev': stdev,
    'M': M, 'Matrix': M, 'x': x, 'y': y, 'z': z
}

def clean_input(text):
    """Normalize common math notation from natural language text."""
    # Convert implied multiplication like 3x or 3(x) to explicit math (3*x)
    text = re.sub(r'(\d)\s*([a-zA-Z\(])', r'\1*\2', text)
    # Convert exponents like x^2 to sympy format x**2
    text = text.replace('^', '**')
    return text

def process_question(text):
    text_clean = text.strip()
    
    # 1. Plotting Intent
    if re.search(r'\b(plot|graph|draw)\b', text_clean, re.IGNORECASE):
        match = re.search(r'plot\((.*?)\)', text_clean, re.IGNORECASE)
        if match:
            return "plot", clean_input(match.group(1))
        expr_match = re.search(r'(?:plot|graph|draw)\s+(?:y\s*=\s*)?([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "plot", clean_input(expr_match.group(1).strip())

    # 2. Calculus: Derivative Intent
    if re.search(r'\b(differentiate|derivative|find\s+d/dx|diff)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:differentiate|derivative\s+of|d/dx|diff)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "derivative", clean_input(expr_match.group(1).strip())

    # 3. Calculus: Integral Intent
    if re.search(r'\b(integrate|integral)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:integrate|integral\s+of)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "integral", clean_input(expr_match.group(1).strip())

    # 4. Equation Solving Intent
    if "=" in text_clean:
        eq_match = re.search(r'([x0-9\+\-\*\/\^\(\)\s]+=[x0-9\+\-\*\/\^\(\)\s]+)', text_clean)
        if eq_match:
            return "solve", clean_input(eq_match.group(1).strip())

    # 5. Direct Evaluation / Statistics
    return "eval", clean_input(text_clean)

# User Input
user_query = st.text_input(
    "Ask a question:", 
    placeholder="e.g. Can you solve 3x + 10 = 25 for me? or Plot x^2 - 4"
)

if user_query:
    intent, extracted_expr = process_question(user_query)
    
    # Execution: Plotting
    if intent == "plot":
        try:
            expr = sp.sympify(extracted_expr)
            f = sp.lambdify(x, expr, "numpy")
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(x_vals, y_vals, label=f"y = {expr}", color="#1f77b4")
            ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
            ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.legend()
            st.pyplot(fig)
            st.info(f"Extracted expression: `{extracted_expr}`")
        except Exception as e:
            st.error(f"Could not plot expression: {e}")

    # Execution: Derivatives
    elif intent == "derivative":
        try:
            expr = sp.sympify(extracted_expr)
            diff_res = sp.diff(expr, x)
            st.subheader("Derivative Result:")
            st.write(f"$$\\frac{{d}}{{dx}}({sp.latex(expr)}) = {sp.latex(diff_res)}$$")
            st.info(f"Extracted expression: `{extracted_expr}`")
        except Exception as e:
            st.error(f"Could not calculate derivative: {e}")

    # Execution: Integrals
    elif intent == "integral":
        try:
            expr = sp.sympify(extracted_expr)
            int_res = sp.integrate(expr, x)
            st.subheader("Integral Result:")
            st.write(f"$$\\int ({sp.latex(expr)})\\,dx = {sp.latex(int_res)} + C$$")
            st.info(f"Extracted expression: `{extracted_expr}`")
        except Exception as e:
            st.error(f"Could not calculate integral: {e}")

    # Execution: Equation Solving
    elif intent == "solve":
        try:
            left_str, right_str = extracted_expr.split("=")
            left_expr = sp.sympify(left_str)
            right_expr = sp.sympify(right_str)
            sol = sp.solve(sp.Eq(left_expr, right_expr), x)
            
            st.subheader("Solution:")
            st.success(f"**x = {sol}**")
            st.caption(f"Filtered equation: `{extracted_expr}`")
        except Exception as e:
            st.error(f"Couldn't parse equation: {e}")

    # Execution: Fallback Evaluation
    else:
        try:
            result = eval(extracted_expr, {"__builtins__": None}, math_namespace)
            st.subheader("Answer:")
            st.write(result)
        except Exception:
            st.error("Could not parse request. Try rephrasing your question clearly.")