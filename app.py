import streamlit as st
import easyocr
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from PIL import Image

# --- Sidebar ---
st.sidebar.title("FinFET Data Extractor")
st.sidebar.image("logo.png", use_column_width=True)

option = st.sidebar.radio("Choose mode", ("Synthetic Demo", "Upload PDF/Image"))

# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_parameters_from_text(text):
    # Placeholder function to extract parameters from text
    # Implement your parameter extraction logic here
    return {
        "Device": "Device 1",
        "Lg (nm)": 5,
        "Hfin (nm)": 10,
        "EOT (nm)": 1.2,
        "ID (A/cm2)": 1.2e-4,
        "Vth (V)": 0.28,
        "Ion/Ioff": 1e5,
        "Vg": np.linspace(0, 1.2, 10).tolist()
    }

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Extracted FinFET Data", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    col_width = pdf.w / (len(df.columns) + 1)
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- Main ---
if option == "Upload PDF/Image":
    st.title("Upload PDF or Image")
    uploaded_file = st.file_uploader("Choose a PDF or image...", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            image = Image.open(uploaded_file)
            reader = easyocr.Reader(["en"])
            result = reader.readtext(np.array(image))
            text = " ".join([res[1] for res in result])

        st.subheader("Extracted Text")
        st.text_area("Text from PDF/Image", text, height=300)

        # Extract parameters
        parameters = extract_parameters_from_text(text)
        df = pd.DataFrame([parameters])

        st.subheader("Extracted Parameters")
        st.dataframe(df)

        # Downloads
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "extracted_data.csv")
        st.download_button("Download PDF", export_pdf(df), "extracted_data.pdf")

else:
    st.title("Synthetic Demo")
    # Your synthetic demo code here
