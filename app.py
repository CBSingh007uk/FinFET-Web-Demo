import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import camelot
import os

# Safe import for PyMuPDF
try:
    import fitz
except ModuleNotFoundError:
    fitz = None
    st.warning("PyMuPDF not installed. PDF-to-image/OCR extraction will not work.")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.image("logo.png", width=150)
st.sidebar.title("FinFET Data Extractor")

pdf_options = { 
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

mode = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Local PDF", "Browse PDF"])

if mode == "Local PDF":
    selected_pdf = st.sidebar.selectbox("Choose PDF", list(pdf_options.keys()))
    pdf_path = pdf_options[selected_pdf]
elif mode == "Browse PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
    pdf_path = uploaded_file if uploaded_file else None
else:
    pdf_path = None  # Synthetic demo mode

st.sidebar.button("Extract", key="extract_btn")

# -----------------------------
# Main Page
# -----------------------------
st.image("logo.png", width=250)
st.title("FinFET Parameter Extraction & Scaling Plots")

# -----------------------------
# Synthetic Demo Functions
# -----------------------------
def synthetic_parameters():
    """Extended synthetic IRDS-aligned dataset"""
    data = [
        {"Node": "7 nm", "Lg (nm)": 14, "Hfin (nm)": 40, "EOT (nm)": 0.6, "ID (A/cm²)": 1.8e4, "Vth (V)": 0.32,
         "Ion/Ioff": 2.5e6, "gm (µS/µm)": 2600, "Rsd (Ω·µm)": 75, "Cgg (fF/µm)": 1.1, "Delay (ps)": 1.2},
        {"Node": "5 nm", "Lg (nm)": 12, "Hfin (nm)": 45, "EOT (nm)": 0.55, "ID (A/cm²)": 2.0e4, "Vth (V)": 0.30,
         "Ion/Ioff": 3.0e6, "gm (µS/µm)": 2800, "Rsd (Ω·µm)": 70, "Cgg (fF/µm)": 1.2, "Delay (ps)": 1.0},
        {"Node": "4 nm", "Lg (nm)": 9, "Hfin (nm)": 50, "EOT (nm)": 0.50, "ID (A/cm²)": 2.3e4, "Vth (V)": 0.28,
         "Ion/Ioff": 4.0e6, "gm (µS/µm)": 3100, "Rsd (Ω·µm)": 60, "Cgg (fF/µm)": 1.4, "Delay (ps)": 0.8},
        {"Node": "3 nm", "Lg (nm)": 7, "Hfin (nm)": 55, "EOT (nm)": 0.48, "ID (A/cm²)": 2.6e4, "Vth (V)": 0.25,
         "Ion/Ioff": 5.0e6, "gm (µS/µm)": 3400, "Rsd (Ω·µm)": 50, "Cgg (fF/µm)": 1.6, "Delay (ps)": 0.6},
        {"Node": "2 nm", "Lg (nm)": 5, "Hfin (nm)": 60, "EOT (nm)": 0.45, "ID (A/cm²)": 3.0e4, "Vth (V)": 0.22,
         "Ion/Ioff": 6.0e6, "gm (µS/µm)": 3600, "Rsd (Ω·µm)": 45, "Cgg (fF/µm)": 1.8, "Delay (ps)": 0.5},
    ]
    return pd.DataFrame(data)

# -----------------------------
# Display & Plotting Functions
# -----------------------------
def display_table(df):
    st.subheader("Extracted Data")
    st.dataframe(df)

def plot_scaling(df):
    st.subheader("Scaling Plots")
    fig, axes = plt.subplots(1, 2, figsize=(12,5))

    axes[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker='o')
    axes[0].set_xlabel("Lg (nm)")
    axes[0].set_ylabel("gm (µS/µm)")
    axes[0].set_title("Lg vs gm")
    axes[0].grid(True)

    axes[1].plot(df["Vth (V)"], df["Ion/Ioff"], marker='o', color='r')
    axes[1].set_xlabel("Vth (V)")
    axes[1].set_ylabel("Ion/Ioff")
    axes[1].set_title("Vth vs Ion/Ioff")
    axes[1].grid(True)

    st.pyplot(fig)

def plot_id_vg(df):
    st.subheader("Id–Vg Synthetic Curves")
    Vg = np.linspace(0, 1, 100)
    fig, ax = plt.subplots()
    for idx, row in df.iterrows():
        Id = row["ID (A/cm²)"] * (1 - np.exp(-Vg / row["Vth (V)"]))
        ax.plot(Vg, Id, label=row["Node"])
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("Id (A/cm²)")
    ax.set_title("Id vs Vg (Synthetic)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# -----------------------------
# PDF Extraction
# -----------------------------
def extract_pdf_tables(path):
    if path is None:
        st.warning("No PDF selected or uploaded.")
        return None
    try:
        tables = camelot.read_pdf(path, flavor='stream', pages='all')
        if len(tables) == 0:
            st.warning("No tables detected. Try a clearer PDF.")
            return None
        df_list = [t.df for t in tables]
        return pd.concat(df_list, ignore_index=True)
    except Exception as e:
        st.error(f"PDF table extraction failed: {e}")
        return None

# -----------------------------
# Main Logic
# -----------------------------
if mode == "Synthetic Demo":
    df = synthetic_parameters()
    display_table(df)
    plot_scaling(df)
    plot_id_vg(df)
else:
    df_pdf = extract_pdf_tables(pdf_path)
    if df_pdf is not None:
        display_table(df_pdf)
        st.info("Id–Vg curve extraction from PDF not yet implemented.")
