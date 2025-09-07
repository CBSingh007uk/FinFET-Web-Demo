import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# Attempt to import EasyOCR
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# App configuration
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# Dark theme colors
BG_COLOR = "#1f1f1f"
TEXT_COLOR = "#e0e0e0"
ACCENT_COLOR = "#00bfff"
SIDEBAR_COLOR = "#272727"

# Sidebar logo
logo_img = Image.new("RGBA", (200, 50), color=(0, 191, 255))
draw = ImageDraw.Draw(logo_img)
draw.text((10, 10), "FinFET Data Extractor", fill="white")
st.sidebar.image(logo_img, use_column_width=True)

# Sidebar navigation
mode = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Upload PDF/Image"])
st.sidebar.markdown("---")
st.sidebar.write("Logs:")

def log(msg):
    st.sidebar.write(msg)
    st.write(msg)

# Utility: PDF export
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    # Embed logo
    pdf.image(BytesIO(logo_img.tobytes()), x=10, y=8, w=60)
    pdf.set_font("Arial", size=10)
    pdf.ln(20)
    for i, row in df.iterrows():
        pdf.cell(0, 8, ", ".join(f"{col}: {row[col]}" for col in df.columns), ln=True)
    # Unicode-safe output
    return pdf.output(dest="S").encode("utf-8")

# Generate synthetic demo data
def generate_synthetic_data(n_devices=5):
    data = []
    for i in range(n_devices):
        Vg = np.linspace(0, 1.0, 50)
        ID = np.random.rand(50) * 1e-4
        Lg = np.random.choice([3, 5]) * 1e-9
        Hfin = np.random.rand() * 10e-9
        EOT = np.random.rand() * 2e-9
        Vth = np.random.rand() * 0.5
        IonIoff = np.random.rand() * 1e5
        gm = np.random.rand() * 1e-3
        Rsd = np.random.rand() * 10
        Cgs = np.random.rand() * 1e-15
        Cgd = np.random.rand() * 1e-15
        Delay = np.random.rand() * 1e-12
        data.append({
            "Vg": Vg, "ID (A/cm2)": ID, "Lg": Lg, "Hfin": Hfin, "EOT": EOT, 
            "Vth": Vth, "Ion/Ioff": IonIoff, "gm": gm, "Rsd": Rsd,
            "Cgs": Cgs, "Cgd": Cgd, "Delay": Delay
        })
    return data

def show_synthetic_demo():
    st.header("Synthetic FinFET Demo")
    data = generate_synthetic_data()
    
    # Display in scrollable table
    table_data = pd.DataFrame({
        "Device": [f"Device {i+1}" for i in range(len(data))],
        "Lg (nm)": [d["Lg"]*1e9 for d in data],
        "Hfin (nm)": [d["Hfin"]*1e9 for d in data],
        "EOT (nm)": [d["EOT"]*1e9 for d in data],
        "Vth (V)": [d["Vth"] for d in data],
        "Ion/Ioff": [d["Ion/Ioff"] for d in data],
        "gm (S)": [d["gm"] for d in data],
        "Rsd (Ohm)": [d["Rsd"] for d in data],
        "Cgs (F)": [d["Cgs"] for d in data],
        "Cgd (F)": [d["Cgd"] for d in data],
        "Delay (s)": [d["Delay"] for d in data]
    })
    st.dataframe(table_data, use_container_width=True)

    # Plot scaling curves
    fig, ax = plt.subplots()
    for i, d in enumerate(data):
        ax.plot(d["Vg"], d["ID (A/cm2)"], marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)", color=TEXT_COLOR)
    ax.set_ylabel("ID (A/cm2)", color=TEXT_COLOR)
    ax.set_title("Scaling Curves", color=TEXT_COLOR)
    ax.legend()
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    st.pyplot(fig)

    # Download buttons
    df_download = pd.DataFrame({
        "Device": [f"Device {i+1}" for i in range(len(data))],
        "Lg (nm)": [d["Lg"]*1e9 for d in data],
        "Hfin (nm)": [d["Hfin"]*1e9 for d in data],
        "EOT (nm)": [d["EOT"]*1e9 for d in data],
        "Vth (V)": [d["Vth"] for d in data],
        "Ion/Ioff": [d["Ion/Ioff"] for d in data],
        "gm (S)": [d["gm"] for d in data],
        "Rsd (Ohm)": [d["Rsd"] for d in data],
        "Cgs (F)": [d["Cgs"] for d in data],
        "Cgd (F)": [d["Cgd"] for d in data],
        "Delay (s)": [d["Delay"] for d in data]
    })
    st.download_button("⬇️ Download CSV", df_download.to_csv(index=False).encode('utf-8'), "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df_download), "synthetic_finfet.pdf")

def show_upload_demo():
    st.header("Upload PDF/Image")
    uploaded_file = st.file_uploader("Choose a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.write("File uploaded:", uploaded_file.name)
        if OCR_AVAILABLE:
            reader = easyocr.Reader(['en'])
            text_result = " ".join(reader.readtext(uploaded_file.getvalue(), detail=0))
        else:
            text_result = "OCR not available. Simulated extraction: ID=1e-4 A/cm2, Vth=0.3 V"
        st.text_area("Extracted Text / Parameters", text_result, height=300)

# Main
st.markdown(f"<div style='background:linear-gradient(90deg,{ACCENT_COLOR},{BG_COLOR});padding:10px'><h1 style='color:{TEXT_COLOR}'>FinFET Data Extractor</h1></div>", unsafe_allow_html=True)

if mode == "Synthetic Demo":
    show_synthetic_demo()
else:
    show_upload_demo()
