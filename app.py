import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io

# -----------------------------
# Page and theme configuration
# -----------------------------
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔬", layout="wide")

# CSS for dark theme + buttons + sidebar scroll
st.markdown("""
<style>
    body {
        background-color: #1f1f1f;
        color: #f0f0f0;
    }
    .sidebar .sidebar-content {
        background-color: #272727;
        color: #f0f0f0;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border-radius: 12px;
        height: 3em;
        width: 12em;
        font-size: 16px;
    }
    div.row-widget.stDownloadButton > button {
        color: white;
        background-color: #2196F3;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Upload PDF/Image", "Synthetic Demo"])

# -----------------------------
# Utility functions
# -----------------------------
def export_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_excel(df):
    output = io.BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

def export_pdf(df, logo_path="logo.png"):
    pdf = FPDF()
    pdf.add_page()
    # Embed logo if exists
    try:
        pdf.image(logo_path, x=10, y=8, w=33)
    except Exception:
        pass
    pdf.set_font("Arial", size=12)
    pdf.ln(40)
    for i, row in df.iterrows():
        line = ", ".join([f"{col}: {row[col]}" for col in df.columns])
        pdf.multi_cell(0, 10, line)
    return pdf.output(dest="S").encode('latin1')

def generate_synthetic_data():
    # Example 3-5 nm node FinFET
    data = {
        "Lg (nm)": [3, 4, 5],
        "Hfin (nm)": [25, 28, 30],
        "EOT (nm)": [0.7, 0.75, 0.8],
        "ID (A/cm2)": [1.2e5, 1.5e5, 1.8e5],
        "Vth (V)": [0.25, 0.26, 0.27],
        "Ion/Ioff": [1.2e6, 1.3e6, 1.5e6],
        "gm (mS/um)": [1.5, 1.6, 1.8],
        "Rsd (ohm-um)": [100, 95, 90],
        "Capacitance (fF)": [1.2, 1.5, 1.8],
        "Delay (ps)": [10, 9.5, 9],
        "Vg (V)": [np.linspace(0, 1, 50) for _ in range(3)]
    }
    df = pd.DataFrame({
        k: v if not isinstance(v, list) else ["Array" for _ in v]
        for k, v in data.items() if k != "Vg"
    })
    return data, df

# -----------------------------
# Pages
# -----------------------------
if page == "Upload PDF/Image":
    st.title("FinFET Data Extractor")
    st.markdown("Upload PDF/Image → OCR → Extract Parameters")

    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.success("File uploaded successfully! (OCR processing not implemented here for demo)")
    else:
        st.info("Upload a file to extract parameters.")

elif page == "Synthetic Demo":
    st.title("Synthetic FinFET Demo")
    st.markdown("Example 3–5 nm node FinFET data (for poster/demo)")

    data, df = generate_synthetic_data()
    st.dataframe(df, use_container_width=True)

    # ----------------------
    # Scaling plots
    # ----------------------
    st.subheader("Scaling Plots")

    # Ids–Vg curves
    fig1, ax1 = plt.subplots()
    for i in range(len(data["Lg (nm)"])):
        ax1.plot(data["Vg (V)"][i], np.linspace(0, data["ID (A/cm2)"][i], len(data["Vg (V)"][i])),
                 label=f"Lg={data['Lg (nm)'][i]} nm")
    ax1.set_xlabel("Vg (V)", color='white')
    ax1.set_ylabel("Id (A/cm²)", color='white')
    ax1.set_title("Ids–Vg Curves", color='white')
    ax1.grid(True, color='#555555')
    ax1.legend()
    fig1.patch.set_facecolor('#272727')
    ax1.set_facecolor('#1f1f1f')
    st.pyplot(fig1)

    # Ion/Ioff vs Lg
    fig2, ax2 = plt.subplots()
    ax2.plot(data["Lg (nm)"], data["Ion/Ioff"], marker='o', color='#4CAF50')
    ax2.set_xlabel("Lg (nm)", color='white')
    ax2.set_ylabel("Ion/Ioff", color='white')
    ax2.set_title("Ion/Ioff vs Gate Length", color='white')
    ax2.grid(True, color='#555555')
    fig2.patch.set_facecolor('#272727')
    ax2.set_facecolor('#1f1f1f')
    st.pyplot(fig2)

    # ----------------------
    # Export options
    # ----------------------
    st.subheader("Export Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("⬇️ CSV", export_csv(df), "synthetic_finfet.csv")
    with col2:
        st.download_button("⬇️ Excel", export_excel(df), "synthetic_finfet.xlsx")
    with col3:
        st.download_button("⬇️ PDF", export_pdf(df, "logo.png"), "synthetic_finfet.pdf")
