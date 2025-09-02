# app.py
import streamlit as st
from PIL import Image, ImageDraw
import pytesseract
from pdf2image import convert_from_bytes
import re
import qrcode
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

# --- QR Code for poster ---
st.subheader("Scan QR Code to Open Live Demo")

# Replace with your deployed Streamlit app URL
app_url = "https://your-app.streamlit.app"

# Generate QR code
qr_img = qrcode.make(app_url)
qr_img = qr_img.convert("RGB")  # Ensure proper format for Streamlit

# Display QR code
st.image(qr_img, caption="Scan to open the FinFET Data Extractor", use_container_width=False)

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
        images = convert_from_bytes(uploaded_file.read())
        img = images[0]  # Take first page
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
