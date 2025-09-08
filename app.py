import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import fitz  # PyMuPDF
import easyocr
from PIL import Image, ImageOps

st.set_page_config(page_title="FinFET Data Extractor",
                   layout="wide",
                   initial_sidebar_state="expanded")

# -----------------------------
# Utility Functions
# -----------------------------

def contrast_text_color(bg_color):
    """Return black or white depending on background brightness."""
    r, g, b = bg_color
    brightness = (r*299 + g*587 + b*114) / 1000
    return (0,0,0) if brightness > 125 else (255,255,255)

def extract_text_from_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image(image_file):
    try:
        img = Image.open(image_file)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(np.array(img))
        text = "\n".join([r[1] for r in result])
        return text
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return ""

def export_pdf(df, logo_img=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    if logo_img:
        # Convert PIL image to temporary PNG in memory
        logo_bytes = BytesIO()
        logo_img.save(logo_bytes, format="PNG")
        logo_bytes.seek(0)
        pdf.image(logo_bytes, x=10, y=8, w=40)
        pdf.ln(25)
    for i, col in enumerate(df.columns):
        pdf.cell(40, 10, col, 1)
    pdf.ln()
    for idx, row in df.iterrows():
        for val in row:
            pdf.cell(40, 10, str(val), 1)
        pdf.ln()
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.image("logo.png", width=120)  # add your logo file
mode = st.sidebar.radio("Mode", ["Upload PDF/Image", "Synthetic Demo"])
st.sidebar.markdown("---")
log_sidebar = st.sidebar.empty()

# -----------------------------
# Main Page
# -----------------------------
st.markdown("<h1 style='text-align:center;color:lightblue;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
log_main = st.empty()

# -----------------------------
# Synthetic Demo Parameters
# -----------------------------
synthetic_df = pd.DataFrame({
    "Lg (nm)": [3, 4, 5],
    "Hfin (nm)": [6, 7, 8],
    "EOT (nm)": [1.2, 1.1, 1.0],
    "Vg (V)": [np.linspace(0,1,50) for _ in range(3)],
    "ID (A/cm2)": [np.linspace(0,1e5,50) for _ in range(3)],
    "Vth (V)": [0.3,0.32,0.35],
    "Ion/Ioff": [15,17,20],
    "gm (S)": [1.5e-3,1.6e-3,1.7e-3],
    "Rsd (Ohm)": [150,145,140],
    "Capacitance (fF)": [0.12,0.11,0.10],
    "Delay (ps)": [10,9.5,9]
})

# -----------------------------
# Show Synthetic Demo
# -----------------------------
def show_synthetic_demo():
    st.subheader("Synthetic FinFET Demo Data")
    st.write(synthetic_df.drop(columns=["Vg","ID (A/cm2)"]))
    log_main.text("Showing synthetic FinFET parameters")
    log_sidebar.text("Synthetic Demo Mode Active")

    # Scaling plots
    st.subheader("ID vs Vg Scaling Plot")
    fig, ax = plt.subplots()
    for i in range(len(synthetic_df)):
        ax.plot(synthetic_df["Vg (V)"][i], synthetic_df["ID (A/cm2)"][i],
                marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.legend()
    st.pyplot(fig)

    # Export options
    df_download = synthetic_df.drop(columns=["Vg (V)","ID (A/cm2)"])
    st.download_button("⬇️ Download CSV", df_download.to_csv(index=False).encode(), "synthetic_finfet.csv")
    st.download_button("⬇️ Download Excel", df_download.to_excel(index=False).encode(), "synthetic_finfet.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df_download, logo_img=Image.open("logo.png")), "synthetic_finfet.pdf")

# -----------------------------
# Upload Mode
# -----------------------------
def show_upload_mode():
    uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf","png","jpg","jpeg"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = extract_text_from_image(uploaded_file)
        st.subheader("Extracted Text")
        st.text_area("Text", text, height=300)
        log_main.text("Upload Mode: Extraction Complete")
        log_sidebar.text("Upload Mode Active")

# -----------------------------
# Main Logic
# -----------------------------
if mode == "Synthetic Demo":
    show_synthetic_demo()
else:
    show_upload_mode()
