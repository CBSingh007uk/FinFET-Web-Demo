import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import io
import re
from PIL import Image

# Optional: PDF processing
import camelot
import fitz  # PyMuPDF
import pytesseract

# -------------------------------
# Logo
# -------------------------------
logo_path = "logo.png"  # main folder
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)
    st.image(logo_path, width=200)  # main page center
else:
    st.warning("Logo not found!")

# -------------------------------
# Sidebar: Input selection
# -------------------------------
option = st.sidebar.selectbox("Choose Input", ["Synthetic Demo", "Local PDF", "Browse PDF"])

pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# -------------------------------
# Synthetic Demo Functions
# -------------------------------
def synthetic_parameters():
    data = [
        {"Node":"5 nm","Lg (nm)":12,"Hfin (nm)":45,"EOT (nm)":0.55,"ID (A/cm²)":2.0e4,"Vth (V)":0.30,"Ion/Ioff":3.0e6,"gm (µS/µm)":2800,"Rsd (Ω·µm)":70,"Cgg (fF/µm)":1.2,"Delay (ps)":1.0},
        {"Node":"4 nm","Lg (nm)":9,"Hfin (nm)":50,"EOT (nm)":0.50,"ID (A/cm²)":2.3e4,"Vth (V)":0.28,"Ion/Ioff":4.0e6,"gm (µS/µm)":3100,"Rsd (Ω·µm)":60,"Cgg (fF/µm)":1.4,"Delay (ps)":0.8},
        {"Node":"3 nm","Lg (nm)":7,"Hfin (nm)":55,"EOT (nm)":0.48,"ID (A/cm²)":2.6e4,"Vth (V)":0.25,"Ion/Ioff":5.0e6,"gm (µS/µm)":3400,"Rsd (Ω·µm)":50,"Cgg (fF/µm)":1.6,"Delay (ps)":0.6},
        {"Node":"2 nm","Lg (nm)":5,"Hfin (nm)":60,"EOT (nm)":0.45,"ID (A/cm²)":3.0e4,"Vth (V)":0.22,"Ion/Ioff":6.0e6,"gm (µS/µm)":3600,"Rsd (Ω·µm)":45,"Cgg (fF/µm)":1.8,"Delay (ps)":0.5},
        {"Node":"1.5 nm","Lg (nm)":4,"Hfin (nm)":65,"EOT (nm)":0.42,"ID (A/cm²)":3.5e4,"Vth (V)":0.20,"Ion/Ioff":7.0e6,"gm (µS/µm)":3800,"Rsd (Ω·µm)":40,"Cgg (fF/µm)":2.0,"Delay (ps)":0.45},
    ]
    return pd.DataFrame(data)

# -------------------------------
# Synthetic Plots
# -------------------------------
def plot_synthetic_iv(df):
    plt.figure(figsize=(6,4))
    for node in df['Node']:
        x = np.linspace(0, 1.0, 100)
        y = 1e-5 * df.loc[df['Node']==node, 'ID (A/cm²)'].values[0] * (x+0.1)**1.5
        plt.plot(x, y, label=node)
    plt.xlabel("Vg (V)")
    plt.ylabel("Id (A/cm²)")
    plt.title("Synthetic Id–Vg Curves")
    plt.legend()
    st.pyplot(plt.gcf())

def plot_scaling(df):
    fig, axes = plt.subplots(1,2, figsize=(10,4))
    axes[0].plot(df['Lg (nm)'], df['gm (µS/µm)'], marker='o')
    axes[0].set_xlabel("Lg (nm)"); axes[0].set_ylabel("gm (µS/µm)"); axes[0].set_title("Lg vs gm")
    
    axes[1].plot(df['Vth (V)'], df['Ion/Ioff'], marker='o')
    axes[1].set_xlabel("Vth (V)"); axes[1].set_ylabel("Ion/Ioff"); axes[1].set_title("Vth vs Ion/Ioff")
    st.pyplot(fig)

# -------------------------------
# PDF Table Extraction
# -------------------------------
def extract_tables(pdf_path):
    tables = []
    try:
        # Camelot stream flavor (text PDFs)
        tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
        tables = [t.df for t in tables if not t.df.empty]
    except Exception as e:
        st.warning(f"Camelot extraction failed: {e}")
    
    # Fallback: OCR
    if not tables:
        st.info("Falling back to OCR table extraction")
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img)
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                rows = []
                for ln in lines:
                    if len(re.findall(r'\d+\.?\d*', ln)) > 0:
                        rows.append(ln.split())
                if rows:
                    tables.append(pd.DataFrame(rows))
        except Exception as e:
            st.error(f"OCR table extraction failed: {e}")
    
    return tables

# -------------------------------
# Main App Logic
# -------------------------------
if option == "Synthetic Demo":
    st.subheader("Synthetic FinFET Dataset")
    df = synthetic_parameters()
    st.dataframe(df)
    plot_synthetic_iv(df)
    plot_scaling(df)

elif option == "Local PDF":
    pdf_choice = st.sidebar.selectbox("Select PDF", list(pdf_options.keys()))
    extract_btn = st.sidebar.button("Extract")
    if extract_btn:
        pdf_path = pdf_options[pdf_choice]
        st.info(f"Processing PDF: {pdf_path}")
        tables = extract_tables(pdf_path)
        if tables:
            for i, t in enumerate(tables):
                st.write(f"Table {i+1}")
                st.dataframe(t)
        else:
            st.warning("No tables detected in PDF.")

elif option == "Browse PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    extract_btn = st.sidebar.button("Extract")
    if extract_btn and uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.info(f"Processing PDF: {uploaded_file.name}")
        tables = extract_tables("temp.pdf")
        if tables:
            for i, t in enumerate(tables):
                st.write(f"Table {i+1}")
                st.dataframe(t)
        else:
            st.warning("No tables detected in PDF.")
