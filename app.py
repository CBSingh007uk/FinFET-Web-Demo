# finfet_streamlit_demo.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import pytesseract
import pdfplumber
import io

# --------------------- Logo ---------------------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
st.image("logo.png", width=200)

st.title("FinFET Data Extractor & Curve Digitization Demo")

# --------------------- Synthetic Demo ---------------------
def synthetic_parameters():
    """IRDS-aligned synthetic FinFET dataset for 3–5 nm nodes"""
    data = [
        {"Node":"5 nm","Lg (nm)":12,"Hfin (nm)":45,"EOT (nm)":0.55,"ID (A/cm²)":2.0e4,"Vth (V)":0.30,
         "Ion/Ioff":3.0e6,"gm (µS/µm)":2800,"Rsd (Ω·µm)":70,"Cgg (fF/µm)":1.2,"Delay (ps)":1.0},
        {"Node":"4 nm","Lg (nm)":9,"Hfin (nm)":50,"EOT (nm)":0.50,"ID (A/cm²)":2.3e4,"Vth (V)":0.28,
         "Ion/Ioff":4.0e6,"gm (µS/µm)":3100,"Rsd (Ω·µm)":60,"Cgg (fF/µm)":1.4,"Delay (ps)":0.8},
        {"Node":"3 nm","Lg (nm)":7,"Hfin (nm)":55,"EOT (nm)":0.48,"ID (A/cm²)":2.6e4,"Vth (V)":0.25,
         "Ion/Ioff":5.0e6,"gm (µS/µm)":3400,"Rsd (Ω·µm)":50,"Cgg (fF/µm)":1.6,"Delay (ps)":0.6},
    ]
    return pd.DataFrame(data)

# --------------------- Sidebar ---------------------
st.sidebar.header("Input Options")
mode = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Local PDF"])

pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

selected_pdf = None
if mode=="Local PDF":
    file_choice = st.sidebar.selectbox("Select PDF from demo", list(pdf_options.keys()))
    upload_file = st.sidebar.file_uploader("Or upload local PDF", type="pdf")
    selected_pdf = upload_file if upload_file else pdf_options[file_choice]

# --------------------- Synthetic Demo Display ---------------------
if mode=="Synthetic Demo":
    st.subheader("Synthetic FinFET Dataset")
    df_synth = synthetic_parameters()
    st.dataframe(df_synth)

    # Scaling plots
    st.subheader("Scaling Plots")
    fig, ax = plt.subplots(1,2, figsize=(12,4))
    ax[0].scatter(df_synth["Lg (nm)"], df_synth["gm (µS/µm)"], c='blue', s=100)
    ax[0].set_xlabel("Lg (nm)"); ax[0].set_ylabel("gm (µS/µm)"); ax[0].set_title("Lg vs gm")
    ax[1].scatter(df_synth["Vth (V)"], df_synth["Ion/Ioff"], c='green', s=100)
    ax[1].set_xlabel("Vth (V)"); ax[1].set_ylabel("Ion/Ioff"); ax[1].set_title("Vth vs Ion/Ioff")
    st.pyplot(fig)

# --------------------- PDF Extraction Functions ---------------------
def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for tbl in page.extract_tables():
                    df = pd.DataFrame(tbl[1:], columns=tbl[0])
                    tables.append(df)
    except Exception as e:
        st.warning(f"Table extraction failed: {e}")
    return tables

def extract_id_vg_curves(pdf_path, pages=None):
    curves_all = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = pages if pages else range(len(pdf.pages))
            for i in pages_to_process:
                page = pdf.pages[i]
                img = page.to_image(resolution=200).original
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (3,3), 0)
                edges = cv2.Canny(blur, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                curves = []
                for cnt in contours:
                    if cv2.contourArea(cnt) < 50:
                        continue
                    xs = cnt[:,:,0].flatten()
                    ys = cnt[:,:,1].flatten()
                    xs_norm = (xs - xs.min()) / (xs.max() - xs.min())
                    ys_norm = (ys - ys.min()) / (ys.max() - ys.min())
                    curves.append((xs_norm, ys_norm))
                curves_all.append(curves)
    except Exception as e:
        st.warning(f"No Id–Vg Curves from PDF (Simplified): {e}")
    return curves_all

# --------------------- PDF Display ---------------------
if mode=="Local PDF" and selected_pdf:
    st.subheader("PDF Extraction Results")
    if st.sidebar.button("Extract Tables & Curves"):
        # Tables
        tables = extract_tables_from_pdf(selected_pdf)
        if tables:
            st.write("Extracted Tables:")
            for idx, df in enumerate(tables):
                st.write(f"Table {idx+1}")
                st.dataframe(df)
        else:
            st.info("No tables detected. Try clearer PDFs.")

        # Id-Vg curves
        st.write("Id–Vg Curves:")
        curves_all = extract_id_vg_curves(selected_pdf)
        for page_idx, curves in enumerate(curves_all):
            st.write(f"Page {page_idx+1}")
            fig, ax = plt.subplots(figsize=(6,4))
            for xs, ys in curves:
                ax.plot(xs, ys, alpha=0.7)
            ax.set_xlabel("Vg (normalized)")
            ax.set_ylabel("Id (normalized)")
            st.pyplot(fig)
