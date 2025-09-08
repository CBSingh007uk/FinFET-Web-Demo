import streamlit as st
import pandas as pd
import io
import os
import re
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt
import numpy as np

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

# ---------------------- App Layout ----------------------
st.set_page_config(page_title="FinFET Extractor Demo", layout="wide")

# Logo (replace path with your logo file if available)
st.image("logo.png", width=200)
st.title("📄 FinFET Parameter & Curve Extractor Demo")
st.write("Synthetic demo for parameter extraction, table detection, and Id–Vg curve digitization.")

# ---------------------- Sidebar ----------------------
st.sidebar.header("PDF Selection")
synthetic_pdfs = {
    "Demo PDF 1": "synthetic/finfet_demo1.pdf",
    "Demo PDF 2": "synthetic/finfet_demo2.pdf"
}
selected_pdf_name = st.sidebar.selectbox("Choose a demo PDF", list(synthetic_pdfs.keys()))
pdf_path = synthetic_pdfs[selected_pdf_name]
uploaded_file = st.sidebar.file_uploader("Or upload your own PDF", type="pdf")
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
            if not tables:
                tbs = camelot.read_pdf(path, pages='all', flavor='stream')
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

def digitize_idvg(image_pil):
    img = np.array(image_pil.convert("RGB"))
    if cv2 is None:
        st.warning("OpenCV not available, skipping curve extraction.")
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    ys, xs = np.where(edges > 0)
    if len(xs) == 0:
        return None
    xs_norm = (xs - xs.min()) / (xs.max() - xs.min())
    ys_norm = (ys - ys.min()) / (ys.max() - ys.min())
    return xs_norm, ys_norm

# ---------------------- PDF Extraction ----------------------
def extract_from_pdf(pdf_file):
    pages_data = []
    tables_all = []
    curves_all = []

    pdf_obj = None
    if pdfplumber and hasattr(pdf_file, "read"):
        pdf_obj = pdfplumber.open(pdf_file)
    elif pdfplumber and isinstance(pdf_file, str):
        pdf_obj = pdfplumber.open(pdf_file)

    if pdf_obj:
        for i, page in enumerate(pdf_obj.pages, start=1):
            text = page.extract_text() or ""
            params = extract_params_from_text(text)
            pages_data.append({"page": i, **params})

            # Curve extraction
            if page.images:
                img_obj = page.to_image(resolution=200).original
                curves = digitize_idvg(img_obj)
                if curves:
                    curves_all.append({"page": i, "x": curves[0], "y": curves[1]})
    else:
        if hasattr(pdf_file, "read"):
            img = Image.open(pdf_file)
        else:
            img = Image.open(pdf_file)
        text = ocr_pdf_page(img)
        params = extract_params_from_text(text)
        pages_data.append({"page": 1, **params})
        curves = digitize_idvg(img)
        if curves:
            curves_all.append({"page": 1, "x": curves[0], "y": curves[1]})

    # Table extraction
    if isinstance(pdf_file, str):
        tables_all = extract_tables_from_pdf(pdf_file)

    return pd.DataFrame(pages_data), tables_all, curves_all

# ---------------------- Extraction Button ----------------------
if st.button("🔍 Extract Parameters, Tables & Curves"):
    try:
        df_params, tables, curves = extract_from_pdf(pdf_path)
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

        # Show tables
        if tables:
            st.subheader("Detected Tables")
            for i, t in enumerate(tables, start=1):
                st.write(f"Table {i}")
                st.dataframe(t)
        else:
            st.info("No tables detected. Try clearer PDFs or enable 'stream' flavor in Camelot.")

        # Plot extracted curves
        if curves:
            st.subheader("Digitized Id–Vg Curves")
            fig, ax = plt.subplots()
            for c in curves:
                ax.plot(c['x'], c['y'], label=f"Page {c['page']}")
            ax.set_xlabel("Vg (normalized)")
            ax.set_ylabel("Id (normalized)")
            ax.legend()
            st.pyplot(fig)
        else:
            st.info("No curves detected.")

    except Exception as e:
        st.error(f"Extraction failed: {e}")
