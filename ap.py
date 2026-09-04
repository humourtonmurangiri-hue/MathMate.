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
st.write("Type full questions or commands—MathMate extracts and solves the math automatically!")

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

# Advanced Extractor & Intent Classifier
def process_question(text):
    text_clean = text.strip()
    
    # 1. Plotting Intent
    if re.search(r'\b(plot|graph|draw)\b', text_clean, re.IGNORECASE):
        # Extract expression inside plot(...) or after keywords
        match = re.search(r'plot\((.*?)\)', text_clean, re.IGNORECASE)
        if match:
            return "plot", match.group(1)
        # Extract equation or expression after keywords like "graph y =" or "plot x**2"
        expr_match = re.search(r'(?:plot|graph|draw)\s+(?:y\s*=\s*)?([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "plot", expr_match.group(1).strip()

    # 2. Calculus: Derivative Intent
    if re.search(r'\b(differentiate|derivative|find\s+d/dx)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:differentiate|derivative\s+of|d/dx)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "derivative", expr_match.group(1).strip()

    # 3. Calculus: Integral Intent
    if re.search(r'\b(integrate|integral)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:integrate|integral\s+of)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "integral", expr_match.group(1).strip()

    # 4. Equation Solving Intent (contains '=' or words like 'solve')
    if "=" in text_clean:
        # Extract full equation containing '='
        eq_match = re.search(r'([x0-9\+\-\*\/\^\(\)\s]+=[x0-9\+\-\*\/\^\(\)\s]+)', text_clean)
        if eq_match:
            return "solve", eq_match.group(1).strip()

    # 5. Direct Evaluation / Statistics
    return "eval", text_clean

# User Input
user_query = st.text_input(
    "Ask a question:", 
    placeholder="e.g. Can you solve 3*x + 10 = 25 for me? or Plot x**2 - 4"
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
            st.error(f"Could not plot: {e}")

    # Execution: Derivatives
    elif intent == "derivative":
        try:
            expr = sp.sympify(extracted_expr)
            diff_res = sp.diff(expr, x)
            st.subheader("Derivative Result:")
            st.write(f"$$\\frac{{d}}{{dx}}({sp.latex(expr)}) = {sp.latex(diff_res)}$$")
        except Exception as e:
            st.error("Could not calculate derivative.")

    # Execution: Integrals
    elif intent == "integral":
        try:
            expr = sp.sympify(extracted_expr)
            int_res = sp.integrate(expr, x)
            st.subheader("Integral Result:")
            st.write(f"$$\\int ({sp.latex(expr)})\\,dx = {sp.latex(int_res)} + C$$")
        except Exception as e:
            st.error("Could not calculate integral.")

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
            st.error("Couldn't parse equation. Ensure explicit multiplication like `3*x`.")

    # Execution: Fallback Evaluation
    else:
        try:
            result = eval(extracted_expr, {"__builtins__": None}, math_namespace)
            st.subheader("Answer:")
            st.write(result)
        except Exception:
            st.error("Could not parse request. Try rephrasing your question clearly.")