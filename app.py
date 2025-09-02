import streamlit as st
from PIL import Image, ImageDraw
import fitz  # PyMuPDF
import easyocr
import re
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="FinFET Data Extractor",
    page_icon="🔬",
    layout="wide"
)

# --- Custom CSS for enhanced styling ---
st.markdown("""
    <style>
        /* Gradient background */
        .stApp {
            background: linear-gradient(135deg, #e0f7fa 0%, #e1bee7 100%);
            font-family: 'Arial', sans-serif;
        }

        /* Buttons */
        .stButton>button {
            color: white;
            background: linear-gradient(90deg, #4CAF50, #81C784);
            border-radius: 15px;
            height: 3em;
            width: 14em;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #81C784, #4CAF50);
            transform: scale(1.05);
        }

        /* Card-style sections */
        .stText, .stMarkdown {
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 12px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }

        /* Headers */
        h1, h2, h3 {
            color: #4A148C;
            font-family: 'Helvetica', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# --- Logo & Title ---
st.image("logo.png", width=180)
st.markdown("<h1 style='text-align:center'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center'>Upload PDF/Image → OCR → Extract Parameters</h3>", unsafe_allow_html=True)

# --- File uploader ---
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
use_synthetic = False

if uploaded_file is None:
    if st.button("Use Synthetic Demo"):
        use_synthetic = True
        img = Image.new("RGB", (500, 200), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        text = "Device Type: FinFET\nLg = 16 nm\nHfin = 35 nm\nEOT = 0.9 nm"
        draw.text((20, 50), text, fill=(0, 0, 0))
        st.info("Using synthetic demo image")
else:
    if uploaded_file.type == "application/pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        img = Image.open(uploaded_file)

# --- Display image & OCR ---
if uploaded_file is not None or use_synthetic:
    st.image(img, caption="Input Image", use_container_width=True)

    # --- OCR using EasyOCR ---
    reader = easyocr.Reader(['en'], gpu=False)
    img_array = np.array(img)
    text_results = reader.readtext(img_array)
    text = "\n".join([t[1] for t in text_results])

    # --- OCR Output Card ---
    st.subheader("Extracted Text")
    st.markdown(f"<div style='background: rgba(255,255,255,0.85); padding:15px; border-radius:12px;'>{text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    # --- Parameter Extraction Card ---
    st.subheader("Extracted Parameters")
    params = {}
    for key in ["Lg", "Hfin", "EOT"]:
        match = re.search(rf"{key}\s*=\s*([\d.]+)", text)
        if match:
            params[key] = f"{match.group(1)} nm"

    if params:
        param_text = "".join([f"- **{k}**: {v}<br>" for k,v in params.items()])
        st.markdown(f"<div style='background: rgba(255,255,255,0.85); padding:15px; border-radius:12px;'>{param_text}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background: rgba(255,255,255,0.85); padding:15px; border-radius:12px;'>No parameters detected. Using synthetic demo.</div>", unsafe_allow_html=True)

else:
    st.info("Upload a file or use the synthetic demo button to begin.")
