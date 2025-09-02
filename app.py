import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import io
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Data Extractor Demo",
    page_icon="📊",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    /* Gradient header */
    .gradient-header {
        font-size: 28px;
        font-weight: bold;
        background: linear-gradient(90deg, #ff4b1f, #1fddff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.5rem;
    }
    /* Styled buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b1f, #1fddff);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
    }
    /* Sidebar logo */
    [data-testid="stSidebar"] {
        background-color: #1a1c23;
    }
</style>
""", unsafe_allow_html=True)

# ---------- LOGO ----------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/512px-React-icon.svg.png", width=120)
st.sidebar.title("Data Extractor")
st.sidebar.markdown("**Demo for poster presentation**")

# ---------- SIDEBAR NAVIGATION ----------
page = st.sidebar.radio("Navigate", ["Home", "Upload", "Demo"])

# ---------- OCR + PDF HELPER ----------
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_pdf(file_bytes):
    text_output = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text_output += page.get_text()
    except Exception as e:
        st.error("PDF parsing failed. Check file format.")
        st.text(f"DEBUG: {e}")
    return text_output

def ocr_from_pdf_images(file_bytes):
    text_output = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_index in range(len(doc)):
            pix = doc[page_index].get_pixmap()
            img_bytes = pix.tobytes("png")
            results = reader.readtext(img_bytes, detail=0)
            text_output += "\n".join(results) + "\n"
    except Exception as e:
        st.error("OCR failed.")
        st.text(f"DEBUG: {e}")
    return text_output

def synthetic_parameters():
    data = {
        "Gate Length (nm)": [12, 14, 16],
        "Fin Height (nm)": [35, 40, 45],
        "EOT (nm)": [0.7, 0.65, 0.6],
        "Ion (µA/µm)": [1020, 980, 1100],
        "Ioff (nA/µm)": [5, 7, 6]
    }
    return pd.DataFrame(data)

# ---------- PAGES ----------
if page == "Home":
    st.markdown('<div class="gradient-header">Welcome to Data Extractor</div>', unsafe_allow_html=True)
    st.write("""
    This web app demonstrates:
    - PDF text + image OCR extraction  
    - Automatic FinFET parameter detection (synthetic demo)  
    - Export results as CSV/XLSX  
    - Mobile-ready via Streamlit Community Cloud  
    """)

elif page == "Upload":
    st.markdown('<div class="gradient-header">Upload PDF to Extract Parameters</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        try:
            with st.spinner("Extracting text and parameters..."):
                # Extract text
                pdf_text = extract_text_from_pdf(uploaded_file.read())
                # OCR from images too
                uploaded_file.seek(0)
                ocr_text = ocr_from_pdf_images(uploaded_file.read())
                combined_text = pdf_text + "\n" + ocr_text

                st.subheader("Raw Extracted Text")
                st.text_area("Combined Text", combined_text, height=200)

                # For demo: Generate synthetic parameters
                df = synthetic_parameters()
                st.subheader("Extracted Parameters (Synthetic)")
                st.dataframe(df)

                # Download options
                csv_bytes = df.to_csv(index=False).encode()
                xlsx_io = io.BytesIO()
                df.to_excel(xlsx_io, index=False)
                xlsx_io.seek(0)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("Download CSV", csv_bytes, "parameters.csv", "text/csv")
                with col2:
                    st.download_button("Download XLSX", xlsx_io, "parameters.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error("Error processing file.")
            st.text(f"DEBUG: {e}")

elif page == "Demo":
    st.markdown('<div class="gradient-header">Synthetic Demo Mode</div>', unsafe_allow_html=True)
    st.write("Showing sample extracted parameters:")
    df = synthetic_parameters()
    st.dataframe(df)
    csv_bytes = df.to_csv(index=False).encode()
    xlsx_io = io.BytesIO()
    df.to_excel(xlsx_io, index=False)
    xlsx_io.seek(0)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download CSV", csv_bytes, "demo_parameters.csv", "text/csv")
    with col2:
        st.download_button("Download XLSX", xlsx_io, "demo_parameters.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
