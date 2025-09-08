import streamlit as st
import pandas as pd
import numpy as np
import requests
import fitz  # PyMuPDF
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# -------------------- Styling --------------------
st.markdown("""
    <style>
    .main {background-color: #1c1c1c; color: #d0d0d0;}
    .sidebar .sidebar-content {background-color: #111111; color: #d0d0d0;}
    .stButton>button {background-color:#4444aa;color:#ffffff;}
    </style>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
st.sidebar.image("logo.png", use_column_width=True)
mode = st.sidebar.radio("Mode", ["Select PDF from GitHub", "Upload PDF", "Synthetic Demo"])

# GitHub PDFs
github_pdfs = {
    "1905.11207v3.pdf": "https://raw.githubusercontent.com/yourusername/yourrepo/main/pdfs/1905.11207v3.pdf",
    "2007.13168v4.pdf": "https://raw.githubusercontent.com/yourusername/yourrepo/main/pdfs/2007.13168v4.pdf",
    "2007.14448v1.pdf": "https://raw.githubusercontent.com/yourusername/yourrepo/main/pdfs/2007.14448v1.pdf",
    "2407.18187v1.pdf": "https://raw.githubusercontent.com/yourusername/yourrepo/main/pdfs/2407.18187v1.pdf",
    "2501.15190v1.pdf": "https://raw.githubusercontent.com/yourusername/yourrepo/main/pdfs/2501.15190v1.pdf"
}

# -------------------- Functions --------------------
def extract_text_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {e}")
        return ""

def parse_parameters(text):
    # Dummy parser: you can replace with real parsing logic
    # Try to extract numbers after "Lg=", "Hfin=", etc.
    param_dict = {
        "Lg (nm)": [3],
        "Hfin (nm)": [6],
        "EOT (nm)": [0.8],
        "Vth (V)": [0.3],
        "ID_max (A/cm2)": [0.8],
        "Ion/Ioff": [5e4],
        "gm (mS/μm)": [1.2],
        "Rs_d (Ω·μm)": [50],
        "Capacitance (fF/μm)": [0.5],
        "Delay (ps)": [10],
        "Vg (V)": [np.linspace(0, 1.2, 10)],
        "ID vs Vg (A/cm2)": [np.linspace(0, 0.8, 10)]
    }
    df = pd.DataFrame(param_dict)
    return df

def export_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Add logo if exists
    try:
        pdf.image("logo.png", x=10, y=8, w=40)
    except:
        pass
    pdf.ln(20)
    for col in df.columns:
        pdf.cell(40, 10, col, border=1)
    pdf.ln()
    for i in range(len(df)):
        for col in df.columns:
            val = df.iloc[i][col]
            if isinstance(val, (list, np.ndarray)):
                val = str(val)
            pdf.cell(40, 10, str(val), border=1)
        pdf.ln()
    return pdf.output(dest="S").encode("latin1")

# -------------------- Main --------------------
if mode == "Select PDF from GitHub":
    selected_pdf = st.sidebar.selectbox("Select PDF", list(github_pdfs.keys()))
    if selected_pdf:
        r = requests.get(github_pdfs[selected_pdf])
        text = extract_text_from_pdf(r.content)
        st.subheader("Extracted Text from PDF")
        st.text_area("PDF Content", text, height=300)
        df = parse_parameters(text)
        st.subheader("Extracted Parameters")
        st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)

elif mode == "Upload PDF":
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file.read())
        st.subheader("Extracted Text from PDF")
        st.text_area("PDF Content", text, height=300)
        df = parse_parameters(text)
        st.subheader("Extracted Parameters")
        st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)

else:  # Synthetic Demo
    st.subheader("Synthetic FinFET Demo Data")
    df = parse_parameters("")
    st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)

# -------------------- Downloads --------------------
st.subheader("Download Extracted Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("⬇️ CSV", export_csv(df), file_name="finfet_params.csv")
with col2:
    st.download_button("⬇️ Excel", export_excel(df), file_name="finfet_params.xlsx")
with col3:
    st.download_button("⬇️ PDF", export_pdf(df), file_name="finfet_params.pdf")

# -------------------- Scaling Plot --------------------
st.subheader("ID vs Vg Scaling Plot")
fig, ax = plt.subplots()
for i in range(len(df)):
    x = df["Vg"][i]
    y = df["ID vs Vg (A/cm2)"][i]
    ax.plot(x, y, marker='o', label=f"Device {i+1}")
ax.set_xlabel("Vg (V)")
ax.set_ylabel("ID (A/cm2)")
ax.legend()
st.pyplot(fig)
