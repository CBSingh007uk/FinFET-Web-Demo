import streamlit as st
import os
import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
import re
import io

# ---------------- PDF options ----------------
pdf_options = { 
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

st.title("FinFET Parameter Extractor")

# ---------------- Select or Upload PDF ----------------
pdf_choice = st.selectbox("Select a PDF from library", list(pdf_options.keys()))
uploaded_file = st.file_uploader("Or upload your own PDF", type="pdf")

if uploaded_file is not None:
    pdf_path = uploaded_file
elif pdf_choice:
    pdf_path = pdf_options[pdf_choice]
else:
    st.warning("Please select or upload a PDF.")
    st.stop()

# ---------------- PDF Text Extraction ----------------
def extract_text_from_pdf(path):
    text = ""
    # if uploaded_file is a BytesIO object
    if isinstance(path, io.BytesIO):
        try:
            with fitz.open(stream=path.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        except Exception:
            path.seek(0)
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
    else:  # path is local file
        try:
            with fitz.open(path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
    return text

pdf_text = extract_text_from_pdf(pdf_path)

# ---------------- Parameter Extraction (basic regex) ----------------
PARAM_REGEXES = {
    'Lg': r'(?:gate\s*length|L[_\s]?g)\s*[:=]?\s*([\d\.]+)\s*(nm|um|µm)?',
    'Hfin': r'(?:fin\s*height|H[_\s]?fin)\s*[:=]?\s*([\d\.]+)\s*(nm|um|µm)?',
    'Wfin': r'(?:fin\s*width|W[_\s]?fin)\s*[:=]?\s*([\d\.]+)\s*(nm|um|µm)?',
    'EOT': r'(?:EOT|effective\s*oxide|oxide\s*thickness)\s*[:=]?\s*([\d\.]+)\s*(nm|um|µm)?',
    'Vth': r'(?:V[_\s]?th|threshold\s*voltage)\s*[:=]?\s*([\d\.]+)\s*(V)?',
    'Ion': r'(?:I[_\s]?on|on\s*current)\s*[:=]?\s*([\d\.]+)\s*(uA|µA|nA)?',
    'Ioff': r'(?:I[_\s]?off|off\s*current)\s*[:=]?\s*([\d\.]+)\s*(uA|µA|nA)?',
    'Id': r'(?:I[_\s]?d|drain\s*current)\s*[:=]?\s*([\d\.]+)\s*(uA|µA|nA)?',
    'Vds': r'(?:V[_\s]?ds|drain\s*voltage)\s*[:=]?\s*([\d\.]+)\s*(V)?',
}

def extract_params(text):
    results = {}
    for param, rx in PARAM_REGEXES.items():
        m = re.search(rx, text, re.IGNORECASE)
        if m:
            val, unit = m.groups()
            if val:
                results[param] = f"{val} {unit or ''}".strip()
    return results

params_dict = extract_params(pdf_text)

if params_dict:
    st.subheader("Extracted Parameters")
    df_params = pd.DataFrame([params_dict])
    st.dataframe(df_params, use_container_width=True)
    
    # Excel download
    towrite = io.BytesIO()
    df_params.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    st.download_button(
        label="⬇️ Download Excel",
        data=towrite,
        file_name="finfet_params.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No parameters found in this PDF. Try a different file.")
