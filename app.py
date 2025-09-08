import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# ---------------------------
# Utility Functions
# ---------------------------

def auto_text_color(bg_color="#1E1E2F"):
    # Determine light/dark text based on bg brightness
    bg_color = bg_color.lstrip("#")
    r, g, b = int(bg_color[:2],16), int(bg_color[2:4],16), int(bg_color[4:],16)
    brightness = (r*299 + g*587 + b*114)/1000
    return "#FFFFFF" if brightness < 128 else "#000000"

def export_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def export_pdf(df, logo_img=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FinFET Extracted Parameters", ln=True, align="C")
    pdf.ln(10)

    if logo_img:
        # Embed logo
        temp_buffer = BytesIO()
        logo_img.save(temp_buffer, format="PNG")
        temp_buffer.seek(0)
        pdf.image(temp_buffer, x=10, y=8, w=30)

    pdf.set_font("Arial", "", 12)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = 8

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, col, border=1)
    pdf.ln(row_height)

    # Data
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)

    return pdf.output(dest="S").encode('latin1')

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.markdown("### Select Mode")
mode = st.sidebar.radio("Mode", ["Upload PDF/Image", "Synthetic Demo"])

pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ---------------------------
# Main Page
# ---------------------------
st.markdown(
    """
    <style>
    .main {background-color: #2C2F3E;}
    .sidebar .sidebar-content {background-color: #2C2F3E;}
    </style>
    """,
    unsafe_allow_html=True
)

text_color = auto_text_color("#2C2F3E")
st.markdown(f"<h1 style='color:{text_color}; text-align:center;'>FinFET Data Extractor</h1>", unsafe_allow_html=True)

log_messages = []

def show_log(msg):
    log_messages.append(msg)
    st.sidebar.text_area("Log", value="\n".join(log_messages), height=200)
    st.text_area("Log", value="\n".join(log_messages), height=200)

# ---------------------------
# Synthetic Demo
# ---------------------------
def show_synthetic_demo():
    st.subheader("Synthetic FinFET Demo Data")
    synthetic_df = pd.DataFrame({
        "Lg (nm)": [3, 5, 7],
        "Hfin (nm)": [6, 8, 10],
        "EOT (nm)": [0.8, 0.9, 1.0],
        "Vth (V)": [0.3, 0.35, 0.4],
        "ID (A/cm2)": [0.8, 0.6, 0.4],
        "Ion/Ioff": [5e4, 4e4, 3e4],
        "Vg (V)": [np.linspace(0, 1, 10) for _ in range(3)]
    })
    st.dataframe(synthetic_df.drop(columns=["Vg"]))

    # Plot ID vs Vg
    fig, ax = plt.subplots()
    for i in range(len(synthetic_df)):
        ax.plot(synthetic_df["Vg"][i], np.linspace(0, synthetic_df["ID (A/cm2)"][i], len(synthetic_df["Vg"][i])),
                marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg Scaling Plot")
    ax.legend()
    st.pyplot(fig)

    # Download buttons
    st.download_button("⬇️ Download CSV", export_csv(synthetic_df), "synthetic_finfet.csv")
    st.download_button("⬇️ Download Excel", export_excel(synthetic_df), "synthetic_finfet.xlsx")
    logo_img = Image.open("logo.png")
    st.download_button("⬇️ Download PDF", export_pdf(synthetic_df, logo_img), "synthetic_finfet.pdf")

# ---------------------------
# Uploaded PDF Handling
# ---------------------------
def extract_text_from_pdf(pdf_path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        show_log(f"Error reading PDF: {e}")
        return ""

def show_uploaded_pdf_mode():
    selected_pdf_name = st.sidebar.selectbox("Select PDF", list(pdf_options.keys()))
    pdf_path = pdf_options[selected_pdf_name]
    st.write(f"Extracting from {selected_pdf_name}...")
    extracted_text = extract_text_from_pdf(pdf_path)
    st.text_area("Extracted Text", extracted_text, height=300)

    # Simulated parameter extraction from text
    extracted_params = {
        "Lg (nm)": 3,
        "Hfin (nm)": 6,
        "EOT (nm)": 0.8,
        "Vth (V)": 0.3,
        "ID (A/cm2)": 0.8,
        "Ion/Ioff": 5e4,
        "Vg (V)": np.linspace(0,1,10)
    }
    df = pd.DataFrame([extracted_params])
    st.dataframe(df.drop(columns=["Vg"]))

    # Plot ID vs Vg
    fig, ax = plt.subplots()
    ax.plot(df["Vg"][0], np.linspace(0, df["ID (A/cm2)"][0], len(df["Vg"][0])), marker='o')
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg Scaling Plot")
    st.pyplot(fig)

    # Download buttons
    st.download_button("⬇️ Download CSV", export_csv(df), "finfet_params.csv")
    st.download_button("⬇️ Download Excel", export_excel(df), "finfet_params.xlsx")
    logo_img = Image.open("logo.png")
    st.download_button("⬇️ Download PDF", export_pdf(df, logo_img), "finfet_params.pdf")

# ---------------------------
# Main Control
# ---------------------------
if mode == "Synthetic Demo":
    show_synthetic_demo()
else:
    show_uploaded_pdf_mode()
