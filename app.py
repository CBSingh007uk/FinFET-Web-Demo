import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from PIL import Image

# -------------------
# Configuration
# -------------------
st.set_page_config(
    page_title="FinFET Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Logo image
logo_img = Image.new("RGB", (200, 60), color=(0, 120, 255))

# -------------------
# Sidebar
# -------------------
st.sidebar.image(logo_img, use_column_width=True)
mode = st.sidebar.radio("Choose Mode:", ["Synthetic Demo", "Upload PDF"])

# Logs container
log_container = st.sidebar.empty()

# -------------------
# Helper functions
# -------------------
def generate_synthetic_df():
    """Create synthetic FinFET data for demo purposes"""
    n_devices = 5
    df = pd.DataFrame({
        "Device": [f"Device {i+1}" for i in range(n_devices)],
        "Lg (nm)": [3, 3, 4, 3.5, 3],
        "Hfin (nm)": [6, 6.5, 5.5, 6, 6],
        "EOT (nm)": [0.8, 0.7, 0.8, 0.85, 0.8],
        "Vth (V)": [0.3, 0.35, 0.32, 0.3, 0.33],
        "ID (A/cm2)": [0.8, 0.85, 0.75, 0.78, 0.82],
        "Ion/Ioff": [5e4, 4.5e4, 5.2e4, 4.9e4, 5e4],
        "Vg": [np.linspace(0, 1, 10) for _ in range(n_devices)]
    })
    return df

def export_pdf(df, logo_img=logo_img):
    """Export DataFrame to PDF with logo"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "FinFET Parameters", ln=True, align="C")

    # Add logo at top-right
    tmp_logo = BytesIO()
    logo_img.save(tmp_logo, format="PNG")
    tmp_logo.seek(0)
    pdf.image(tmp_logo, x=150, y=8, w=50)

    pdf.ln(20)

    # Add table
    pdf.set_font("Arial", "", 12)
    col_width = pdf.w / (len(df.columns)+1)
    row_height = 8

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)

    # Rows
    for idx, row in df.iterrows():
        for item in row:
            if isinstance(item, np.ndarray):
                item_str = ", ".join([f"{v:.2f}" for v in item])
            else:
                item_str = str(item)
            pdf.cell(col_width, row_height, item_str, border=1)
        pdf.ln(row_height)

    return pdf.output(dest="S").encode("latin1")

# -------------------
# Main functions
# -------------------
def show_synthetic_demo():
    st.subheader("Synthetic FinFET Demo Data")
    df = generate_synthetic_df()

    # Show table without Vg column
    st.dataframe(df.drop(columns=["Vg"], errors="ignore"))

    # Scaling plots
    st.subheader("ID vs Vg Scaling Plot")
    fig, ax = plt.subplots()
    for i in range(len(df)):
        x = df["Vg"][i]
        y = np.linspace(0, df["ID (A/cm2)"][i], len(x))
        ax.plot(x, y, marker='o', label=df["Device"][i])
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg")
    ax.legend()
    st.pyplot(fig)

    # Export options
    st.subheader("Download Table")
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "synthetic_finfet.csv")
    st.download_button("⬇️ Download Excel", df.to_excel(index=False), "synthetic_finfet.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

def show_uploaded_pdf_mode():
    st.subheader("Upload PDF/Image")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file:
        # Simulate extraction for demo
        df = pd.DataFrame({
            "Parameter": ["Lg (nm)", "Hfin (nm)", "EOT (nm)", "Vth (V)", "ID (A/cm2)", "Ion/Ioff"],
            "Value": [3, 6, 0.8, 0.3, 0.8, 5e4]
        })
        st.write("Extracted Parameters:")
        st.dataframe(df)

        # Download
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "finfet_extracted.csv")
        st.download_button("⬇️ Download Excel", df.to_excel(index=False), "finfet_extracted.xlsx")
        st.download_button("⬇️ Download PDF", export_pdf(df), "finfet_extracted.pdf")

# -------------------
# Run selected mode
# -------------------
if mode == "Synthetic Demo":
    show_synthetic_demo()
else:
    show_uploaded_pdf_mode()
