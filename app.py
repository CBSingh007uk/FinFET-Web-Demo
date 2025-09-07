import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# ---------- CONFIG ----------
st.set_page_config(page_title="FinFET Data Extractor",
                   page_icon="🔍",
                   layout="wide")

# ---------- THEME ----------
BACKGROUND_COLOR = "#1E1E2F"
TEXT_COLOR = "#E0E0E0"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    .sidebar .sidebar-content {{
        background-color: #2E2E3F;
        color: {TEXT_COLOR};
    }}
    .stButton>button {{
        background-color: #4E4EFF;
        color: #FFFFFF;
        border-radius: 8px;
        padding: 0.5em 1em;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- LOGO ----------
def generate_logo():
    img = Image.new('RGBA', (200, 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((10,10), "FinFET Extractor", fill=(255,255,255,255), font=font)
    return img

logo_img = generate_logo()
st.sidebar.image(logo_img, use_column_width=True)

# ---------- SIDEBAR OPTIONS ----------
option = st.sidebar.selectbox("Select Mode:", ["Synthetic Demo", "Upload PDF/Image"])

# ---------- PDF EXPORT ----------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    # Embed logo
    logo_buffer = BytesIO()
    logo_img.save(logo_buffer, format="PNG")
    logo_buffer.seek(0)
    pdf.image(logo_buffer, x=10, y=8, w=60)
    pdf.set_font("Arial", size=10)
    pdf.ln(20)
    for i, row in df.iterrows():
        pdf.cell(0, 8, ", ".join(f"{col}: {row[col]}" for col in df.columns), ln=True)
    return pdf.output(dest="S").encode("utf-8")

# ---------- SYNTHETIC DEMO ----------
def show_synthetic_demo():
    st.subheader("Synthetic FinFET Data (3–5 nm node)")

    # Example parameters
    data = {
        "Device": ["FinFET1", "FinFET2", "FinFET3"],
        "Lg (nm)": [5, 4, 3],
        "Hfin (nm)": [20, 22, 18],
        "EOT (nm)": [1.2, 1.1, 1.0],
        "Vth (V)": [0.3, 0.32, 0.28],
        "ID (A/cm2)": [1.2e3, 1.5e3, 1.1e3],
        "Ion/Ioff": [1e5, 1.2e5, 0.9e5],
        "gm (mS)": [2.1, 2.5, 1.8],
        "Rsd (Ω)": [150, 145, 160],
        "Cgg (fF)": [1.2, 1.3, 1.1],
        "Delay (ps)": [10, 9, 11],
        "Vg (V)": [list(np.linspace(0, 1.0, 50))]*3
    }

    df = pd.DataFrame(data)

    # Table with horizontal scroll
    st.dataframe(df, use_container_width=True)

    # Scaling plots
    st.subheader("ID vs Vg Scaling Plot")
    fig, ax = plt.subplots()
    for i in range(len(df)):
        ax.plot(df["Vg"][i], np.linspace(0, df["ID (A/cm2)"][i], len(df["Vg"][i])),
                marker='o', label=df["Device"][i])
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.legend()
    st.pyplot(fig)

    # Download options
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode("utf-8"), "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

# ---------- MAIN ----------
if option == "Synthetic Demo":
    show_synthetic_demo()
else:
    st.subheader("Upload PDF/Image for OCR and Parameter Extraction")
    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.info("OCR processing not implemented in this demo.")
        st.write("File uploaded:", uploaded_file.name)
