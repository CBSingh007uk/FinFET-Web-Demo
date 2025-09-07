# app.py
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
from fpdf import FPDF
import easyocr
import io

# --- Page config ---
st.set_page_config(
    page_title="FinFET Data Extractor",
    page_icon="🔬",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        body {background-color: #1f2937; color: #f0f4f8;}
        .stButton>button {background-color:#4CAF50;color:white;border-radius:12px;height:3em;width:10em;font-size:16px;}
        .stSidebar {background-color: #111827; color:#f0f4f8;}
        h1,h2,h3,h4,h5,h6 {color: #f0f4f8;}
        .reportview-container .main .block-container{padding-top:2rem;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("FinFET Extractor")
log_sidebar = st.sidebar.empty()

# --- Header ---
st.markdown(
    "<h1 style='background: linear-gradient(to right, #4f46e5, #06b6d4); padding:10px; border-radius:10px;'>FinFET Data Extractor</h1>",
    unsafe_allow_html=True
)
st.markdown("Upload a PDF/Image → OCR → Extract Parameters")

# --- Logo ---
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except:
    st.info("Logo not found. Place 'logo.png' in app folder.")

# --- File upload ---
uploaded_file = st.file_uploader("Upload PDF/Image", type=["pdf","png","jpg","jpeg"])

# --- Synthetic Demo ---
synthetic_demo = st.button("Use Synthetic Demo")

# --- Logger ---
def log(msg):
    st.text(msg)
    log_sidebar.text(msg)

# --- PDF export ---
def export_pdf(df, logo_path="logo.png"):
    pdf = FPDF()
    pdf.add_page()
    # Embed logo
    try:
        pdf.image(logo_path, x=10, y=8, w=33)
    except:
        pass
    pdf.set_font("Arial", size=12)
    pdf.ln(40)
    # Table
    for i in range(len(df)):
        row = df.iloc[i]
        for col in df.columns:
            pdf.cell(40, 10, str(row[col]), border=1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin1")

# --- Generate synthetic data ---
def get_synthetic_data():
    data = {
        "Lg (nm)": [5, 5.5, 6],
        "Hfin (nm)": [35, 36, 37],
        "EOT (nm)": [0.8, 0.85, 0.9],
        "ID (A/cm2)": [1.2e3,1.3e3,1.25e3],
        "Vth (V)": [0.35,0.36,0.34],
        "Ion/Ioff": [1e5,1.1e5,0.95e5],
        "gm (mS/um)": [1.2,1.1,1.3],
        "Rsd (Ohm-um)": [2.1,2.0,2.2],
        "Capacitance (fF/um)": [0.3,0.32,0.31],
        "Delay (ps)": [12,11.5,12.2],
        "Vg (V)": [0,0.1,0.2]
    }
    df = pd.DataFrame(data)
    return df

# --- Show synthetic demo ---
def show_synthetic_demo():
    df = get_synthetic_data()
    st.subheader("Synthetic FinFET Demo Parameters")
    st.dataframe(df, width=1200)
    
    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "synthetic_finfet.csv")
    
    # Download PDF
    try:
        pdf_bytes = export_pdf(df)
        st.download_button("⬇️ Download PDF", pdf_bytes, "synthetic_finfet.pdf")
    except Exception as e:
        log(f"PDF export error: {e}")

    # Scaling plots
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("darkgrid")
    fig, ax = plt.subplots(figsize=(6,4))
    for i in range(len(df)):
        ax.plot(df["Vg"][i:i+1], df["ID (A/cm2)"][i:i+1], marker='o', label=f'Device {i+1}')
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("Synthetic ID-Vg Scaling")
    ax.legend()
    st.pyplot(fig)

# --- OCR and extraction ---
def process_file(file):
    reader = easyocr.Reader(['en'], gpu=False)
    # If PDF, convert first page to image
    from pdf2image import convert_from_bytes
    if file.type == "application/pdf":
        try:
            images = convert_from_bytes(file.read())
            img = images[0]
        except Exception as e:
            log(f"PDF to Image conversion error: {e}")
            return
    else:
        img = Image.open(file)
    
    st.image(img, caption="Uploaded Input", use_container_width=True)
    log("Running OCR...")
    try:
        text = reader.readtext(np.array(img), detail=0)
        text_str = "\n".join(text)
        st.subheader("Extracted Text")
        st.text(text_str)
        log("OCR completed successfully")
    except Exception as e:
        log(f"OCR error: {e}")
        return
    
    # Dummy extraction example
    df = pd.DataFrame([{
        "Lg (nm)": "12",
        "Hfin (nm)": "40",
        "EOT (nm)": "0.8",
        "ID (A/cm2)": "1.2e3",
        "Vth (V)": "0.35",
        "Ion/Ioff": "1e5",
        "gm (mS/um)": "1.2",
        "Rsd (Ohm-um)": "2.1",
        "Capacitance (fF/um)": "0.3",
        "Delay (ps)": "12",
        "Vg (V)": "0.0"
    }])
    st.subheader("Extracted Parameters")
    st.dataframe(df, width=1200)
    
    # Download CSV/PDF
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "extracted_finfet.csv")
    try:
        pdf_bytes = export_pdf(df)
        st.download_button("⬇️ Download PDF", pdf_bytes, "extracted_finfet.pdf")
    except Exception as e:
        log(f"PDF export error: {e}")

# --- Main ---
if synthetic_demo:
    log("Using synthetic demo")
    show_synthetic_demo()
elif uploaded_file is not None:
    process_file(uploaded_file)
else:
    st.info("Upload a PDF/Image or use Synthetic Demo.")
