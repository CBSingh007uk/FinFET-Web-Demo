import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw
import io
from fpdf import FPDF
import easyocr

# -----------------------------
# Page config and theme
# -----------------------------
st.set_page_config(
    page_title="FinFET Data Extractor",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS for dark theme and styled buttons
# -----------------------------
st.markdown("""
<style>
body {
    background-color: #1e1e2f;
    color: #e0e0e0;
}
.sidebar .sidebar-content {
    background-color: #2a2a3d;
}
.stButton>button {
    color: white;
    background: linear-gradient(90deg, #4CAF50, #2e7d32);
    border-radius: 12px;
    height: 3em;
    width: 10em;
    font-size: 16px;
}
h1, h2, h3, h4, h5 {
    color: #00bfff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logo
# -----------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=150)
except:
    st.warning("Logo not found")

st.title("FinFET Data Extractor")
st.markdown("Upload PDF/Image → OCR → Extract Parameters")

# -----------------------------
# Sidebar log
# -----------------------------
st.sidebar.header("Logs")
log_container = st.sidebar.empty()
log_messages = []

def log(msg):
    log_messages.append(msg)
    log_container.text("\n".join(log_messages))
    st.text("\n".join(log_messages))  # also center

# -----------------------------
# Synthetic demo data
# -----------------------------
def get_synthetic_data():
    # 5nm node synthetic FinFET data
    Vg = np.linspace(0, 1.0, 10)
    data = {
        "Lg": [5]*10,
        "Hfin": [35]*10,
        "EOT": [0.8]*10,
        "ID (A/cm2)": np.random.rand(10)*1e3,
        "Vth": np.random.rand(10)*0.3+0.3,
        "Ion/Ioff": np.random.rand(10)*1e3,
        "gm": np.random.rand(10)*5,
        "Rsd": np.random.rand(10)*100,
        "Capacitance (fF)": np.random.rand(10)*2,
        "Delay (ps)": np.random.rand(10)*50,
        "Vg": [Vg]*10  # for plotting
    }
    df = pd.DataFrame(data)
    return df

# -----------------------------
# Export PDF
# -----------------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Synthetic FinFET Data Extractor", ln=True, align="C")
    try:
        pdf.image("logo.png", x=80, y=15, w=50)
    except:
        pass
    pdf.ln(40)
    pdf.set_font("Arial", "", 12)
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    for idx, row in df.iterrows():
        for val in row:
            pdf.cell(40, 10, str(round(val, 3)) if isinstance(val, (int,float,np.float64)) else str(val), 1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin1")

# -----------------------------
# Show synthetic demo
# -----------------------------
def show_synthetic_demo():
    df = get_synthetic_data()
    st.subheader("Synthetic Demo Data")
    st.dataframe(df, use_container_width=True)

    # Scaling plots
    st.subheader("Scaling Plots")
    fig, ax = plt.subplots(figsize=(8,4))
    for i in range(len(df)):
        ax.plot(df["Vg"][i], df["ID (A/cm2)"][i], marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg")
    ax.legend()
    st.pyplot(fig)

    # Download buttons
    st.subheader("Download Options")
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

# -----------------------------
# Main App Logic
# -----------------------------
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf","png","jpg","jpeg"])

if uploaded_file:
    log(f"File uploaded: {uploaded_file.name}")
    st.info("File upload detected. OCR not implemented in this demo.")
else:
    if st.button("Use Synthetic Demo"):
        log("Using synthetic demo")
        show_synthetic_demo()
