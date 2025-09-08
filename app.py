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
    """Expanded IRDS-aligned synthetic FinFET dataset for 3–5 nm nodes"""
    data = [
        {"Node": "7 nm", "Lg (nm)": 15, "Hfin (nm)": 40, "EOT (nm)": 0.60,
         "ID (A/cm²)": 1.8e4, "Vth (V)": 0.32, "Ion/Ioff": 2.5e6,
         "gm (µS/µm)": 2500, "Rsd (Ω·µm)": 80, "Cgg (fF/µm)": 1.0, "Delay (ps)": 1.2},
        {"Node": "6 nm", "Lg (nm)": 13, "Hfin (nm)": 42, "EOT (nm)": 0.57,
         "ID (A/cm²)": 1.9e4, "Vth (V)": 0.31, "Ion/Ioff": 2.8e6,
         "gm (µS/µm)": 2600, "Rsd (Ω·µm)": 75, "Cgg (fF/µm)": 1.1, "Delay (ps)": 1.1},
        {"Node": "5 nm", "Lg (nm)": 12, "Hfin (nm)": 45, "EOT (nm)": 0.55,
         "ID (A/cm²)": 2.0e4, "Vth (V)": 0.30, "Ion/Ioff": 3.0e6,
         "gm (µS/µm)": 2800, "Rsd (Ω·µm)": 70, "Cgg (fF/µm)": 1.2, "Delay (ps)": 1.0},
        {"Node": "4 nm", "Lg (nm)": 9, "Hfin (nm)": 50, "EOT (nm)": 0.50,
         "ID (A/cm²)": 2.3e4, "Vth (V)": 0.28, "Ion/Ioff": 4.0e6,
         "gm (µS/µm)": 3100, "Rsd (Ω·µm)": 60, "Cgg (fF/µm)": 1.4, "Delay (ps)": 0.8},
        {"Node": "3 nm", "Lg (nm)": 7, "Hfin (nm)": 55, "EOT (nm)": 0.48,
         "ID (A/cm²)": 2.6e4, "Vth (V)": 0.25, "Ion/Ioff": 5.0e6,
         "gm (µS/µm)": 3400, "Rsd (Ω·µm)": 50, "Cgg (fF/µm)": 1.6, "Delay (ps)": 0.6},
        {"Node": "2 nm", "Lg (nm)": 5, "Hfin (nm)": 60, "EOT (nm)": 0.45,
         "ID (A/cm²)": 3.0e4, "Vth (V)": 0.22, "Ion/Ioff": 6.0e6,
         "gm (µS/µm)": 3800, "Rsd (Ω·µm)": 40, "Cgg (fF/µm)": 1.8, "Delay (ps)": 0.5},
    ]
    df = pd.DataFrame(data)

    # Synthetic Id–Vg curves: assume simple exponential model
    vg = np.linspace(0, 1, 50)
    curves = {}
    for _, row in df.iterrows():
        id_curve = row["ID (A/cm²)"] / (1 + np.exp(-(vg - row["Vth (V)"])/0.05))
        curves[row["Node"]] = id_curve
    return df, vg, curves

# ------------------ Predefined PDFs ------------------
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ------------------ Sidebar ------------------
st.sidebar.title("FinFET Demo Options")
mode = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Local Predefined PDF", "Browse PDF"])

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
        df, vg, curves = synthetic_parameters()
        st.dataframe(df)

        # ------------------ Line Charts for Scaling ------------------
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        ax[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker='o')
        ax[0].set_xlabel("Lg (nm)")
        ax[0].set_ylabel("gm (µS/µm)")
        ax[0].set_title("Lg vs gm (Line Chart)")
        ax[0].grid(True)

        ax[1].plot(df["Vth (V)"], df["Ion/Ioff"], marker='s', color='green')
        ax[1].set_xlabel("Vth (V)")
        ax[1].set_ylabel("Ion/Ioff")
        ax[1].set_title("Vth vs Ion/Ioff (Line Chart)")
        ax[1].grid(True)
        st.pyplot(fig)

        # ------------------ Id–Vg Curves ------------------
        st.subheader("Synthetic Id–Vg Curves")
        fig2, ax2 = plt.subplots(figsize=(8,5))
        for node, id_curve in curves.items():
            ax2.plot(vg, id_curve, label=f"{node} Node")
        ax2.set_xlabel("Vg (V)")
        ax2.set_ylabel("Id (A/cm²)")
        ax2.set_title("Id–Vg Curves (Synthetic)")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

        # ------------------ Download Excel ------------------
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
