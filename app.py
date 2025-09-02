# app.py
import streamlit as st
from PIL import Image, ImageDraw
import pytesseract
import fitz  # PyMuPDF
import re
import io

# --- Page Config ---
st.set_page_config(
    page_title="FinFET Data Extractor",
    page_icon="🔬",
    layout="centered"
)

# --- Custom CSS for colorful buttons & background ---
st.markdown("""
    <style>
        .stApp {background-color: #f0f4ff;}
        .stButton>button {
            color: white;
            background-color: #4CAF50;
            border-radius: 12px;
            height: 3em;
            width: 12em;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Logo & Title ---
st.image("logo.png", width=150)  # Replace with your logo
st.title("FinFET Data Extractor")
st.markdown("**Upload PDF/Image → OCR → Extract Parameters**")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
use_synthetic = False

if uploaded_file is None:
    if st.button("Use Synthetic Demo"):
        use_synthetic = True
        # Create synthetic image with FinFET parameters
        img = Image.new("RGB", (500, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        text = "Device Type: FinFET\nLg = 16 nm\nHfin = 35 nm\nEOT = 0.9 nm"
        draw.text((20, 50), text, fill=(0, 0, 0))
        st.info("Using synthetic demo image")
else:
    if uploaded_file.type == "application/pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]  # first page
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        img = Image.open(uploaded_file)

# --- Display image & OCR ---
if uploaded_file is not None or use_synthetic:
    st.image(img, caption="Input Image", use_container_width=True)

    # --- OCR ---
    text = pytesseract.image_to_string(img)

    st.subheader("Extracted Text")
    st.text(text)

    # --- Parameter extraction ---
    st.subheader("Extracted Parameters")
    params = {}
    for key in ["Lg", "Hfin", "EOT"]:
        match = re.search(rf"{key}\s*=\s*([\d.]+)", text)
        if match:
            params[key] = f"{match.group(1)} nm"

    if params:
        for k, v in params.items():
            st.markdown(f"- **{k}**: {v}")
    else:
        st.markdown("No parameters detected. Using synthetic demo.")

else:
    st.info("Upload a file or use the synthetic demo button to begin.")
