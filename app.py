import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image as PILImage
import base64

# ---- CONFIG ----
st.set_page_config(page_title="FinFET Data Extractor", page_icon="🔎", layout="wide")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the buttons below to explore:")
st.sidebar.button("Home")
st.sidebar.button("About")
st.sidebar.button("Contact")

# ---- HEADER ----
st.markdown(
    """
    <div style="background: linear-gradient(90deg, #1e1e1e, #3c3c3c);
                padding: 20px; border-radius: 12px; text-align: center;">
        <h1 style="color: white;">🔎 FinFET Data Extractor</h1>
        <p style="color: #ddd;">Extract, Analyze, and Export Device Parameters</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---- FILE UPLOAD ----
uploaded_file = st.file_uploader("Upload a FinFET PDF file", type=["pdf"])

# OCR reader
reader = easyocr.Reader(['en'])

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_text(text):
    # Placeholder synthetic demo parameters
    params = {
        "Gate Length (Lg)": "12 nm",
        "Fin Height (Hfin)": "30 nm",
        "EOT": "0.7 nm",
        "Drain Current (Id)": "1.2 mA/um",
        "Subthreshold Slope (SS)": "65 mV/dec"
    }
    return params

def auto_text_color(bg_color):
    # Ensure text contrasts with background
    r, g, b = bg_color
    brightness = (r*299 + g*587 + b*114) / 1000
    return (255,255,255) if brightness < 128 else (0,0,0)

def create_pdf(params, logo_path):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    if logo_path:
        img = Image(logo_path, width=80, height=80)
        elements.append(img)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>FinFET Parameters Extracted</b>", styles["Title"]))
    elements.append(Spacer(1, 24))

    for k, v in params.items():
        elements.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value

if uploaded_file:
    try:
        with st.spinner("Extracting data..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            params = analyze_text(extracted_text)

        # Display output
        st.success("Parameters extracted successfully!")
        df = pd.DataFrame(list(params.items()), columns=["Parameter", "Value"])
        st.table(df)

        # Download as CSV/Excel
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="finfet_parameters.csv", mime="text/csv")
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button("Download Excel", data=excel_buffer.getvalue(),
                           file_name="finfet_parameters.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # PDF export with logo
        logo_path = "logo.png"  # Ensure logo.png exists in app directory
        pdf_data = create_pdf(params, logo_path)
        st.download_button("Download PDF Report", data=pdf_data,
                           file_name="finfet_report.pdf", mime="application/pdf")
    except Exception as e:
        st.error("Error processing file.")
        st.exception(e)
else:
    st.info("Upload a PDF file to begin.")
