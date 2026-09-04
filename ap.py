import streamlit as st
import math
import statistics
import re
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import pytesseract
from PIL import Image
import os

# Import new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Page configuration
st.set_page_config(page_title="Yumat MathMate", page_icon="📚", layout="centered")

st.title("📚 YUMAT MATHMATE - Smart University Tutor")
st.write("Solve calculus, linear algebra, statistics, or upload full exam papers for complete solutions!")

# Setup symbolic variables
x, y, z, t = sp.symbols('x y z t')

def clean_input(text):
    text = re.sub(r'(\d)\s*([a-zA-Z\(])', r'\1*\2', text)
    text = text.replace('^', '**')
    return text

def process_question(text):
    text_clean = text.strip()
    
    if re.search(r'\b(plot|graph|draw)\b', text_clean, re.IGNORECASE):
        match = re.search(r'plot\((.*?)\)', text_clean, re.IGNORECASE)
        if match:
            return "plot", clean_input(match.group(1))
        expr_match = re.search(r'(?:plot|graph|draw)\s+(?:y\s*=\s*)?([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "plot", clean_input(expr_match.group(1).strip())

    if re.search(r'\b(differentiate|derivative|diff)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:differentiate|derivative\s+of|diff)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "derivative", clean_input(expr_match.group(1).strip())

    if re.search(r'\b(integrate|integral)\b', text_clean, re.IGNORECASE):
        expr_match = re.search(r'(?:integrate|integral\s+of)\s+([x0-9\+\-\*\/\^\(\)\s]+)', text_clean, re.IGNORECASE)
        if expr_match:
            return "integral", clean_input(expr_match.group(1).strip())

    if "=" in text_clean:
        eq_match = re.search(r'([x0-9\+\-\*\/\^\(\)\s]+=[x0-9\+\-\*\/\^\(\)\s]+)', text_clean)
        if eq_match:
            return "solve", clean_input(eq_match.group(1).strip())

    return "eval", clean_input(text_clean)

def execute_math(intent, extracted_expr):
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
            st.code(f"y = {sp.latex(expr)}", language="latex")
        except Exception as e:
            st.error(f"Could not plot expression: {e}")

    elif intent == "derivative":
        try:
            expr = sp.sympify(extracted_expr)
            diff_res = sp.diff(expr, x)
            
            st.subheader("Step-by-Step Solution")
            st.write("**1. Identify Target Function:**")
            st.latex(f"f(x) = {sp.latex(expr)}")
            st.write("**2. Apply Differentiation Rules:**")
            st.latex(f"\\frac{{d}}{{dx}} \\left( {sp.latex(expr)} \\right)")
            st.write("**3. Final Derivative Result:**")
            latex_out = f"\\frac{{d}}{{dx}}({sp.latex(expr)}) = {sp.latex(diff_res)}"
            st.latex(latex_out)
            st.code(latex_out, language="latex")
        except Exception as e:
            st.error(f"Could not calculate derivative: {e}")

    elif intent == "integral":
        try:
            expr = sp.sympify(extracted_expr)
            int_res = sp.integrate(expr, x)
            
            st.subheader("Step-by-Step Solution")
            st.write("**1. Identify Integrand:**")
            st.latex(f"f(x) = {sp.latex(expr)}")
            st.write("**2. Apply Integration Rules:**")
            st.latex(f"\\int \\left( {sp.latex(expr)} \\right) \\, dx")
            st.write("**3. Final Result (Indefinite Integral):**")
            latex_out = f"\\int ({sp.latex(expr)})\\,dx = {sp.latex(int_res)} + C"
            st.latex(latex_out)
            st.code(latex_out, language="latex")
        except Exception as e:
            st.error(f"Could not calculate integral: {e}")

    elif intent == "solve":
        try:
            left_str, right_str = extracted_expr.split("=")
            left_expr, right_expr = sp.sympify(left_str), sp.sympify(right_str)
            sol = sp.solve(sp.Eq(left_expr, right_expr), x)
            
            st.subheader("Solution")
            st.latex(f"{sp.latex(left_expr)} = {sp.latex(right_expr)}")
            st.success(f"**Roots / Solutions:** {sol}")
        except Exception as e:
            st.error(f"Couldn't parse equation: {e}")

    else:
        try:
            expr = sp.sympify(extracted_expr)
            st.subheader("Result")
            st.latex(sp.latex(expr))
        except Exception:
            st.error("Could not parse request. Ensure standard mathematical syntax.")

# Sidebar Navigation
mode = st.sidebar.radio("Select Tool:", [
    "💬 General Math & Natural Language", 
    "📄 Full Paper / Assignment Solver", 
    "📐 Linear Algebra (Matrices)", 
    "📊 Probability & Statistics"
])

# Tool 1: General Math Solver
if mode == "💬 General Math & Natural Language":
    st.markdown("**Quick Prompts:**")
    col1, col2, col3 = st.columns(3)
    
    prompt_choice = None
    if col1.button("Differentiate x^3 + 2x"):
        prompt_choice = "Differentiate x^3 + 2x"
    if col2.button("Integrate sin(x)*cos(x)"):
        prompt_choice = "Integrate sin(x)*cos(x)"
    if col3.button("Plot x^2 - 4"):
        prompt_choice = "Plot x^2 - 4"

    tab1, tab2 = st.tabs(["💬 Text Input", "📷 Upload Image"])
    
    with tab1:
        user_query = st.text_input("Ask a question:", value=prompt_choice if prompt_choice else "", placeholder="e.g. Differentiate x^3 - 5x + 2")
        if user_query:
            intent, extracted_expr = process_question(user_query)
            execute_math(intent, extracted_expr)

    with tab2:
        uploaded_file = st.file_uploader("Upload equation image:", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            try:
                extracted_text = pytesseract.image_to_string(image)
                st.write("**Extracted Text:**", f"`{extracted_text.strip()}`")
                if extracted_text.strip():
                    intent, extracted_expr = process_question(extracted_text)
                    execute_math(intent, extracted_expr)
            except Exception as e:
                st.error(f"OCR Error: {e}")

# Tool 2: Full Document / Paper Solver (AI Powered)
elif mode == "📄 Full Paper / Assignment Solver":
    st.subheader("📄 Upload Exam Paper or Assignment PDF/Image")
    st.write("Upload a past paper or assignment image/PDF to get detailed solutions for all questions!")
    
    # Check for API key in secrets or sidebar input
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

    doc_file = st.file_uploader("Upload Paper (PDF, PNG, JPG):", type=["pdf", "png", "jpg", "jpeg"])
    
    if doc_file:
        if not api_key:
            st.warning("Please provide a Gemini API Key to enable AI document understanding.")
        else:
            if st.button("Solve Entire Paper"):
                with st.spinner("Analyzing document and solving questions step-by-step..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        bytes_data = doc_file.read()
                        mime_type = doc_file.type
                        
                        prompt = (
                            "You are Yumat MathMate, an expert university mathematics tutor. "
                            "Analyze this document carefully. Identify every mathematical question or problem. "
                            "For each question:\n"
                            "1. State the question clearly.\n"
                            "2. Provide a rigorous, step-by-step mathematical solution.\n"
                            "3. Use LaTeX formatting for all mathematical expressions and equations.\n"
                            "4. Highlight the final answer clearly."
                        )
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                types.Part.from_bytes(data=bytes_data, mime_type=mime_type),
                                prompt
                            ]
                        )
                        
                        st.markdown("### 📝 Complete Solutions & Explanations")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Error processing document: {e}")

# Tool 3: Linear Algebra Dedicated Suite
elif mode == "📐 Linear Algebra (Matrices)":
    st.subheader("Matrix Operations Suite")
    matrix_str = st.text_area("Enter Matrix rows (comma separated elements, new lines for rows):", "1, 2\n3, 4")
    
    try:
        rows = [[float(num) for num in row.split(",")] for row in matrix_str.strip().split("\n")]
        M = sp.Matrix(rows)
        st.write("**Input Matrix (A):**")
        st.latex(sp.latex(M))

        op = st.selectbox("Select Operation:", ["Determinant", "Inverse", "Eigenvalues & Eigenvectors", "Rank & Nullity", "Trace"])
        
        if st.button("Calculate"):
            if op == "Determinant":
                st.latex(f"|A| = {M.det()}")
            elif op == "Inverse":
                if M.det() == 0:
                    st.error("Matrix is singular (Determinant = 0); no inverse exists.")
                else:
                    st.latex(f"A^{{-1}} = {sp.latex(M.inv())}")
            elif op == "Eigenvalues & Eigenvectors":
                st.write("**Eigenvalues & Multiplicities:**", M.eigenvals())
                st.write("**Eigenvectors:**")
                for vect in M.eigenvects():
                    st.latex(f"\\lambda = {vect[0]} \\implies v = {sp.latex(vect[2][0])}")
            elif op == "Rank & Nullity":
                st.write(f"**Rank:** {M.rank()}")
                st.write(f"**Nullity:** {M.shape[1] - M.rank()}")
            elif op == "Trace":
                st.latex(f"\\text{{Trace}}(A) = {M.trace()}")
    except Exception as e:
        st.error(f"Matrix parsing error: {e}")

# Tool 4: Probability & Statistics
elif mode == "📊 Probability & Statistics":
    st.subheader("Statistical Distributions & Data Analysis")
    
    stat_tool = st.selectbox("Select Calculator:", ["Summary Statistics", "Normal Distribution (Z-Score)"])
    
    if stat_tool == "Summary Statistics":
        data_input = st.text_input("Enter numbers separated by commas:", "12, 15, 18, 22, 30")
        if data_input:
            try:
                data = [float(x.strip()) for x in data_input.split(",")]
                st.write(f"**Mean ($\mu$):** {statistics.mean(data):.4f}")
                st.write(f"**Median:** {statistics.median(data):.4f}")
                st.write(f"**Std Dev ($s$):** {statistics.stdev(data):.4f}")
            except Exception as e:
                st.error("Invalid dataset format.")

    elif stat_tool == "Normal Distribution (Z-Score)":
        x_val = st.number_input("Value (X):", value=75.0)
        mean_val = st.number_input("Mean (μ):", value=70.0)
        std_val = st.number_input("Std Dev (σ):", value=5.0, min_value=0.1)
        
        z_score = (x_val - mean_val) / std_val
        st.latex(f"Z = \\frac{{X - \\mu}}{{\\sigma}} = \\frac{{{x_val} - {mean_val}}}{{{std_val}}} = {z_score:.4f}")