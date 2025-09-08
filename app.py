import streamlit as st
import pandas as pd
from PIL import Image
import os
import io
import re
import numpy as np
import cv2
import pytesseract
import camelot

# ---------- Config ----------
pdf_options = { 
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# Logo (example)
st.sidebar.image("logo.png", use_column_width=True)

# ---------- Sidebar ----------
st.sidebar.title("FinFET Data Extractor")
mode = st.sidebar.radio("Choose input:", ["Synthetic Demo", "Select Local PDF", "Upload PDF"])
selected_pdf = None

if mode == "Synthetic Demo":
    demo_options = list(pdf_options.keys())
    selected_demo = st.sidebar.selectbox("Select demo PDF:", demo_options)
    selected_pdf = pdf_options[selected_demo]

elif mode == "Select Local PDF":
    local_files = [f for f in os.listdir("pdfs") if f.lower().endswith(".pdf")]
    if local_files:
        selected_pdf_name = st.sidebar.selectbox("Choose PDF:", local_files)
        selected_pdf = os.path.join("pdfs", selected_pdf_name)

elif mode == "Upload PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type="pdf")
    if uploaded_file is not None:
        with open(f"pdfs/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        selected_pdf = f"pdfs/{uploaded_file.name}"

if selected_pdf:
    if st.sidebar.button("⬇️ Extract"):
        st.info(f"Processing {selected_pdf}...")

        # ---------- Table Extraction ----------
        tables = []
        try:
            tables = camelot.read_pdf(selected_pdf, flavor='lattice', pages='all')  # lattice first
            if not tables:
                tables = camelot.read_pdf(selected_pdf, flavor='stream', pages='all')
        except Exception as e:
            st.warning(f"Table extraction failed: {e}")

        if tables:
            st.subheader("Detected Tables")
            for i, t in enumerate(tables):
                df = t.df
                st.write(f"Table {i+1}")
                st.dataframe(df)
        else:
            st.warning("No tables detected. Try clearer PDFs or enable 'stream' flavor in Camelot.")

        # ---------- OCR + Param Extraction ----------
        # Synthetic demo: we can just generate example parameters
        if mode == "Synthetic Demo":
            df_params = pd.DataFrame({
                "Lg (nm)": [10, 12],
                "Hfin (nm)": [30, 32],
                "Wfin (nm)": [8, 9],
                "EOT (nm)": [1.2, 1.5],
                "Vth (V)": [0.3, 0.32],
                "Ion (uA)": [150, 160],
                "Ioff (uA)": [0.01, 0.02]
            })
        else:
            # OCR-based param extraction from PDF
            from pdf2image import convert_from_path
            pages = convert_from_path(selected_pdf, dpi=300)
            params_rows = []
            for pnum, page in enumerate(pages, start=1):
                text = pytesseract.image_to_string(page)
                row = {}
                for param in ["Lg", "Hfin", "Wfin", "EOT", "Vth", "Ion", "Ioff"]:
                    m = re.search(rf"{param}[:=]?\s*([-+]?\d*\.?\d+)", text, re.IGNORECASE)
                    row[param] = float(m.group(1)) if m else None
                params_rows.append(row)
            df_params = pd.DataFrame(params_rows)

        st.subheader("Extracted FinFET Parameters")
        st.dataframe(df_params)

        # ---------- Id-Vg Curve Digitization ----------
        st.subheader("Id-Vg Curves")
        import plotly.express as px

        curves = []
        # Simple heuristic: just detect dark lines in the page image
        page = pages[0]  # first page for demo
        img = np.array(page.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours[:3]:  # limit to first few curves
            xs, ys = cnt[:,0,0], cnt[:,0,1]
            x_data = (xs - xs.min()) / (xs.max() - xs.min())
            y_data = (ys - ys.min()) / (ys.max() - ys.min())
            curves.append({"x": x_data, "y": y_data})

        if curves:
            fig = px.line()
            for i, c in enumerate(curves):
                fig.add_scatter(x=c['x'], y=c['y'], mode='lines', name=f"Curve {i+1}")
            st.plotly_chart(fig)
        else:
            st.warning("No curves detected. Try a clearer figure page.")
