import streamlit as st
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw
import io
import numpy as np
import matplotlib.pyplot as plt
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔬", layout="wide")

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Synthetic Demo"])

# ----------------------------
# CSS Styles
# ----------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #2a2a2a;
        color: #e0e0e0;
    }
    .css-18e3th9 {
        background-color: #222222;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        border-radius: 10px;
        font-size: 16px;
        padding: 0.5em 1.5em;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Header with gradient
# ----------------------------
st.markdown("""
    <h1 style='background: linear-gradient(to right, #4CAF50, #45a049);
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;
               font-weight: bold;'>FinFET Data Extractor</h1>
    <p>Upload PDF/Image → OCR → Extract Parameters</p>
""", unsafe_allow_html=True)

# ----------------------------
# Logo
# ----------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=150)
except:
    st.warning("Logo not found. Place logo.png in app folder.")

# ----------------------------
# Utility: Export PDF
# ----------------------------
def export_pdf(df, logo_path="logo.png"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Add logo
    try:
        pdf.image(logo_path, 10, 8, 33)
    except:
        pass

    # ASCII-safe title
    title_safe = "Synthetic FinFET Parameters (3-5 nm)"
    pdf.cell(200, 10, title_safe, ln=True, align="C")
    pdf.ln(20)

    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)

    # Header
    for col in df.columns:
        safe_col = col.encode("latin1", "replace").decode("latin1")
        pdf.cell(col_width, 10, safe_col, border=1)
    pdf.ln()

    # Rows
    for _, row in df.iterrows():
        for val in row:
            safe_val = str(val).encode("latin1", "replace").decode("latin1")
            pdf.cell(col_width, 10, safe_val, border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin1")

# ----------------------------
# Synthetic Demo Function
# ----------------------------

def show_synthetic_demo():
    # Example 3–5 nm FinFET parameters
    data = {
        "Lg (nm)": [3, 4, 5],
        "Hfin (nm)": [25, 28, 30],
        "EOT (nm)": [0.7, 0.75, 0.8],
        "ID (A/cm2)": [1.2e5, 1.5e5, 1.8e5],
        "Vth (V)": [0.25, 0.26, 0.27],
        "Ion/Ioff": [1.2e6, 1.3e6, 1.5e6],
        "gm (mS/µm)": [1.1, 1.2, 1.3],
        "Rsd (Ω·µm)": [150, 140, 130],
        "Cgg (fF/µm)": [2.5, 2.6, 2.7],
        "Delay (ps)": [12, 11.5, 11],
        "Vg (V)": [np.linspace(0, 1, 50) for _ in range(3)]  # gate voltage sweep
    }
    df = pd.DataFrame({k: v if not isinstance(v, list) else v[0] for k, v in data.items()})
    st.subheader("Synthetic FinFET Parameters")
    st.dataframe(df, use_container_width=True)

    # ----------------------
    # Scaling Plots
    # ----------------------
    st.subheader("Scaling Plots")

    fig1, ax1 = plt.subplots()
    for i, row in df.iterrows():
        ax1.plot(data["Vg"][i], np.linspace(0, row["ID"], 50), label=f"Lg={row['Lg (nm)']} nm")
    ax1.set_xlabel("Vg (V)")
    ax1.set_ylabel("Id (A/cm²)")
    ax1.set_title("Ids–Vg Curves")
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    # Example: Ion/Ioff vs Lg
    fig2, ax2 = plt.subplots()
    ax2.plot(df["Lg (nm)"], df["Ion/Ioff"], marker='o')
    ax2.set_xlabel("Lg (nm)")
    ax2.set_ylabel("Ion/Ioff")
    ax2.set_title("Ion/Ioff vs Gate Length")
    ax2.grid(True)
    st.pyplot(fig2)

    # ----------------------
    # Download options
    # ----------------------
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    excel_bytes = excel_buffer.getvalue()
    pdf_bytes = export_pdf(df)

    col1, col2, col3 = st.columns(3)
    col1.download_button("Download CSV", csv_bytes, file_name="synthetic_finfet.csv")
    col2.download_button("Download Excel", excel_bytes, file_name="synthetic_finfet.xlsx")
    col3.download_button("Download PDF", pdf_bytes, file_name="synthetic_finfet.pdf")


# ----------------------------
# Main App
# ----------------------------
if page == "Home":
    st.info("Upload a PDF or image to extract FinFET parameters (OCR not implemented in this demo).")
    st.warning("Use 'Synthetic Demo' for full functional demo.")

elif page == "Synthetic Demo":
    try:
        show_synthetic_demo()
    except Exception as e:
        st.error(f"Error in synthetic demo: {e}")
