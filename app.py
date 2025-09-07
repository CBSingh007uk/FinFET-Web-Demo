import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from pdf2image import convert_from_bytes
import easyocr

# --- Page config ---
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# --- Sidebar and center log ---
log_sidebar = st.sidebar.empty()
log_center = st.empty()
def log(msg):
    log_sidebar.text(msg)
    log_center.text(msg)

# --- Dark theme CSS ---
st.markdown("""
<style>
body {
    background-color: #1c1c1e;
    color: #f0f0f0;
}
.stButton>button {
    color: #ffffff;
    background-color: #4caf50;
    border-radius: 12px;
    height: 3em;
    width: 10em;
    font-size: 16px;
}
.stFileUploader>div>div>input {
    color: #f0f0f0;
}
</style>
""", unsafe_allow_html=True)

# --- Header with gradient ---
st.markdown("""
<div style="background: linear-gradient(90deg, #0f2027, #203a43, #2c5364); padding: 20px; border-radius: 10px; text-align:center;">
<h1 style="color:#e0e0e0;">🔬 FinFET Data Extractor</h1>
<p style="color:#c0c0c0;">Upload PDF/Image → OCR → Extract Parameters</p>
</div>
""", unsafe_allow_html=True)

# --- Logo ---
try:
    logo = Image.open("logo.png")
    st.image(logo, width=120)
except Exception as e:
    log(f"Logo not found: {e}")

# --- File upload ---
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
reader = easyocr.Reader(['en'], gpu=False)

def ocr_file(file):
    try:
        if file.type == "application/pdf":
            images = convert_from_bytes(file.read())
            img = images[0]
        else:
            img = Image.open(file)
        result = reader.readtext(np.array(img))
        text = " ".join([r[1] for r in result])
        log(f"OCR extracted text: {text[:200]}...")
        return text
    except Exception as e:
        log(f"OCR failed: {e}")
        st.error(f"OCR failed: {e}")
        return ""

# --- Extract parameters from text ---
def extract_params(text):
    import re
    keys = ["Lg","Hfin","EOT","ID","Vth","Ion/Ioff","gm","Rsd","Capacitance","Delay"]
    params = {}
    for k in keys:
        m = re.search(rf"{k}\s*[:=]\s*([\d.eE+-]+)", text)
        if m:
            params[k] = float(m.group(1))
        else:
            params[k] = None
    return params

# --- Synthetic demo ---
def show_synthetic_demo():
    log("Using synthetic demo")
    n_samples = 5
    data = {
        "Lg (nm)": np.random.choice([3,4,5], n_samples),
        "Hfin (nm)": np.random.randint(10,50,n_samples),
        "EOT (nm)": np.round(np.random.uniform(0.5,1.0,n_samples),2),
        "ID (A/cm2)": np.round(np.random.uniform(1e-5,1e-3,n_samples),6),
        "Vth (V)": np.round(np.random.uniform(0.2,0.5,n_samples),2),
        "Ion/Ioff": np.round(np.random.uniform(1e4,1e6,n_samples),0),
        "gm": np.round(np.random.uniform(0.1,1.0,n_samples),2),
        "Rsd (ohm)": np.round(np.random.uniform(10,50,n_samples),2),
        "Capacitance (fF)": np.round(np.random.uniform(0.1,1.0,n_samples),2),
        "Delay (ps)": np.round(np.random.uniform(1,10,n_samples),2),
        "Vg_sample (V)": [np.round(np.linspace(0,1,10),2).tolist() for _ in range(n_samples)]
    }
    df = pd.DataFrame(data)
    st.subheader("Synthetic FinFET Parameters")
    st.dataframe(df.drop(columns=["Vg_sample"]), use_container_width=True)
    log("Synthetic table generated")

    # --- Scaling plots ---
    st.subheader("Scaling Plots")
    fig, ax = plt.subplots()
    for i in range(n_samples):
        vg = np.linspace(0,1,10)
        id_curve = np.linspace(0, data["ID (A/cm2)"][i], 10)
        ax.plot(vg,id_curve,label=f"Sample {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg Scaling")
    ax.legend()
    st.pyplot(fig)

    # --- Export buttons ---
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv_bytes, "synthetic_finfet.csv")

    excel_bytes = BytesIO()
    df.to_excel(excel_bytes, index=False)
    st.download_button("⬇️ Download Excel", excel_bytes.getvalue(), "synthetic_finfet.xlsx")

    pdf_bytes = export_pdf(df)
    st.download_button("⬇️ Download PDF", pdf_bytes, "synthetic_finfet.pdf")

# --- PDF export with embedded logo ---
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    # Logo
    try:
        pdf.image("logo.png", x=10, y=8, w=30)
    except:
        pass
    pdf.set_font("Arial", "B", 12)
    pdf.ln(20)
    for col in df.columns:
        pdf.cell(30,10,str(col),1)
    pdf.ln()
    for i in range(len(df)):
        for col in df.columns:
            val = df[col][i]
            if isinstance(val,list):
                val = str(val)
            pdf.cell(30,10,val,1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin1")

# --- Main logic ---
if uploaded_file is not None:
    text = ocr_file(uploaded_file)
    if text:
        params = extract_params(text)
        st.subheader("Extracted Parameters")
        st.table(params)
else:
    if st.button("Use Synthetic Demo"):
        show_synthetic_demo()
