import streamlit as st
import pandas as pd
import io
import os
import re
from PIL import Image
import pytesseract

# Attempt to import openpyxl for Excel export
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ModuleNotFoundError:
    EXCEL_AVAILABLE = False

# Optional: pdfplumber for table extraction
try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None

# ---------------------- PDF Options ----------------------
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="FinFET Parameter Extractor", layout="wide")
st.title("📄 FinFET Parameter Extractor")
st.write("Select a PDF from the list or upload your own PDF for parameter extraction.")

# Sidebar PDF selection
st.sidebar.header("Select PDF")
selected_pdf_name = st.sidebar.selectbox("Choose a PDF", list(pdf_options.keys()))
pdf_path = pdf_options[selected_pdf_name]

# Optional PDF upload
uploaded_file = st.file_uploader("Or upload a PDF from your computer", type="pdf")
if uploaded_file is not None:
    pdf_path = uploaded_file  # Use uploaded PDF

# ---------------------- Parameter Extraction ----------------------
# Standard FinFET parameters
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

def extract_params_from_text(text):
    """Extract FinFET parameters using regex."""
    results = {}
    for param, regex in PARAM_REGEXES.items():
        match = re.search(regex, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(2).strip() if match.group(2) else ""
            results[param] = f"{value} {unit}".strip()
    return results

def extract_parameters(pdf_file):
    """Extract parameters from a PDF or uploaded file."""
    text_content = ""

    # pdfplumber extraction
    if pdfplumber and hasattr(pdf_file, "read"):
        # Uploaded file
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
    elif pdfplumber and isinstance(pdf_file, str) and os.path.exists(pdf_file):
        # Local file
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
    else:
        # fallback: OCR on first page
        if hasattr(pdf_file, "read"):
            img = Image.open(pdf_file)
        else:
            img = Image.open(pdf_file)
        text_content = pytesseract.image_to_string(img)

    params_dict = extract_params_from_text(text_content)
    if not params_dict:
        st.warning("No parameters detected. The PDF may require OCR or improved regex patterns.")
    df = pd.DataFrame(params_dict.items(), columns=["Parameter", "Value"])
    return df

# ---------------------- Extraction Button ----------------------
if st.button("🔍 Extract Parameters"):
    try:
        df = extract_parameters(pdf_path)
        st.subheader("Extracted Parameters")
        st.dataframe(df, use_container_width=True)

        # Download button
        towrite = io.BytesIO()
        if EXCEL_AVAILABLE:
            df.to_excel(towrite, index=False, engine='openpyxl')
            st.download_button("⬇️ Download Excel", towrite.getvalue(), file_name="finfet_params.xlsx")
        else:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download CSV", csv_data, file_name="finfet_params.csv")
    except Exception as e:
        st.error(f"Extraction failed: {e}")
