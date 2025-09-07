import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from PIL import Image

# --- Page config ---
st.set_page_config(
    page_title="FinFET Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
st.sidebar.markdown("<h1 style='color:white;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
try:
    logo_img = Image.open("logo.png")  # make sure this exists in app folder
    st.sidebar.image(logo_img, use_column_width=True)
except:
    st.sidebar.write("Logo not found")

option = st.sidebar.radio(
    "Choose mode",
    ("Synthetic Demo", "Upload PDF/Image")
)

# --- Helper: Export PDF ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Synthetic FinFET Data", ln=True, align="C")
    pdf.ln(10)
    # Add table
    pdf.set_font("Arial", "", 12)
    col_width = pdf.w / (len(df.columns) + 1)
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()
    for index, row in df.iterrows():
        for item in row:
            if isinstance(item, list):
                pdf.cell(col_width, 10, str([round(x,2) for x in item]), border=1)
            else:
                pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- Synthetic Demo ---
def show_synthetic_demo():
    st.subheader("Synthetic Demo Parameters")
    # Example FinFET 3-5nm node data
    df = pd.DataFrame({
        "Device": [f"Device {i+1}" for i in range(3)],
        "Lg (nm)": [5, 3, 4],
        "Hfin (nm)": [10, 8, 9],
        "EOT (nm)": [1.2, 1.0, 1.1],
        "ID (A/cm2)": [1.2e-4, 1.5e-4, 1.1e-4],
        "Vth (V)": [0.28, 0.25, 0.27],
        "Ion/Ioff": [10**5, 2*10**5, 1.5*10**5],
        "Vg": [np.linspace(0, 1.2, 10).tolist() for _ in range(3)]
    })

    st.dataframe(df, use_container_width=True)

    # Scaling Plot: ID vs Vg
    st.subheader("ID vs Vg Scaling Plot")
    fig, ax = plt.subplots()
    for i in range(len(df)):
        Vg_values = df.at[i, "Vg"]
        ID_values = np.linspace(0, df.at[i, "ID (A/cm2)"], len(Vg_values))
        ax.plot(Vg_values, ID_values, marker='o', label=df.at[i, "Device"])
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.legend()
    st.pyplot(fig)

    # Downloads
    df_download = df.copy()
    csv_data = df_download.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv_data, "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df_download), "synthetic_finfet.pdf")

# --- Main ---
try:
    if option == "Synthetic Demo":
        show_synthetic_demo()
    else:
        st.info("Upload PDF/Image functionality not implemented in this snippet.")
except Exception as e:
    st.error(f"Error: {e}")
    st.sidebar.error(f"Error: {e}")
