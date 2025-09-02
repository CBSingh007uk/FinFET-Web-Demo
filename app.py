import streamlit as st
from PIL import Image
import pytesseract
import io

# Optional: PDF → Image conversion
from pdf2image import convert_from_bytes

# --- Page config ---
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔬", layout="centered")

# --- CSS for colors & buttons ---
st.markdown("""
    <style>
        .main {background-color: #f0f4ff;}
        .stButton>button {
            color: white;
            background-color: #4CAF50;
            border-radius: 12px;
            height: 3em;
            width: 10em;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Logo & Title ---
st.image("logo.png", width=150)
st.title("FinFET Data Extractor")
st.markdown("**Upload PDF/Image → OCR → Extract Parameters**")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

# --- Synthetic fallback if no file ---
use_synthetic = False
if uploaded_file is None:
    if st.button("Use Synthetic Demo"):
        use_synthetic = True
        # Create synthetic image
        img = Image.new("RGB", (400, 200), color=(255, 255, 255))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((10, 80), "Hello Tesseract!", fill=(0, 0, 0))
        st.info("Using synthetic demo image")
else:
    if uploaded_file.type == "application/pdf":
        images = convert_from_bytes(uploaded_file.read())
        img = images[0]  # Take first page
    else:
        img = Image.open(uploaded_file)

# --- Display image & OCR ---
if uploaded_file is not None or use_synthetic:
    st.image(img, caption="Input Image", use_column_width=True)

    # --- OCR ---
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ckushwah\tesseract.exe"  # For local, ignored on hosted
    text = pytesseract.image_to_string(img)

    st.subheader("Extracted Text")
    st.text(text)

    # --- Dummy parameter extraction ---
    st.subheader("Extracted Parameters")
    st.markdown("""
    - Gate length: **20nm (detected)**  
    - Fin height: **40nm (detected)**  
    - EOT: **0.8nm (detected)**  
    """)

else:
    st.info("Upload a file or use the synthetic demo.")
