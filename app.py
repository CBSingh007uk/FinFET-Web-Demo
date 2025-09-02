import streamlit as st
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import numpy as np
import io
import traceback

# --- Streamlit Page Config ---
st.set_page_config(page_title="Data Extractor", layout="wide", page_icon="📄")

# --- Custom CSS ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(to bottom right, #f0f9ff, #cbebff);
        }
        header, footer {visibility: hidden;}
        .main-header {
            font-size: 2rem;
            font-weight: bold;
            padding: 1rem;
            text-align: center;
            color: white;
            background: linear-gradient(90deg, #0077b6, #00b4d8);
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .stButton>button {
            background-color: #0077b6 !important;
            color: white !important;
            border: none;
            padding: 0.6em 1.2em;
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #023e8a !important;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Extract Text", "About"])

st.sidebar.markdown("---")
st.sidebar.info("Powered by **Streamlit + EasyOCR + PyMuPDF**")

# --- Main Header ---
st.markdown('<div class="main-header">📄 Data Extractor</div>', unsafe_allow_html=True)

if page == "Extract Text":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file:
        try:
            st.write("### Processing File...")
            file_bytes = uploaded_file.read()

            # Step 1: Load PDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            st.success(f"Loaded PDF with {doc.page_count} pages")

            # Step 2: Initialize OCR
            with st.spinner("Loading EasyOCR model..."):
                reader = easyocr.Reader(['en'])

            # Step 3: Extract text page-by-page
            all_text = []
            progress = st.progress(0)
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                img_np = np.array(img)
                result = reader.readtext(img_np)
                page_text = " ".join([r[1] for r in result])
                all_text.append(f"--- Page {i+1} ---\n{page_text}\n")
                progress.progress((i+1)/len(doc))

            st.success("Extraction complete!")
            st.text_area("Extracted Text", "\n\n".join(all_text), height=400)

        except Exception as e:
            st.error("### Processing error occurred!")
            st.code(traceback.format_exc())  # Show full traceback for debugging

else:
    st.subheader("About This App")
    st.markdown("""
        **Data Extractor** lets you:
        - Upload any PDF document  
        - Convert each page into an image  
        - Use **EasyOCR** to read text directly from page images  
        - Display extracted text in a clean interface  

        **Tech stack:**  
        - [Streamlit](https://streamlit.io) for the web UI  
        - [PyMuPDF](https://pymupdf.readthedocs.io/) to parse PDFs  
        - [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition  
    """)

