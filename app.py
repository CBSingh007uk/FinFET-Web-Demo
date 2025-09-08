import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt
from PIL import Image

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="FinFET Data Extractor",
                   layout="wide",
                   page_icon="📊")

# ------------------------
# STYLING
# ------------------------
st.markdown(
    """
    <style>
    .main {background-color: #1e1e1e; color: #e0f7fa;}
    .stSidebar {background-color: #111111; color: #e0f7fa;}
    .sidebar .sidebar-content {color: #e0f7fa;}
    .css-1aumxhk {color: #e0f7fa;}  /* for buttons and texts */
    </style>
    """, unsafe_allow_html=True
)

# ------------------------
# LOGO
# ------------------------
logo_img = Image.open("logo.png")  # place logo.png in the repo
st.sidebar.image(logo_img, use_column_width=True)

# ------------------------
# PDF REPOSITORY OPTIONS
# ------------------------
pdf_options = { 
    "Arxiv 1905.11207v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190v1": "pdfs/2501.15190v1.pdf"
}

# ------------------------
# FUNCTION TO SIMULATE PARAMETER EXTRACTION
# ------------------------
def parse_parameters(text):
    # Here you can implement actual extraction; for demo, we simulate
    df = pd.DataFrame({
        "Lg (nm)": [3, 4, 5],
        "Hfin (nm)": [6, 6.5, 7],
        "EOT (nm)": [0.8, 0.85, 0.9],
        "Vth (V)": [0.3, 0.35, 0.4],
        "ID_max (A/cm2)": [0.8, 1.0, 1.2],
        "Ion/Ioff": [5e4, 4e4, 3e4],
        "Vg (V)": [list(np.linspace(0, 1.0, 10))]*3,
        "ID vs Vg (A/cm2)": [list(np.linspace(0, 0.8, 10)),
                             list(np.linspace(0, 1.0, 10)),
                             list(np.linspace(0, 1.2, 10))]
    })
    return df

# ------------------------
# FUNCTION TO EXPORT PDF WITH LOGO
# ------------------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    # Logo
    pdf.image("logo.png", x=10, y=8, w=30)
    pdf.set_font("Arial", "B", 14)
    pdf.ln(20)
    pdf.cell(0, 10, "Extracted FinFET Parameters", ln=True)
    pdf.ln(5)
    # Table
    pdf.set_font("Arial", "", 12)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = 8
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    for i in range(len(df)):
        for col in df.columns:
            val = df.iloc[i][col]
            if isinstance(val, list):
                val = ", ".join([f"{v:.2f}" if isinstance(v,float) else str(v) for v in val])
            pdf.cell(col_width, row_height, str(val), border=1)
        pdf.ln(row_height)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# ------------------------
# MAIN APP
# ------------------------
st.title("📊 FinFET Data Extractor")
st.markdown("Upload a PDF/Image or select one from our repository to extract FinFET parameters.")

mode = st.sidebar.radio("Choose Mode", ["Synthetic Demo", "Select PDF", "Upload PDF"])

if mode == "Synthetic Demo":
    st.header("Synthetic FinFET Demo Data")
    synthetic_text = "Simulated FinFET parameters for testing."
    st.text_area("PDF Content", synthetic_text, height=150)
    df = parse_parameters(synthetic_text)
    st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)

    # ID vs Vg plots
    st.subheader("ID vs Vg Scaling Plot")
    fig, ax = plt.subplots()
    for i in range(len(df)):
        ax.plot(df["Vg (V)"][i], df["ID vs Vg (A/cm2)"][i], marker='o', label=f"Device {i+1}")
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.legend()
    st.pyplot(fig)

    # Download buttons
    st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "synthetic_finfet.csv")
    excel_bytes = BytesIO()
    df.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    st.download_button("⬇️ Download Excel", excel_bytes, "synthetic_finfet.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")

elif mode == "Select PDF":
    st.header("Select PDF from Repository")
    selected_pdf = st.selectbox("Choose PDF", list(pdf_options.keys()))
    pdf_path = pdf_options[selected_pdf]
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = BytesIO(f.read())
        text = f"Simulated extraction from {selected_pdf}"
        st.text_area("PDF Content", text, height=200)
        df = parse_parameters(text)
        st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)
        # Download
        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), f"{selected_pdf}.csv")
        excel_bytes = BytesIO()
        df.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        st.download_button("⬇️ Download Excel", excel_bytes, f"{selected_pdf}.xlsx")
        st.download_button("⬇️ Download PDF", export_pdf(df), f"{selected_pdf}.pdf")
    except FileNotFoundError:
        st.error(f"File {pdf_path} not found.")

elif mode == "Upload PDF":
    st.header("Upload your own PDF")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        text = "Simulated extraction from uploaded PDF."
        st.text_area("Extracted Text from PDF", text, height=200)
        df = parse_parameters(text)
        st.dataframe(df.drop(columns=["Vg", "ID vs Vg (A/cm2)"]), use_container_width=True)
        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "uploaded_finfet.csv")
        excel_bytes = BytesIO()
        df.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        st.download_button("⬇️ Download Excel", excel_bytes, "uploaded_finfet.xlsx")
        st.download_button("⬇️ Download PDF", export_pdf(df), "uploaded_finfet.pdf")
