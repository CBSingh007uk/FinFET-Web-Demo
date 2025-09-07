# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw
import easyocr
from io import BytesIO
from fpdf import FPDF
from pdf2image import convert_from_bytes

# --- Page config ---
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔬", layout="wide")

# --- Custom CSS for dark theme ---
st.markdown("""
    <style>
        body {
            background-color: #1e1e2f;
            color: #e0e0e0;
        }
        .sidebar .sidebar-content {
            background-color: #2e2e3e;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            height: 3em;
            width: 12em;
            font-size: 18px;
        }
        .stDownloadButton>button {
            background-color: #2196F3;
            color: white;
            border-radius: 10px;
        }
        h1, h2, h3 {
            color: #00bcd4;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("FinFET Data Extractor")
st.sidebar.markdown("Upload PDF/Image → OCR → Extract Parameters")
log_text = st.sidebar.empty()  # sidebar log

# --- Load logo ---
try:
    logo = Image.open("logo.png")
except:
    logo = Image.new("RGB", (150, 50), color=(0, 150, 150))
st.image(logo, width=200)

st.title("FinFET Data Extractor")
st.markdown("**Upload PDF/Image or use synthetic demo**")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload PDF/Image", type=["pdf", "png", "jpg", "jpeg"])

# --- Synthetic demo parameters ---
synthetic_data = {
    "Lg (nm)": [5.0, 4.5, 3.8],
    "Hfin (nm)": [35, 40, 30],
    "EOT (nm)": [0.9, 0.8, 0.7],
    "Vth (V)": [0.25, 0.22, 0.20],
    "ID (A/cm2)": [1.2e-4, 1.5e-4, 1.7e-4],
    "Ion/Ioff": [1.2e5, 1.5e5, 1.7e5],
    "gm (S)": [1.2e-3, 1.5e-3, 1.7e-3],
    "Rsd (Ohm)": [100, 90, 85],
    "Cgg (fF)": [0.8, 0.7, 0.65],
    "Delay (ps)": [5, 4.5, 4.0],
    "Vg": [np.linspace(0, 1, 50) for _ in range(3)]
}

# --- Function to export PDF with logo ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Add logo
    try:
        pdf.image("logo.png", x=160, y=5, w=30)
    except:
        pass
    pdf.ln(20)
    for i, row in df.iterrows():
        pdf.cell(0, 10, txt=f"Device {i+1}:", ln=True)
        for col in df.columns:
            pdf.cell(0, 10, txt=f"  {col}: {row[col]}", ln=True)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin1")

# --- Function to perform OCR ---
def run_ocr(img):
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(np.array(img))
    text = "\n".join([res[1] for res in result])
    return text

# --- Function to show synthetic demo ---
def show_synthetic_demo():
    st.subheader("Synthetic Demo")
    df = pd.DataFrame({
        k: v if k != "Vg" else ["Array"]*len(v) for k,v in synthetic_data.items()
    })
    st.dataframe(df, use_container_width=True)
    # Scaling plots
    st.subheader("Scaling Plots")
    fig, ax = plt.subplots(figsize=(6,4))
    for i in range(len(synthetic_data["Lg (nm)"])):
        ax.plot(synthetic_data["Vg"][i], np.linspace(0, synthetic_data["ID (A/cm2)"][i], len(synthetic_data["Vg"][i])), label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("Scaling Plot")
    ax.legend()
    st.pyplot(fig)

    # Download buttons
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

    log_text.text("Synthetic demo displayed successfully.")

# --- Main logic ---
try:
    if uploaded_file:
        st.subheader("Uploaded File Preview")
        if uploaded_file.type == "application/pdf":
            pages = convert_from_bytes(uploaded_file.read())
            img = pages[0]
        else:
            img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_container_width=True)

        st.subheader("Running OCR...")
        text = run_ocr(img)
        st.text(text)
        log_text.text("OCR completed successfully.")

    else:
        if st.button("Use Synthetic Demo"):
            show_synthetic_demo()
except Exception as e:
    st.error(f"Error: {e}")
    log_text.text(f"Error: {e}")
