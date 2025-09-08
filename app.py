import streamlit as st
import pandas as pd
import numpy as np
import fitz  # PyMuPDF
from fpdf import FPDF
from PIL import Image
import io
import os

st.set_page_config(
    page_title="FinFET Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Dark Theme & Styling ---------------- #
dark_bg_color = "#2b2b2b"
light_text_color = "#e0e0e0"
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-color: {dark_bg_color};
        color: {light_text_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {dark_bg_color};
        color: {light_text_color};
    }}
    .stButton>button {{
        background-color: #4B4B4B;
        color: {light_text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Sidebar ---------------- #
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_column_width=True)
mode = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Local PDF"])

# ---------------- Local PDF Options ---------------- #
pdf_options = { 
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ---------------- Functions ---------------- #
def extract_text_from_pdf(pdf_path):
    """Extract full text from a local PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return ""

def simulate_parameters():
    """Generate synthetic demo FinFET parameters"""
    data = {
        "Lg (nm)": [3, 4, 5],
        "Hfin (nm)": [6, 7, 8],
        "EOT (nm)": [0.8, 0.85, 0.9],
        "Vth (V)": [0.3, 0.32, 0.35],
        "ID_max (A/cm2)": [0.8, 0.85, 0.9],
        "Ion/Ioff": [5e4, 4.5e4, 4e4],
        "gm (mS/μm)": [2.1, 2.0, 1.9],
        "Rsd (Ω)": [150, 160, 170],
        "Capacitance (fF/μm)": [1.2, 1.3, 1.4],
        "Delay (ps)": [12, 13, 14]
    }
    df = pd.DataFrame(data)
    df["Vg (V)"] = [np.linspace(0,1,10) for _ in range(len(df))]
    df["ID vs Vg (A/cm2)"] = [np.linspace(0, ID, 10) for ID in df["ID_max (A/cm2)"]]
    return df

def export_pdf(df, logo_path="logo.png"):
    """Export DataFrame as PDF with optional logo"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    try:
        pdf.image(logo_path, x=10, y=8, w=40)
    except Exception as e:
        st.warning(f"Logo not embedded: {e}")
    pdf.ln(20)
    pdf.cell(0, 10, "FinFET Parameters", ln=True)
    pdf.set_font("Arial", "", 12)
    for col in df.columns:
        pdf.cell(0, 10, f"{col}: {df[col].tolist()}", ln=True)
    return pdf.output(dest="S").encode("latin1")

# ---------------- Main ---------------- #
if mode == "Synthetic Demo":
    st.title("Synthetic FinFET Demo Data")
    df = simulate_parameters()
    st.dataframe(df.drop(columns=["Vg (V)", "ID vs Vg (A/cm2)"]), use_container_width=True)

    st.subheader("Scaling Plots")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for i in range(len(df)):
        ax.plot(df["Vg (V)"][i], df["ID vs Vg (A/cm2)"][i], marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.legend()
    st.pyplot(fig)

    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode('utf-8'), "synthetic_finfet.csv")
    st.download_button("⬇️ Download Excel", df.to_excel(index=False, engine='openpyxl'), "synthetic_finfet.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

elif mode == "Local PDF":
    st.title("Select a Local PDF")
    pdf_choice = st.selectbox("Select PDF", list(pdf_options.keys()))
    pdf_path = pdf_options[pdf_choice]

    if os.path.exists(pdf_path):
        text = extract_text_from_pdf(pdf_path)
        st.subheader("Extracted Text from PDF")
        st.text_area("PDF Content", text, height=300)

        # Currently using synthetic parameter extraction
        df = simulate_parameters()
        st.subheader("Extracted Parameters")
        st.dataframe(df.drop(columns=["Vg (V)", "ID vs Vg (A/cm2)"]), use_container_width=True)

        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode('utf-8'), "finfet_params.csv")
        st.download_button("⬇️ Download Excel", df.to_excel(index=False, engine='openpyxl'), "finfet_params.xlsx")
        st.download_button("⬇️ Download PDF", export_pdf(df), "finfet_params.pdf")
    else:
        st.error(f"PDF file not found: {pdf_path}")

# ---------------- Debug Log ---------------- #
st.sidebar.subheader("Debug Log")
st.sidebar.text(f"Mode: {mode}")
if mode == "Local PDF":
    st.sidebar.text(f"Selected PDF: {pdf_choice}")
