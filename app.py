import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image
import numpy as np
import qrcode
import base64

# --- CONFIG ---
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
BACKGROUND_COLOR = "#1E1E2F"   # slightly lighter than pure dark
TEXT_COLOR = "#F5F5F5"

# --- UTILITY: automatic text color based on background brightness ---
def get_contrasting_text_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r*299 + g*587 + b*114) / 1000
    return "#000000" if brightness > 160 else "#FFFFFF"

# --- STYLE ---
st.markdown(
    f"""
    <style>
        body {{
            background-color: {BACKGROUND_COLOR};
            color: {get_contrasting_text_color(BACKGROUND_COLOR)};
        }}
        .stButton>button {{
            background: linear-gradient(90deg, #4b6cb7, #182848);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
        }}
        .stSidebar {{
            background-color: #2A2A3D;
            color: white;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Choose mode:", ["Upload PDF", "Synthetic Demo"])
st.sidebar.info("This demo extracts FinFET parameters using OCR + NLP.")

# --- OCR Reader ---
reader = easyocr.Reader(['en'])

# --- MAIN HEADER ---
st.markdown("<h1 style='text-align:center;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
st.write("---")

# --- DATA EXTRACTION FUNCTION ---
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def synthetic_parameters():
    # fake FinFET parameters
    return pd.DataFrame([
        {"Lg (nm)": 14, "Hfin (nm)": 30, "EOT (nm)": 0.9, "Idsat (µA/µm)": 1100},
        {"Lg (nm)": 10, "Hfin (nm)": 40, "EOT (nm)": 0.7, "Idsat (µA/µm)": 1500}
    ])

# --- OUTPUT EXPORTS ---
def export_to_excel(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def export_to_csv(df):
    return df.to_csv(index=False).encode()

def export_to_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    # Add logo
    try:
        logo = RLImage("logo.png", width=1.5*inch, height=1.5*inch)
        elems.append(logo)
        elems.append(Spacer(1, 0.2*inch))
    except:
        pass

    elems.append(Paragraph("Extracted FinFET Parameters", styles["Heading1"]))
    elems.append(Spacer(1, 0.2*inch))

    for col in df.columns:
        for val in df[col]:
            elems.append(Paragraph(f"<b>{col}</b>: {val}", styles["Normal"]))
        elems.append(Spacer(1, 0.1*inch))

    doc.build(elems)
    pdf_data = buf.getvalue()
    buf.close()
    return pdf_data

# --- MAIN APP LOGIC ---
if mode == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            st.subheader("Extracted Text Preview")
            st.text_area("Text", text, height=200)

            # Dummy extracted parameters (replace with NLP parsing logic)
            df = synthetic_parameters()
            st.subheader("Extracted Parameters")
            st.dataframe(df)

            # Download buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Download as Excel", export_to_excel(df), "parameters.xlsx")
            with col2:
                st.download_button("Download as CSV", export_to_csv(df), "parameters.csv")
            with col3:
                st.download_button("Download as PDF", export_to_pdf(df), "parameters.pdf", mime="application/pdf")

        except Exception as e:
            st.error("Error while processing PDF.")
            st.exception(e)

elif mode == "Synthetic Demo":
    st.subheader("Synthetic FinFET Data")
    df = synthetic_parameters()
    st.dataframe(df)
    st.download_button("Download as Excel", export_to_excel(df), "synthetic.xlsx")
    st.download_button("Download as CSV", export_to_csv(df), "synthetic.csv")
    st.download_button("Download as PDF", export_to_pdf(df), "synthetic.pdf", mime="application/pdf")
