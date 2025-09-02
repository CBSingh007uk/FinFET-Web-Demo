import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import easyocr
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
from PIL import Image as PILImage
import base64

# --- Utility: Auto text color based on background ---
def get_contrasting_text_color(bg_color="#222222"):
    # Convert hex to RGB
    bg_color = bg_color.lstrip('#')
    r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#FFFFFF" if brightness < 128 else "#000000"

# --- Set darker theme ---
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

bg_color = "#1b1b1b"
text_color = get_contrasting_text_color(bg_color)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .css-1d391kg, .css-1v3fvcr {{
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: {text_color};
        padding: 10px 15px;
        border-radius: 10px;
    }}
    .stButton>button {{
        background: #444;
        color: #fff;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1em;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background: #666;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar with logo ---
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.markdown("### FinFET Data Extractor")
st.sidebar.write("Upload PDF or use demo mode.")

# --- Main app header ---
st.markdown("<h1 style='text-align:center;'>FinFET Parameter Extractor</h1>", unsafe_allow_html=True)

# --- Mode selection ---
mode = st.radio("Choose mode:", ["Upload PDF", "Synthetic Demo"], horizontal=True)

# --- Data container ---
extracted_data = pd.DataFrame()

try:
    if mode == "Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
        if uploaded_file is not None:
            # Read PDF text using PyMuPDF
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            st.text_area("Extracted PDF text (debug):", full_text[:1000])

            # OCR images inside PDF (optional)
            reader = easyocr.Reader(['en'], gpu=False)
            for page_index in range(len(doc)):
                for img_index, img in enumerate(doc.get_page_images(page_index)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    pil_img = PILImage.open(io.BytesIO(image_bytes))
                    ocr_result = reader.readtext(image_bytes)
                    st.write(f"OCR results page {page_index+1}, image {img_index+1}:", ocr_result)

            # Dummy extraction logic (replace with NLP/LLM parser)
            extracted_data = pd.DataFrame({
                "Parameter": ["Lg (nm)", "Hfin (nm)", "EOT (nm)", "Id (uA/um)"],
                "Value": [16, 45, 0.9, 1250]
            })
            st.success("PDF processed successfully!")

    elif mode == "Synthetic Demo":
        extracted_data = pd.DataFrame({
            "Parameter": ["Lg (nm)", "Hfin (nm)", "EOT (nm)", "Id (uA/um)", "SS (mV/dec)"],
            "Value": [14, 50, 0.8, 1320, 65]
        })
        st.success("Synthetic demo data generated!")

    if not extracted_data.empty:
        st.subheader("Extracted Parameters")
        st.dataframe(extracted_data)

        # --- Download options ---
        csv = extracted_data.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv, "extracted_data.csv", "text/csv")
        xlsx = io.BytesIO()
        with pd.ExcelWriter(xlsx, engine='openpyxl') as writer:
            extracted_data.to_excel(writer, index=False, sheet_name='Parameters')
        st.download_button("Download as Excel", xlsx.getvalue(), "extracted_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # --- PDF Export with embedded logo ---
        def create_pdf_with_logo(dataframe, logo_path="logo.png"):
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            elements = []

            # Add logo
            try:
                logo = Image(logo_path, 2*inch, 2*inch)
                elements.append(logo)
            except:
                elements.append(Paragraph("Logo missing", getSampleStyleSheet()["Normal"]))
            elements.append(Spacer(1, 12))

            # Add table
            table_data = [list(dataframe.columns)] + dataframe.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            return pdf_buffer.getvalue()

        pdf_bytes = create_pdf_with_logo(extracted_data)
        st.download_button("Download PDF Report", pdf_bytes, "extracted_report.pdf", "application/pdf")

except Exception as e:
    st.error("An error occurred while processing.")
    st.exception(e)
