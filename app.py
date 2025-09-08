import streamlit as st
import pandas as pd
import io
import os
import re
from PIL import Image
import pytesseract

# Optional dependencies
try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None
try:
    import camelot
except ModuleNotFoundError:
    camelot = None
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ModuleNotFoundError:
    EXCEL_AVAILABLE = False
try:
    import cv2
except ModuleNotFoundError:
    cv2 = None
import numpy as np

# ---------------------- PDF Options ----------------------
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

st.set_page_config(page_title="FinFET Extractor", layout="wide")
st.title("📄 FinFET Parameter Extractor & Curve Digitizer")
st.write("Select a PDF or upload your own for multi-page extraction, table parsing, and Id–Vg digitization.")

# ---------------------- Sidebar ----------------------
st.sidebar.header("PDF Selection")
selected_pdf_name = st.sidebar.selectbox("Choose a PDF", list(pdf_options.keys()))
pdf_path = pdf_options[selected_pdf_name]
uploaded_file = st.file_uploader("Or upload your own PDF", type="pdf")
if uploaded_file is not None:
    pdf_path = uploaded_file

# ---------------------- Regex for parameters ----------------------
PARAM_REGEXES = {
    'Lg': r'(?:gate\s*length|L[_\s]?g)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ]*)?',
    'Hfin': r'(?:fin\s*height|H[_\s]?fin)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ]*)?',
    'Wfin': r'(?:fin\s*width|W[_\s]?fin)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ]*)?',
    'EOT': r'(?:EOT|effective\s*oxide|oxide\s*thickness)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ]*)?',
    'Vth': r'(?:V[_\s]?th|threshold\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Z%µμ]*)?',
    'Ion': r'(?:I[_\s]?on|on\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ/]*)?',
    'Ioff': r'(?:I[_\s]?off|off\s*current|leakage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ/]*)?',
    'Id': r'(?:I[_\s]?d|drain\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Zµμ/]*)?',
    'Vds': r'(?:V[_\s]?ds|drain\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(\s*[a-zA-Z%µμ]*)?',
}

# ---------------------- Extraction Functions ----------------------
def extract_params_from_text(text):
    results = {}
    for param, regex in PARAM_REGEXES.items():
        match = re.search(regex, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(2).strip() if match.group(2) else ""
            results[param] = f"{value} {unit}".strip()
    return results

def extract_tables_from_pdf(path):
    tables = []
    if camelot and isinstance(path, str) and os.path.exists(path):
        try:
            tbs = camelot.read_pdf(path, pages='all', flavor='lattice')
            tables.extend([t.df for t in tbs if not t.df.empty])
        except:
            pass
    return tables

def ocr_pdf_page(page_image):
    if cv2:
        img = np.array(page_image.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_pil = Image.fromarray(thresh)
    else:
        img_pil = page_image
    text = pytesseract.image_to_string(img_pil)
    return text

def extract_from_pdf(pdf_file):
    pages_data = []
    tables_all = []

    if pdfplumber and hasattr(pdf_file, "read"):
        pdf_obj = pdfplumber.open(pdf_file)
    elif pdfplumber and isinstance(pdf_file, str):
        pdf_obj = pdfplumber.open(pdf_file)
    else:
        pdf_obj = None

    if pdf_obj:
        for i, page in enumerate(pdf_obj.pages, start=1):
            text = page.extract_text() or ""
            params = extract_params_from_text(text)
            pages_data.append({"page": i, **params})
    else:
        # fallback: first page OCR
        if hasattr(pdf_file, "read"):
            img = Image.open(pdf_file)
        else:
            img = Image.open(pdf_file)
        text = ocr_pdf_page(img)
        params = extract_params_from_text(text)
        pages_data.append({"page": 1, **params})

    # table extraction
    if isinstance(pdf_file, str):
        tables_all = extract_tables_from_pdf(pdf_file)

    return pd.DataFrame(pages_data), tables_all

# ---------------------- Button ----------------------
if st.button("🔍 Extract Parameters & Tables"):
    try:
        df_params, tables = extract_from_pdf(pdf_path)
        st.subheader("Extracted Parameters")
        st.dataframe(df_params, use_container_width=True)

        # Download Excel/CSV
        towrite = io.BytesIO()
        if EXCEL_AVAILABLE:
            df_params.to_excel(towrite, index=False, engine='openpyxl')
            st.download_button("⬇️ Download Excel", towrite.getvalue(), file_name="finfet_params.xlsx")
        else:
            csv_data = df_params.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv_data, file_name="finfet_params.csv")

        # Show extracted tables
        if tables:
            st.subheader("Detected Tables")
            for i, t in enumerate(tables, start=1):
                st.write(f"Table {i}")
                st.dataframe(t)
        else:
            st.info("No tables detected.")

    except Exception as e:
        st.error(f"Extraction failed: {e}")
