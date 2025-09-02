import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# --- PAGE CONFIG ---
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stApp {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #1F6FEB;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stSidebar {
        background-color: #1E1E1E !important;
        color: #FFFFFF;
    }
    .block-container {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align:center; color:white;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:#BBBBBB;'>Upload PDF/Image or Use Synthetic Demo</h4>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.markdown("### Navigation")
demo_mode = st.sidebar.checkbox("Use Synthetic Demo", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**Output Options:**")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

# --- OCR READER ---
reader = easyocr.Reader(['en'])

# --- DATA EXTRACTION FUNCTION ---
def extract_text_from_pdf(file):
    text_blocks = []
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text_blocks.append(page.get_text())
        return "\n".join(text_blocks)
    except Exception as e:
        st.error(f"PDF Extraction Error: {e}")
        return ""

def extract_text_from_image(file):
    try:
        results = reader.readtext(file.read())
        return "\n".join([res[1] for res in results])
    except Exception as e:
        st.error(f"Image OCR Error: {e}")
        return ""

def parse_parameters(text):
    # --- Fake parser for demo ---
    return {
        "Lg (nm)": 14,
        "Hfin (nm)": 35,
        "EOT (nm)": 0.8,
        "Id (µA/µm)": 1200
    }

# --- MAIN LOGIC ---
if demo_mode:
    st.info("**Demo Mode Active** – Using synthetic FinFET data.")
    extracted_text = "Synthetic Id-Vg data for FinFET: Lg=14nm, Hfin=35nm, EOT=0.8nm, Id=1200uA/um"
else:
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = extract_text_from_image(uploaded_file)
    else:
        st.warning("Upload a file or enable Demo Mode.")
        st.stop()

# --- PARAMETER EXTRACTION ---
parameters = parse_parameters(extracted_text)
df = pd.DataFrame(list(parameters.items()), columns=["Parameter", "Value"])

# --- DISPLAY RESULTS ---
st.subheader("Extracted Parameters")
st.dataframe(df, use_container_width=True)

# --- DOWNLOAD OUTPUT ---
output_format = st.sidebar.radio("Select Export Format:", ["Excel", "CSV", "PDF"])
st.sidebar.markdown("Click below to download:")

def download_excel():
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return buf

def download_csv():
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf

def download_pdf_with_logo():
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>FinFET Extracted Parameters</b>", styles['Title']))
    elements.append(Spacer(1, 20))
    for _, row in df.iterrows():
        elements.append(Paragraph(f"{row['Parameter']}: {row['Value']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    try:
        elements.append(Image("logo.png", width=100, height=100))
    except:
        elements.append(Paragraph("Logo not found.", styles['Normal']))
    doc.build(elements)
    buf.seek(0)
    return buf

if output_format == "Excel":
    st.sidebar.download_button("Download Excel", download_excel(), "finfet_data.xlsx")
elif output_format == "CSV":
    st.sidebar.download_button("Download CSV", download_csv(), "finfet_data.csv")
else:
    st.sidebar.download_button("Download PDF", download_pdf_with_logo(), "finfet_data.pdf")

# --- DEBUG SECTION ---
with st.expander("Debug Info"):
    st.text_area("Raw Extracted Text", extracted_text, height=200)
