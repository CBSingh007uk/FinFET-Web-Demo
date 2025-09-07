import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io

# ----------------------
# Page config & style
# ----------------------
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔬", layout="wide")

# Darker theme
st.markdown("""
    <style>
        .main {background-color: #1f1f1f; color: #e0e0e0;}
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            font-size: 16px;
            height: 2.8em;
        }
        .sidebar .sidebar-content {background-color: #272727; color: #e0e0e0;}
        .stMarkdown h1 {color: #a0d8f0;}
    </style>
""", unsafe_allow_html=True)

# ----------------------
# Logo
# ----------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=150)
except Exception:
    st.warning("Logo not found. Place 'logo.png' in the app folder.")

# ----------------------
# Title
# ----------------------
st.title("FinFET Data Extractor")
st.markdown("Upload PDF/Image → OCR → Extract Parameters")

# ----------------------
# Synthetic demo
# ----------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Embed logo if exists
    try:
        pdf.image("logo.png", x=10, y=8, w=30)
    except Exception:
        pass
    pdf.ln(35)
    for i in range(len(df)):
        for col in df.columns:
            pdf.cell(0, 8, f"{col}: {df[col][i]}", ln=True)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin1")

def show_synthetic_demo():
    st.subheader("Synthetic Demo (3–5 nm FinFET)")

    # Parameters
    data = {
        "Lg (nm)": [3, 4, 5],
        "Hfin (nm)": [25, 28, 30],
        "EOT (nm)": [0.7, 0.75, 0.8],
        "ID (A/cm2)": [1.2e5, 1.5e5, 1.8e5],
        "Vth (V)": [0.25, 0.26, 0.27],
        "Ion/Ioff": [1.2e6, 1.3e6, 1.5e6],
        "gm (mS/µm)": [1.1, 1.2, 1.3],
        "Rsd (Ω·µm)": [150, 140, 130],
        "Cgg (fF/µm)": [2.5, 2.6, 2.7],
        "Delay (ps)": [12, 11.5, 11],
        "Vg (V)": [np.linspace(0, 1, 50) for _ in range(3)]
    }

    # DataFrame for display (exclude Vg)
    df_display = pd.DataFrame({k: v for k, v in data.items() if k != "Vg"})
    st.dataframe(df_display, use_container_width=True)

    # ----------------------
    # Scaling plots
    # ----------------------
    st.subheader("Scaling Plots")

    # Ids–Vg curves
    fig1, ax1 = plt.subplots()
    for i in range(len(data["Lg (nm)"])):
        ax1.plot(data["Vg"][i], np.linspace(0, data["ID (A/cm2)"][i], len(data["Vg"][i])),
                 label=f"Lg={data['Lg (nm)'][i]} nm")
    ax1.set_xlabel("Vg (V)", color='white')
    ax1.set_ylabel("Id (A/cm²)", color='white')
    ax1.set_title("Ids–Vg Curves", color='white')
    ax1.grid(True, color='#555555')
    ax1.legend()
    fig1.patch.set_facecolor('#1f1f1f')
    ax1.set_facecolor('#272727')
    st.pyplot(fig1)

    # Ion/Ioff vs Lg
    fig2, ax2 = plt.subplots()
    ax2.plot(df_display["Lg (nm)"], df_display["Ion/Ioff"], marker='o', color='#4CAF50')
    ax2.set_xlabel("Lg (nm)", color='white')
    ax2.set_ylabel("Ion/Ioff", color='white')
    ax2.set_title("Ion/Ioff vs Gate Length", color='white')
    ax2.grid(True, color='#555555')
    fig2.patch.set_facecolor('#1f1f1f')
    ax2.set_facecolor('#272727')
    st.pyplot(fig2)

    # ----------------------
    # Download options
    # ----------------------
    csv_bytes = df_display.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_display.to_excel(writer, index=False)
    excel_bytes = excel_buffer.getvalue()
    pdf_bytes = export_pdf(df_display)

    col1, col2, col3 = st.columns(3)
    col1.download_button("Download CSV", csv_bytes, file_name="synthetic_finfet.csv")
    col2.download_button("Download Excel", excel_bytes, file_name="synthetic_finfet.xlsx")
    col3.download_button("Download PDF", pdf_bytes, file_name="synthetic_finfet.pdf")

# ----------------------
# Show synthetic demo
# ----------------------
show_synthetic_demo()
