import streamlit as st
import fitz  # PyMuPDF
import easyocr
import pandas as pd
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image
import numpy as np
import qrcode
import matplotlib.pyplot as plt

def synthetic_parameters():
    # IRDS-aligned synthetic FinFET dataset for 3–5 nm nodes
    data = [
        {
            "Node": "5 nm",
            "Lg (nm)": 12,
            "Hfin (nm)": 45,
            "EOT (nm)": 0.55,
            "ID (A/cm²)": 2.0e4,
            "Vth (V)": 0.30,
            "Ion/Ioff": 3.0e6,
            "gm (µS/µm)": 2800,
            "Rsd (Ω·µm)": 70,
            "Cgg (fF/µm)": 1.2,
            "Delay (ps)": 1.0,
        },
        {
            "Node": "4 nm",
            "Lg (nm)": 9,
            "Hfin (nm)": 50,
            "EOT (nm)": 0.50,
            "ID (A/cm²)": 2.3e4,
            "Vth (V)": 0.28,
            "Ion/Ioff": 4.0e6,
            "gm (µS/µm)": 3100,
            "Rsd (Ω·µm)": 60,
            "Cgg (fF/µm)": 1.4,
            "Delay (ps)": 0.8,
        },
        {
            "Node": "3 nm",
            "Lg (nm)": 7,
            "Hfin (nm)": 55,
            "EOT (nm)": 0.48,
            "ID (A/cm²)": 2.6e4,
            "Vth (V)": 0.25,
            "Ion/Ioff": 5.0e6,
            "gm (µS/µm)": 3400,
            "Rsd (Ω·µm)": 50,
            "Cgg (fF/µm)": 1.6,
            "Delay (ps)": 0.6,
        },
    ]
    return pd.DataFrame(data)


def show_synthetic_demo():
    st.subheader("📊 Synthetic Demo (3–5 nm IRDS-aligned FinFET Parameters)")
    
    df = synthetic_parameters()
    st.dataframe(df, use_container_width=True)

    # Plot scaling trends
    st.markdown("### Scaling Trends")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # gm vs Lg
    axes[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker="o", color="cyan", linewidth=2)
    axes[0].invert_xaxis()  # smaller Lg → right side
    axes[0].set_xlabel("Lg (nm)")
    axes[0].set_ylabel("gm (µS/µm)")
    axes[0].set_title("Lg vs gm")

    # Ion/Ioff vs Vth
    axes[1].plot(df["Vth (V)"], df["Ion/Ioff"], marker="s", color="magenta", linewidth=2)
    axes[1].set_xlabel("Vth (V)")
    axes[1].set_ylabel("Ion/Ioff")
    axes[1].set_title("Vth vs Ion/Ioff")

    st.pyplot(fig)

    # Allow download
    st.download_button(
        "💾 Download Synthetic Data (CSV)",
        data=df.to_csv(index=False),
        file_name="synthetic_finfet_3to5nm.csv",
        mime="text/csv"
    )


# --- CONFIG ---
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
BACKGROUND_COLOR = "#1E1E2F"   # slightly lighter dark
SIDEBAR_COLOR = "#2A2A3D"
TEXT_COLOR = "#F5F5F5"

# --- UTILITY: automatic text color based on background brightness ---
def get_contrasting_text_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r*299 + g*587 + b*114) / 1000
    return "#000000" if brightness > 160 else "#FFFFFF"

# --- CUSTOM CSS ---
st.markdown(
    f"""
    <style>
        /* Body background & text */
        body {{
            background-color: {BACKGROUND_COLOR};
            color: {get_contrasting_text_color(BACKGROUND_COLOR)};
        }}
        /* Gradient buttons */
        .stButton>button {{
            background: linear-gradient(90deg, #4b6cb7, #182848);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
        }}
        /* Sidebar background */
        .css-1d391kg {{
            background-color: {SIDEBAR_COLOR} !important;
        }}
        /* Sidebar text color desktop + mobile */
        .css-1v3fvcr, .css-1v3fvcr span, .css-1v3fvcr p, .st-bf {{
            color: {TEXT_COLOR} !important;
        }}
        /* Sidebar headers */
        .css-1k0ckh2 h1, .css-1k0ckh2 h2, .css-1k0ckh2 h3, .css-1k0ckh2 h4 {{
            color: {TEXT_COLOR} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Choose mode:", ["Upload PDF", "Synthetic Demo"])
st.sidebar.info("Upload a PDF or use the synthetic demo to extract FinFET parameters.")

# --- OCR Reader ---
reader = easyocr.Reader(['en'])

# --- HEADER ---
st.markdown("<h1 style='text-align:center;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)
st.write("---")

# --- DATA EXTRACTION FUNCTIONS ---
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def synthetic_parameters():
    return pd.DataFrame([
        {"Lg (nm)": 14, "Hfin (nm)": 30, "EOT (nm)": 0.9, "Idsat (µA/µm)": 1100},
        {"Lg (nm)": 10, "Hfin (nm)": 40, "EOT (nm)": 0.7, "Idsat (µA/µm)": 1500}
    ])

# --- EXPORT FUNCTIONS ---
def export_to_excel(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def export_to_csv(df):
    return df.to_csv(index=False).encode()

def export_to_pdf(df):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    # Logo embedding
    try:
        logo = RLImage("logo.png", width=1.5*inch, height=1.5*inch)
        elems.append(logo)
        elems.append(Spacer(1, 0.2*inch))
    except:
        pass

    elems.append(Paragraph("Extracted FinFET Parameters", styles["Heading1"]))
    elems.append(Spacer(1, 0.2*inch))

    for col in df.columns:
        for val in df[col]:
            elems.append(Paragraph(f"<b>{col}</b>: {val}", styles["Normal"]))
        elems.append(Spacer(1, 0.1*inch))

    doc.build(elems)
    pdf_data = buf.getvalue()
    buf.close()
    return pdf_data

# --- MAIN APP LOGIC ---
if mode == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file:
        try:
            text = extract_text_from_pdf(uploaded_file)
            st.subheader("Extracted Text Preview")
            st.text_area("Text", text, height=200)

            # Use synthetic extraction for demo
            df = synthetic_parameters()
            st.subheader("Extracted Parameters")
            st.dataframe(df)

            # Download buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Download as Excel", export_to_excel(df), "parameters.xlsx")
            with col2:
                st.download_button("Download as CSV", export_to_csv(df), "parameters.csv")
            with col3:
                st.download_button("Download as PDF", export_to_pdf(df), "parameters.pdf", mime="application/pdf")

        except Exception as e:
            st.error("Error while processing PDF.")
            st.exception(e)

elif mode == "Synthetic Demo":
    st.subheader("Synthetic FinFET Data")
    df = synthetic_parameters()
    st.dataframe(df)
    st.download_button("Download as Excel", export_to_excel(df), "synthetic.xlsx")
    st.download_button("Download as CSV", export_to_csv(df), "synthetic.csv")
    st.download_button("Download as PDF", export_to_pdf(df), "synthetic.pdf", mime="application/pdf")
