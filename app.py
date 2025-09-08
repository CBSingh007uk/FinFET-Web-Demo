import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import requests
import fitz  # PyMuPDF
from fpdf import FPDF
from PIL import Image

# ------------------------
# App Config
# ------------------------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide", initial_sidebar_state="expanded")

# Dark theme colors
BACKGROUND_COLOR = "#1e1e1e"
TEXT_COLOR = "#d4d4d4"
BUTTON_COLOR = "#3a3a3a"
BUTTON_TEXT_COLOR = "#ffffff"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    .stButton>button {{
        background-color: {BUTTON_COLOR};
        color: {BUTTON_TEXT_COLOR};
    }}
    .sidebar .sidebar-content {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# Logo
# ------------------------
try:
    logo_img = Image.open("logo.png")  # put your logo.png in same folder
    st.sidebar.image(logo_img, use_column_width=True)
except:
    st.sidebar.write("Logo not found")

# ------------------------
# GitHub PDF links
# ------------------------
github_pdfs = {
    "1905.11207v3.pdf": "https://raw.githubusercontent.com/CBSingh007uk/FinFET-Web-Demo/pdfs/1905.11207v3.pdf",
    "2007.13168v4.pdf": "https://raw.githubusercontent.com/CBSingh007uk/FinFET-Web-Demo/pdfs/2007.13168v4.pdf",
    "2007.14448v1.pdf": "https://raw.githubusercontent.com/CBSingh007uk/FinFET-Web-Demo/pdfs/2007.14448v1.pdf",
    "2407.18187v1.pdf": "https://raw.githubusercontent.com/CBSingh007uk/FinFET-Web-Demo/pdfs/2407.18187v1.pdf",
    "2501.15190v1.pdf": "https://raw.githubusercontent.com/CBSingh007uk/FinFET-Web-Demo/pdfs/2501.15190v1.pdf"
}

# ------------------------
# Functions
# ------------------------
def extract_text_from_pdf(pdf_stream):
    try:
        pdf_stream.seek(0)
        doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return ""

def parse_parameters(text):
    """
    For now, return synthetic demo data.
    """
    param_dict = {
        "Lg (nm)": [3],
        "Hfin (nm)": [6],
        "EOT (nm)": [0.8],
        "Vth (V)": [0.3],
        "ID_max (A/cm2)": [0.8],
        "Ion/Ioff": [5e4],
        "gm (mS/μm)": [1.2],
        "Rs_d (Ω·μm)": [50],
        "Capacitance (fF/μm)": [0.5],
        "Delay (ps)": [10],
        "Vg": [np.linspace(0, 1.2, 10)],
        "ID vs Vg (A/cm2)": [np.linspace(0, 0.8, 10)]
    }
    return pd.DataFrame(param_dict)

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FinFET Parameters", ln=True, align="C")
    pdf.ln(5)
    # add table
    pdf.set_font("Arial", "", 12)
    for i in df.index:
        row_text = " | ".join([f"{col}: {df[col][i]}" for col in df.columns if col not in ["Vg","ID vs Vg (A/cm2)"]])
        pdf.multi_cell(0, 8, row_text)
    # embed logo
    try:
        pdf.image("logo.png", x=160, y=10, w=30)
    except:
        pass
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# ------------------------
# Sidebar Options
# ------------------------
mode = st.sidebar.selectbox("Select Mode", ["Synthetic Demo", "Upload PDF", "Choose PDF from Repository"])

st.sidebar.markdown("---")
log_sidebar = st.sidebar.empty()

# ------------------------
# Synthetic Demo
# ------------------------
if mode == "Synthetic Demo":
    st.header("Synthetic FinFET Demo Data")
    df = parse_parameters("synthetic")
    # Safe drop
    columns_to_drop = [c for c in ["Vg", "ID vs Vg (A/cm2)"] if c in df.columns]
    st.dataframe(df.drop(columns=columns_to_drop), use_container_width=True)

    # Scaling plot
    if "Vg" in df.columns and "ID vs Vg (A/cm2)" in df.columns:
        fig, ax = plt.subplots()
        for i in df.index:
            ax.plot(df["Vg"][i], df["ID vs Vg (A/cm2)"][i], marker='o', label=f"Device {i+1}")
        ax.set_xlabel("Vg (V)")
        ax.set_ylabel("ID (A/cm2)")
        ax.set_title("ID vs Vg Scaling Plot")
        ax.legend()
        st.pyplot(fig)

    # Download buttons
    csv_bytes = df.to_csv(index=False).encode()
    excel_bytes = BytesIO()
    df.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    st.download_button("⬇️ Download CSV", csv_bytes, "finfet_demo.csv")
    st.download_button("⬇️ Download Excel", excel_bytes, "finfet_demo.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df), "finfet_demo.pdf")

# ------------------------
# Upload PDF
# ------------------------
elif mode == "Upload PDF":
    st.header("Upload PDF/Image")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file:
        pdf_bytes = BytesIO(uploaded_file.read())
        text = extract_text_from_pdf(pdf_bytes)
        st.subheader("Extracted Text")
        st.text_area("PDF Content", text, height=300)
        df = parse_parameters(text)
        columns_to_drop = [c for c in ["Vg", "ID vs Vg (A/cm2)"] if c in df.columns]
        st.dataframe(df.drop(columns=columns_to_drop), use_container_width=True)
        log_sidebar.text_area("Log", f"Extracted {len(df)} rows", height=100)

# ------------------------
# Choose PDF from GitHub Repository
# ------------------------
elif mode == "Choose PDF from Repository":
    st.header("Choose PDF from Repository")
    selected_pdf = st.selectbox("Select PDF", list(github_pdfs.keys()))
    if selected_pdf:
        r = requests.get(github_pdfs[selected_pdf])
        if r.status_code == 200:
            pdf_bytes = BytesIO(r.content)
            text = extract_text_from_pdf(pdf_bytes)
            st.subheader("Extracted Text")
            st.text_area("PDF Content", text, height=300)
            df = parse_parameters(text)
            columns_to_drop = [c for c in ["Vg", "ID vs Vg (A/cm2)"] if c in df.columns]
            st.dataframe(df.drop(columns=columns_to_drop), use_container_width=True)
            log_sidebar.text_area("Log", f"Extracted {len(df)} rows from {selected_pdf}", height=100)
        else:
            st.error("Failed to download PDF from GitHub.")
