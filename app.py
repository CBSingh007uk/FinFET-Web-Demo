import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import io
from fpdf import FPDF
from PIL import Image

# ------------------------
# Helper: extract text from PDF
# ------------------------
def extract_text_from_pdf(path_or_file):
    try:
        if isinstance(path_or_file, str):  # local file path
            doc = fitz.open(path_or_file)
        else:  # uploaded file (BytesIO)
            doc = fitz.open(stream=path_or_file.read(), filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error extracting PDF: {e}"

# ------------------------
# Helper: extract parameters using regex
# ------------------------
def extract_parameters(text):
    params = {}
    try:
        params['Lg (nm)'] = float(re.search(r"Lg\s*=?\s*(\d+\.?\d*)nm", text).group(1))
    except: pass
    try:
        params['Hfin (nm)'] = float(re.search(r"Hfin\s*=?\s*(\d+\.?\d*)nm", text).group(1))
    except: pass
    try:
        params['EOT (nm)'] = float(re.search(r"EOT\s*=?\s*(\d+\.?\d*)nm", text).group(1))
    except: pass
    try:
        params['Vth (V)'] = float(re.search(r"Vth\s*=?\s*(\d+\.?\d*)V", text).group(1))
    except: pass
    try:
        params['ID (A/cm2)'] = float(re.search(r"ID_max\s*=?\s*(\d+\.?\d*)A/cm2", text).group(1))
    except: pass
    try:
        params['Ion/Ioff'] = re.search(r"Ion/Ioff\s*=?\s*([\deE\+\-\.]+)", text).group(1)
    except: pass

    return pd.DataFrame([params]) if params else pd.DataFrame()

# ------------------------
# Helper: export PDF with logo + table
# ------------------------
def export_pdf(df, logo_path="logo.png"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add logo if exists
    try:
        pdf.image(logo_path, x=10, y=8, w=40)
    except:
        pass

    pdf.ln(30)
    pdf.cell(200, 10, txt="Extracted FinFET Parameters", ln=True, align="C")

    pdf.ln(10)
    for col in df.columns:
        pdf.cell(60, 10, col, border=1)
    pdf.ln()
    for _, row in df.iterrows():
        for col in df.columns:
            pdf.cell(60, 10, str(row[col]), border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# ------------------------
# Sidebar setup
# ------------------------
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("📂 FinFET Data Extractor")

mode = st.sidebar.radio("Choose Mode:", ["Synthetic Demo", "Select PDF", "Upload PDF"])

pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf",
}

# ------------------------
# Main App Logic
# ------------------------
st.title("📊 FinFET Data Extraction App")

df = pd.DataFrame()

if mode == "Synthetic Demo":
    st.subheader("Synthetic FinFET Demo Data")
    text = "Lg=3nm, Hfin=6nm, EOT=0.8nm, Vth=0.3V, ID_max=0.8A/cm2, Ion/Ioff=5e4"
    df = extract_parameters(text)
    st.dataframe(df, use_container_width=True)

elif mode == "Select PDF":
    st.subheader("Select an Arxiv PDF from Repository")
    choice = st.selectbox("Choose PDF", list(pdf_options.keys()))
    pdf_path = pdf_options[choice]
    text = extract_text_from_pdf(pdf_path)
    st.text_area("Extracted PDF Text", text[:2000] + "...", height=200)  # preview
    df = extract_parameters(text)
    st.dataframe(df, use_container_width=True)

elif mode == "Upload PDF":
    st.subheader("Upload Your Own PDF")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted PDF Text", text[:2000] + "...", height=200)  # preview
        df = extract_parameters(text)
        st.dataframe(df, use_container_width=True)

# ------------------------
# Download Options
# ------------------------
if not df.empty:
    # CSV
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "finfet_params.csv", "text/csv")

    # Excel
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    st.download_button("⬇️ Download Excel", buffer, "finfet_params.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF
    pdf_bytes = export_pdf(df)
    st.download_button("⬇️ Download PDF", pdf_bytes, "finfet_params.pdf", "application/pdf")
