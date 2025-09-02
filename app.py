import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import numpy as np
import io
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Helper: auto text color detection
# -----------------------------
def get_contrasting_text_color(bg_color):
    # bg_color is hex (e.g. "#123456")
    bg_color = bg_color.lstrip('#')
    r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return "#FFFFFF" if luminance < 128 else "#000000"

# -----------------------------
# Helper: extract text from PDF
# -----------------------------
def extract_text_from_pdf(file_bytes):
    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# -----------------------------
# Helper: synthetic parameter extractor
# -----------------------------
def extract_parameters(text):
    # In a real app: NLP + regex + ML
    # For demo: return synthetic data
    return pd.DataFrame({
        "Parameter": ["Lg (nm)", "Hfin (nm)", "EOT (nm)", "Id (uA/um)", "Vth (V)"],
        "Value": [12, 35, 0.8, 420, 0.42]
    })

# -----------------------------
# Helper: export dataframe to PDF with logo
# -----------------------------
def export_pdf_with_logo(df, logo_path="logo.png"):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image as RLImage, Spacer
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Add logo at top
    try:
        logo = RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        elements.append(logo)
        elements.append(Spacer(1, 0.2*inch))
    except:
        pass  # no logo

    # Add table
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#333333")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#DDDDDD")),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="FinFET Parameter Extractor", layout="wide")

# -----------------------------
# Sidebar with logo
# -----------------------------
st.sidebar.image("logo.png", width=150)
st.sidebar.title("FinFET Data Extractor")
st.sidebar.markdown("Upload a PDF or use the demo mode below.")
demo_mode = st.sidebar.checkbox("Use synthetic demo data", value=True)

# -----------------------------
# Page background + gradient header
# -----------------------------
bg_color = "#0A0A0A"  # dark background
text_color = get_contrasting_text_color(bg_color)
header_gradient = "linear-gradient(90deg, #0D47A1, #1976D2)"

page_bg_css = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-color: {bg_color};
    color: {text_color};
}}
h1, h2, h3, h4, h5, h6, p, div, span {{
    color: {text_color} !important;
}}
[data-testid="stHeader"] {{
    background: {header_gradient};
}}
.stButton>button {{
    border-radius: 10px;
    background: #1976D2;
    color: white;
    font-weight: bold;
    padding: 0.5em 1em;
}}
.stDownloadButton>button {{
    border-radius: 10px;
    background: #388E3C;
    color: white;
    font-weight: bold;
    padding: 0.5em 1em;
}}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# -----------------------------
# Main app
# -----------------------------
st.title("📊 FinFET Parameter Extractor")

if demo_mode:
    st.info("Demo mode enabled — using synthetic data.")
    text = "Synthetic PDF content..."
    df = extract_parameters(text)
    st.dataframe(df)
else:
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        st.info("Extracting data from PDF...")
        pdf_text = extract_text_from_pdf(uploaded_file.read())
        if pdf_text.strip():
            df = extract_parameters(pdf_text)
            st.dataframe(df)
        else:
            df = None
            st.warning("No text detected in the uploaded PDF.")
    else:
        df = None

# -----------------------------
# Download section
# -----------------------------
if demo_mode or df is not None:
    st.subheader("Download Extracted Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "finfet_data.csv", "text/csv")
    xlsx = io.BytesIO()
    with pd.ExcelWriter(xlsx, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="FinFET Data")
    st.download_button("Download Excel", xlsx.getvalue(), "finfet_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    pdf_file = export_pdf_with_logo(df)
    st.download_button("Download PDF (with logo)", pdf_file, "finfet_data.pdf", "application/pdf")
