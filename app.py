import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import easyocr
from fpdf import FPDF
from pdf2image import convert_from_bytes

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="FinFET Data Extractor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CSS -----------------
st.markdown("""
<style>
body {
    background-color: #1e1e2f;
    color: #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #2e2e44;
    color: #e0e0e0;
}
.stButton>button {
    color: white;
    background: linear-gradient(to right, #4CAF50, #2E8B57);
    border-radius: 12px;
    height: 3em;
    width: 12em;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ----------------- LOG FUNCTION -----------------
def log(message, center=True):
    if center:
        st.text(message)
    st.sidebar.text(message)

# ----------------- LOGO -----------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=150)
except Exception:
    log("Logo not found, using default title.")

st.title("🔬 FinFET Data Extractor")
st.sidebar.title("🔬 Logs")

# ----------------- FILE UPLOADER -----------------
uploaded_file = st.file_uploader(
    "Upload a PDF or Image (PNG/JPG/JPEG)",
    type=["pdf", "png", "jpg", "jpeg"]
)

use_synthetic = st.button("Use Synthetic Demo")

# ----------------- SYNTHETIC DATA -----------------
def synthetic_data():
    np.random.seed(0)
    n_samples = 5
    df = pd.DataFrame({
        "Lg (nm)": np.random.uniform(3,5,n_samples),
        "Hfin (nm)": np.random.uniform(20,35,n_samples),
        "EOT (nm)": np.random.uniform(0.7,1.2,n_samples),
        "Vth (V)": np.random.uniform(0.2,0.5,n_samples),
        "ID (A/cm2)": np.random.uniform(1e-5,1e-3,n_samples),
        "Ion/Ioff": np.random.uniform(1e3,1e5,n_samples),
        "gm (S)": np.random.uniform(1e-3,0.1,n_samples),
        "Rsd (Ohm)": np.random.uniform(10,100,n_samples),
        "Capacitance (fF)": np.random.uniform(0.1,5,n_samples),
        "Delay (ps)": np.random.uniform(1,20,n_samples),
        "Vg (V)": [np.linspace(0, 1, 50) for _ in range(n_samples)]
    })
    return df

# ----------------- PDF EXPORT -----------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Synthetic FinFET Parameters", ln=True, align="C")
    try:
        pdf.image("logo.png", x=10, y=10, w=30)
    except:
        pass
    pdf.ln(20)
    pdf.set_font("Arial", "", 12)
    for i in range(len(df)):
        for col in df.columns[:-1]:  # skip Vg
            pdf.cell(0, 8, f"{col}: {df[col][i]}", ln=True)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin1")

# ----------------- OCR FUNCTION -----------------
def run_ocr(img):
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(np.array(img))
        text = "\n".join([r[1] for r in result])
        return text
    except Exception as e:
        log(f"OCR error: {e}")
        return ""

# ----------------- MAIN -----------------
if uploaded_file or use_synthetic:
    if use_synthetic:
        df = synthetic_data()
        st.subheader("Synthetic FinFET Demo Data")
        st.dataframe(df.drop(columns=["Vg"]))
        # Scaling plot
        st.subheader("Scaling Plots (ID vs Vg)")
        fig, ax = plt.subplots()
        for i in range(len(df)):
            ax.plot(df["Vg"][i], np.linspace(0, df["ID (A/cm2)"][i], len(df["Vg"][i])), label=f"Sample {i+1}")
        ax.set_xlabel("Vg (V)")
        ax.set_ylabel("ID (A/cm²)")
        ax.legend()
        st.pyplot(fig)

        # Download buttons
        st.download_button("⬇️ Download CSV", df.drop(columns=["Vg"]).to_csv(index=False), "synthetic_finfet.csv")
        st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")
        log("Synthetic demo generated.", center=False)

    else:
        try:
            if uploaded_file.type == "application/pdf":
                images = convert_from_bytes(uploaded_file.read())
                img = images[0]
            else:
                img = Image.open(uploaded_file)

            st.image(img, caption="Input Image", use_container_width=True)
            text = run_ocr(img)
            st.subheader("Extracted Text")
            st.text(text)
            log("OCR completed.", center=False)

            # TODO: Add regex-based parameter extraction here

        except Exception as e:
            log(f"Error processing file: {e}")
else:
    st.info("Upload a file or use the Synthetic Demo button.")
