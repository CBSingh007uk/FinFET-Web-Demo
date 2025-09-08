import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from PIL import Image
import camelot
import os

# ------------------ CONFIG ------------------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# Logo
st.sidebar.image("logo.png", use_column_width=True)  # Replace with your logo path

# ------------------ Synthetic Demo Dataset ------------------
def synthetic_parameters():
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

# ------------------ Predefined PDFs ------------------
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ------------------ Sidebar ------------------
st.sidebar.title("Select Mode")
mode = st.sidebar.radio("Mode", ["Synthetic Demo", "Local Predefined PDF", "Browse PDF"])

selected_pdf_path = None
uploaded_file = None

if mode == "Local Predefined PDF":
    pdf_name = st.sidebar.selectbox("Select PDF", list(pdf_options.keys()))
    selected_pdf_path = pdf_options[pdf_name]
elif mode == "Browse PDF":
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if st.sidebar.button("Extract / Run"):
    if mode == "Synthetic Demo":
        st.subheader("Synthetic Demo Parameters")
        df = synthetic_parameters()
        st.dataframe(df)

        # Scaling plots
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        # Lg vs gm
        ax[0].scatter(df["Lg (nm)"], df["gm (µS/µm)"], color='blue')
        ax[0].set_xlabel("Lg (nm)")
        ax[0].set_ylabel("gm (µS/µm)")
        ax[0].set_title("Lg vs gm")
        # Vth vs Ion/Ioff
        ax[1].scatter(df["Vth (V)"], df["Ion/Ioff"], color='green')
        ax[1].set_xlabel("Vth (V)")
        ax[1].set_ylabel("Ion/Ioff")
        ax[1].set_title("Vth vs Ion/Ioff")
        st.pyplot(fig)

        # Download CSV
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, engine='openpyxl')
        st.download_button("⬇️ Download Excel", towrite.getvalue(), "synthetic_finfet.xlsx")

    elif mode in ["Local Predefined PDF", "Browse PDF"]:
        # Determine PDF path
        if uploaded_file is not None:
            pdf_path = uploaded_file
        else:
            pdf_path = selected_pdf_path
            if not os.path.exists(pdf_path):
                st.error(f"PDF not found: {pdf_path}")
                st.stop()

        st.subheader("PDF Extraction Results")

        # ------------------ Table Extraction ------------------
        try:
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
            if tables:
                for i, t in enumerate(tables):
                    st.write(f"Table {i+1}")
                    st.dataframe(t.df)
            else:
                st.warning("No tables detected. Try clearer PDFs or different flavor in Camelot.")
        except Exception as e:
            st.error(f"Table extraction failed: {e}")

        # ------------------ Id-Vg Curve Digitization ------------------
        st.info("Id–Vg curve extraction not implemented for PDF mode in this demo.")
        st.warning("Interactive curve extraction from multi-page PDFs requires OpenCV and advanced processing.")

