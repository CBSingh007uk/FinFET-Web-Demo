import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import camelot
import pdfplumber
from io import BytesIO
import os

# ------------------------------
# Logo
# ------------------------------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
logo_path = "logo.png"  # add your logo here
if os.path.exists(logo_path):
    st.image(logo_path, width=200)

st.title("FinFET Parameter Extraction & Analysis Demo")

# ------------------------------
# Synthetic Demo Functions
# ------------------------------
def synthetic_parameters():
    """IRDS-aligned synthetic FinFET dataset for 3–5 nm nodes"""
    data = [
        {"Node": "5 nm", "Lg (nm)": 12, "Hfin (nm)": 45, "EOT (nm)": 0.55,
         "ID (A/cm²)": 2.0e4, "Vth (V)": 0.30, "Ion/Ioff": 3.0e6,
         "gm (µS/µm)": 2800, "Rsd (Ω·µm)": 70, "Cgg (fF/µm)": 1.2, "Delay (ps)": 1.0},
        {"Node": "4 nm", "Lg (nm)": 9, "Hfin (nm)": 50, "EOT (nm)": 0.50,
         "ID (A/cm²)": 2.3e4, "Vth (V)": 0.28, "Ion/Ioff": 4.0e6,
         "gm (µS/µm)": 3100, "Rsd (Ω·µm)": 60, "Cgg (fF/µm)": 1.4, "Delay (ps)": 0.8},
        {"Node": "3 nm", "Lg (nm)": 7, "Hfin (nm)": 55, "EOT (nm)": 0.48,
         "ID (A/cm²)": 2.6e4, "Vth (V)": 0.25, "Ion/Ioff": 5.0e6,
         "gm (µS/µm)": 3400, "Rsd (Ω·µm)": 50, "Cgg (fF/µm)": 1.6, "Delay (ps)": 0.6},
    ]
    return pd.DataFrame(data)

def synthetic_iv_curves():
    """Generate synthetic Id-Vg curves"""
    Vg = np.linspace(0, 1.0, 100)
    curves = {}
    for node, k in zip(["5 nm", "4 nm", "3 nm"], [2.0e-4, 2.3e-4, 2.6e-4]):
        Id = k * (Vg - 0.25)**2
        Id[Id<0] = 0
        curves[node] = Id
    return Vg, curves

# ------------------------------
# Sidebar Options
# ------------------------------
pdf_options = { 
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

option = st.sidebar.selectbox(
    "Select Input Source",
    ["Synthetic Demo"] + list(pdf_options.keys()) + ["Browse PDF"]
)

uploaded_file = None
selected_pdf = None
if option == "Browse PDF":
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
elif option in pdf_options:
    selected_pdf = pdf_options[option]

extract_button = st.sidebar.button("Extract")

# ------------------------------
# Main Extraction Logic
# ------------------------------
if extract_button:
    if option == "Synthetic Demo":
        df = synthetic_parameters()
        st.subheader("Synthetic FinFET Dataset")
        st.dataframe(df)

        # Scaling plots
        st.subheader("Scaling Plots")
        fig, axes = plt.subplots(1,2, figsize=(12,4))
        axes[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker='o', linestyle='-')
        axes[0].set_xlabel("Lg (nm)")
        axes[0].set_ylabel("gm (µS/µm)")
        axes[0].set_title("Lg vs gm")
        axes[1].plot(df["Vth (V)"], df["Ion/Ioff"], marker='s', linestyle='--', color='orange')
        axes[1].set_xlabel("Vth (V)")
        axes[1].set_ylabel("Ion/Ioff")
        axes[1].set_title("Vth vs Ion/Ioff")
        st.pyplot(fig)

        # Synthetic Id-Vg curves
        st.subheader("Synthetic Id–Vg Curves")
        Vg, curves = synthetic_iv_curves()
        plt.figure(figsize=(6,4))
        for node, Id in curves.items():
            plt.plot(Vg, Id, label=node)
        plt.xlabel("Vg (V)")
        plt.ylabel("Id (A/cm²)")
        plt.title("Synthetic Id–Vg Curves")
        plt.legend()
        st.pyplot(plt)

    elif selected_pdf or uploaded_file:
        # PDF Table Extraction
        pdf_path = selected_pdf if selected_pdf else uploaded_file
        st.subheader(f"Extracted Parameters from PDF")
        try:
            if uploaded_file:
                tables = camelot.read_pdf(uploaded_file, pages='all', flavor='stream', dpi=300)
            else:
                tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream', dpi=300)
            if tables:
                df_list = [t.df for t in tables]
                df = pd.concat(df_list, ignore_index=True)
                st.dataframe(df)
            else:
                st.warning("No tables detected. Try clearer PDFs or 'lattice' flavor.")
        except Exception as e:
            st.error(f"Table extraction failed: {e}")

        # PDF Figure Extraction (simplified)
        st.subheader("Id–Vg Curves from PDF (Simplified)")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:2]:  # first 2 pages for demo
                    im = page.to_image(resolution=150)
                    st.image(im.original, caption=f"Page {page.page_number}")
                    # TODO: curve digitization could be added with OpenCV (advanced)
        except Exception as e:
            st.warning(f"PDF figure extraction failed: {e}")
