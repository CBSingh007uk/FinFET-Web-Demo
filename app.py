import os
import re
import pandas as pd
from io import BytesIO
from PIL import Image
import streamlit as st

# ---------- Optional imports ----------
try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:
    fitz = None

try:
    import pytesseract
except ModuleNotFoundError:
    pytesseract = None

# ---------- CONFIG ----------
PDF_FOLDER = "pdfs"
PARAM_REGEXES = {
    'Lg': r'(?:gate\s*length|L[_\s]?g)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Hfin': r'(?:fin\s*height|H[_\s]?fin)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'EOT': r'(?:EOT|effective\s*oxide|oxide\s*thickness)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Vth': r'(?:V[_\s]?th|threshold\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Ion': r'(?:I[_\s]?on|on\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Ioff': r'(?:I[_\s]?off|off\s*current|leakage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Id': r'(?:I[_\s]?d|drain\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Vds': r'(?:V[_\s]?ds|drain\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
}

# ---------- Helpers ----------
def extract_text_from_pdf(pdf_path):
    """Extract text using pdfplumber or PyMuPDF fallback"""
    text = ""
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception:
            pass
    if fitz:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            pass
    return ""

def extract_params_from_text(text):
    """Return dict of FinFET parameters found in text"""
    params = {}
    for p, rx in PARAM_REGEXES.items():
        m = re.search(rx, text, re.IGNORECASE)
        if m:
            params[p] = m.group(1)
    return params

def ocr_image_to_text(img):
    if pytesseract is None:
        return ""
    return pytesseract.image_to_string(img)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
st.title("📄 FinFET Parameter Extractor")

# PDF selection
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

pdf_choice = st.selectbox("Select a PDF from local folder:", list(pdf_options.keys()))
pdf_path = pdf_options[pdf_choice]

uploaded_file = st.file_uploader("Or upload a PDF from your computer:", type="pdf")
if uploaded_file:
    pdf_path = uploaded_file
    st.info(f"Processing uploaded file: {uploaded_file.name}")

# Extract parameters
if st.button("Extract Parameters"):
    if isinstance(pdf_path, str) and not os.path.exists(pdf_path):
        st.error(f"PDF not found: {pdf_path}")
    else:
        text = ""
        if isinstance(pdf_path, str):
            text = extract_text_from_pdf(pdf_path)
        else:
            # uploaded BytesIO file
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
                    tmpf.write(pdf_path.read())
                    tmp_path = tmpf.name
                text = extract_text_from_pdf(tmp_path)
            except Exception:
                st.error("Failed to read uploaded PDF")

        # If no text from PDF, try OCR on first page image
        if not text and fitz:
            try:
                doc = fitz.open(tmp_path if not isinstance(pdf_path, str) else pdf_path)
                page = doc[0]
                pix = page.get_pixmap(dpi=300)
                img = Image.open(BytesIO(pix.tobytes("png")))
                text = ocr_image_to_text(img)
            except Exception:
                st.warning("Failed OCR extraction")

        if not text:
            st.warning("No text extracted from PDF.")
        else:
            params = extract_params_from_text(text)
            if not params:
                st.warning("No FinFET parameters detected.")
            else:
                df = pd.DataFrame([params])
                st.subheader("Extracted Parameters")
                st.dataframe(df, use_container_width=True)
                # Download Excel
                towrite = BytesIO()
                df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=towrite,
                    file_name="finfet_params.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
