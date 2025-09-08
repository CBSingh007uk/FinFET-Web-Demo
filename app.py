import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# ------------------------------
# Configuration
# ------------------------------
st.set_page_config(
    page_title="FinFET Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Utility functions
# ------------------------------
def generate_logo():
    """Generates a synthetic logo."""
    logo = Image.new("RGB", (200, 50), color="#0d1117")
    d = ImageDraw.Draw(logo)
    font = ImageFont.load_default()
    d.text((10, 10), "FinFET Extractor", fill=(200, 200, 255), font=font)
    return logo

def export_pdf(df, logo_img):
    """Exports DataFrame to PDF with embedded logo."""
    pdf = FPDF()
    pdf.add_page()
    # Save logo temporarily
    logo_bytes = BytesIO()
    logo_img.save(logo_bytes, format="PNG")
    logo_bytes.seek(0)
    pdf.image(logo_bytes, x=10, y=8, w=50)
    pdf.set_font("Arial", size=12)
    pdf.ln(30)
    # Table content
    for i, row in df.iterrows():
        row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        pdf.cell(0, 8, row_text, ln=True)
    return pdf.output(dest="S").encode("latin1")

def export_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# ------------------------------
# Synthetic Demo Data
# ------------------------------
def get_synthetic_data():
    devices = 5
    points = 20
    Vg = np.linspace(0, 1.0, points)
    data = {
        "Device": [],
        "Lg (nm)": [],
        "Hfin (nm)": [],
        "EOT (nm)": [],
        "ID (A/cm2)": [],
        "Vth (V)": [],
        "Ion/Ioff": [],
        "gm (mS)": [],
        "Rsd (Ohm)": [],
        "Cgg (fF)": [],
        "Delay (ps)": [],
        "Vg": []
    }
    for i in range(devices):
        data["Device"].append(f"Device {i+1}")
        data["Lg (nm)"].append(round(np.random.uniform(3,5),2))
        data["Hfin (nm)"].append(round(np.random.uniform(5,8),2))
        data["EOT (nm)"].append(round(np.random.uniform(0.7,1.0),2))
        ID = np.random.uniform(0.1, 1.0, points)
        data["ID (A/cm2)"].append(ID)
        data["Vth (V)"].append(round(np.random.uniform(0.2,0.35),2))
        data["Ion/Ioff"].append(round(np.random.uniform(10**4, 10**5)))
        data["gm (mS)"].append(round(np.random.uniform(0.5, 2.0),2))
        data["Rsd (Ohm)"].append(round(np.random.uniform(100,200),2))
        data["Cgg (fF)"].append(round(np.random.uniform(5,15),2))
        data["Delay (ps)"].append(round(np.random.uniform(10,50),2))
        data["Vg"].append(Vg)
    df = pd.DataFrame(data)
    return df

# ------------------------------
# Layout
# ------------------------------
st.markdown(
    """
    <style>
    body {background-color: #121212; color: #cfcfcf;}
    .stButton>button {background-color:#0d1117; color:#cfcfcf; border-radius:5px;}
    .sidebar .sidebar-content {background-color:#1e1e1e;}
    </style>
    """, unsafe_allow_html=True
)

# Sidebar
st.sidebar.image(generate_logo(), use_column_width=True)
option = st.sidebar.radio("Select Mode", ["Synthetic Demo", "Upload PDF/Image"])

# Central log area
log_area = st.empty()

# ------------------------------
# Synthetic Demo
# ------------------------------
def show_synthetic_demo():
    df = get_synthetic_data()
    st.subheader("Synthetic FinFET Demo Data")
    
    # Display table with side scroll
    st.dataframe(df.drop(columns=["Vg","ID (A/cm2)"]), width=1200, height=300)
    
    # Scaling plots
    fig, ax = plt.subplots(figsize=(8,5))
    for i in range(len(df)):
        ax.plot(df["Vg"][i], df["ID (A/cm2)"][i], marker='o', label=df["Device"][i])
    ax.set_xlabel("Vg (V)")
    ax.set_ylabel("ID (A/cm2)")
    ax.set_title("ID vs Vg Scaling Plot")
    ax.legend()
    st.pyplot(fig)
    
    # Download buttons
    logo = generate_logo()
    df_download = df.drop(columns=["Vg"])  # For CSV, keep numeric columns only
    st.download_button("⬇️ Download CSV", export_csv(df_download), "synthetic_finfet.csv")
    st.download_button("⬇️ Download PDF", export_pdf(df_download, logo), "synthetic_finfet.pdf")

# ------------------------------
# PDF Upload Simulation
# ------------------------------
def show_upload_simulation():
    st.subheader("Simulated PDF Upload Content")
    simulated_text = """This is a simulated PDF content for testing the FinFET Data Extractor.
Parameters extracted: Lg=3nm, Hfin=6nm, EOT=0.8nm, Vth=0.3V, ID_max=0.8A/cm2, Ion/Ioff=5e4"""
    st.text_area("Extracted Text", simulated_text, height=200)

# ------------------------------
# Main
# ------------------------------
try:
    if option == "Synthetic Demo":
        show_synthetic_demo()
    else:
        show_upload_simulation()
except Exception as e:
    log_area.error(f"Error: {e}")
    st.exception(e)
