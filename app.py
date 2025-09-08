import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt

# Optional dependencies
try:
    import camelot
except ModuleNotFoundError:
    camelot = None
try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None
try:
    import cv2
except ModuleNotFoundError:
    cv2 = None

# ---------------- App Layout ----------------
st.set_page_config(page_title="FinFET Extractor Demo", layout="wide")
st.image("logo.png", width=200)
st.title("📄 FinFET Parameter & Id–Vg Curve Extractor")
st.write("Synthetic demo for parameter extraction, table detection, and Id–Vg curve digitization.")

# ---------------- Sidebar ----------------
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

# ---------------- Parameter Regex ----------------
PARAM_REGEXES = {
    'Lg': r'(?:gate\s*length|L[_\s]?g)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Hfin': r'(?:fin\s*height|H[_\s]?fin)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Wfin': r'(?:fin\s*width|W[_\s]?fin)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'EOT': r'(?:EOT|effective\s*oxide|oxide\s*thickness)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Vth': r'(?:V[_\s]?th|threshold\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Ion': r'(?:I[_\s]?on|on\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Ioff': r'(?:I[_\s]?off|off\s*current|leakage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Id': r'(?:I[_\s]?d|drain\s*current)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
    'Vds': r'(?:V[_\s]?ds|drain\s*voltage)\s*[:=]?\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)',
}

# ---------------- Functions ----------------
def extract_params_from_text(text):
    import re
    results = {}
    for param, rx in PARAM_REGEXES.items():
        m = re.search(rx, text, re.IGNORECASE)
        if m:
            results[param] = float(m.group(1))
    return results

def extract_tables(pdf_file):
    tables = []
    if camelot and isinstance(pdf_file, str) and os.path.exists(pdf_file):
        try:
            tbs = camelot.read_pdf(pdf_file, pages="all", flavor="lattice")
            tables.extend([t.df for t in tbs if not t.df.empty])
            if not tables:
                tbs = camelot.read_pdf(pdf_file, pages="all", flavor="stream")
                tables.extend([t.df for t in tbs if not t.df.empty])
        except:
            pass
    return tables

def digitize_idvg_from_page(page_image):
    if cv2 is None:
        return None
    img = np.array(page_image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    edges = cv2.Canny(blur, 50, 150)
    ys, xs = np.where(edges > 0)
    if len(xs) == 0: return None
    # Normalize for plotting
    xs_norm = (xs - xs.min()) / (xs.max() - xs.min())
    ys_norm = (ys - ys.min()) / (ys.max() - ys.min())
    return xs_norm, ys_norm

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
                img_obj = page.to_image(resolution=150).original
                curves = digitize_idvg_from_page(img_obj)
                if curves:
                    curves_all.append({"page": i, "x": curves[0], "y": curves[1]})
    else:
        # fallback single image
        if hasattr(pdf_file, "read"):
            img = Image.open(pdf_file)
        else:
            img = Image.open(pdf_file)
        text = pytesseract.image_to_string(img)
        params = extract_params_from_text(text)
        pages_data.append({"page": 1, **params})
        curves = digitize_idvg_from_page(img)
        if curves:
            curves_all.append({"page": 1, "x": curves[0], "y": curves[1]})

    if isinstance(pdf_file, str):
        tables_all = extract_tables(pdf_file)

    return pd.DataFrame(pages_data), tables_all, curves_all

# ---------------- Extract Button ----------------
if st.button("🔍 Extract Parameters, Tables & Curves"):
    try:
        df_params, tables, curves = extract_from_pdf(pdf_path)

        st.subheader("Extracted Parameters")
        st.dataframe(df_params, use_container_width=True)

        # Download CSV
        csv_data = df_params.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download CSV", csv_data, file_name="finfet_params.csv")

        # Show tables
        st.subheader("Detected Tables")
        if tables:
            for i, t in enumerate(tables, start=1):
                st.write(f"Table {i}")
                st.dataframe(t)
        else:
            st.info("No tables detected. Try clearer PDFs or enable Camelot 'stream' flavor.")

        # Plot Id–Vg curves
        st.subheader("Digitized Id–Vg Curves")
        if curves:
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
