# finfet_web_demo.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import fitz  # PyMuPDF

# ---------------------------
# Sidebar Logo
# ---------------------------
logo_path = "logo.png"  # Ensure logo.png is in main folder
st.sidebar.image(logo_path, width=150)

# ---------------------------
# Sidebar: Common Options
# ---------------------------
st.sidebar.header("FinFET Data Extractor Demo")
option = st.sidebar.selectbox(
    "Select Demo Mode:",
    ["Synthetic Demo", "Local PDF", "Browse PDF"]
)

st.sidebar.button("Extract Data")  # Common extract button placeholder

# ---------------------------
# Main Page Logo
# ---------------------------
st.image(logo_path, width=200)

# ---------------------------
# Synthetic Demo Data
# ---------------------------
def synthetic_parameters():
    """IRDS-aligned synthetic FinFET dataset for multiple nodes"""
    data = [
        {"Node":"7nm","Lg (nm)":15,"Hfin (nm)":40,"EOT (nm)":0.60,"ID (A/cm²)":1.8e4,
         "Vth (V)":0.32,"Ion/Ioff":2.5e6,"gm (µS/µm)":2600,"Rsd (Ω·µm)":80,"Cgg (fF/µm)":1.0,"Delay (ps)":1.2},
        {"Node":"6nm","Lg (nm)":14,"Hfin (nm)":42,"EOT (nm)":0.58,"ID (A/cm²)":1.9e4,
         "Vth (V)":0.31,"Ion/Ioff":2.7e6,"gm (µS/µm)":2700,"Rsd (Ω·µm)":75,"Cgg (fF/µm)":1.1,"Delay (ps)":1.1},
        {"Node":"5nm","Lg (nm)":12,"Hfin (nm)":45,"EOT (nm)":0.55,"ID (A/cm²)":2.0e4,
         "Vth (V)":0.30,"Ion/Ioff":3.0e6,"gm (µS/µm)":2800,"Rsd (Ω·µm)":70,"Cgg (fF/µm)":1.2,"Delay (ps)":1.0},
        {"Node":"4nm","Lg (nm)":9,"Hfin (nm)":50,"EOT (nm)":0.50,"ID (A/cm²)":2.3e4,
         "Vth (V)":0.28,"Ion/Ioff":4.0e6,"gm (µS/µm)":3100,"Rsd (Ω·µm)":60,"Cgg (fF/µm)":1.4,"Delay (ps)":0.8},
        {"Node":"3nm","Lg (nm)":7,"Hfin (nm)":55,"EOT (nm)":0.48,"ID (A/cm²)":2.6e4,
         "Vth (V)":0.25,"Ion/Ioff":5.0e6,"gm (µS/µm)":3400,"Rsd (Ω·µm)":50,"Cgg (fF/µm)":1.6,"Delay (ps)":0.6},
        {"Node":"2nm","Lg (nm)":5,"Hfin (nm)":60,"EOT (nm)":0.45,"ID (A/cm²)":3.0e4,
         "Vth (V)":0.22,"Ion/Ioff":6.0e6,"gm (µS/µm)":3600,"Rsd (Ω·µm)":40,"Cgg (fF/µm)":1.8,"Delay (ps)":0.5},
    ]
    return pd.DataFrame(data)

# ---------------------------
# PDF Options (Local pre-defined)
# ---------------------------
pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

# ---------------------------
# Utility: Scaling Plots
# ---------------------------
def plot_scaling(df):
    fig, axs = plt.subplots(1,3,figsize=(15,4))
    
    # Lg vs gm
    axs[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], 'o-', color='blue')
    axs[0].set_xlabel("Lg (nm)")
    axs[0].set_ylabel("gm (µS/µm)")
    axs[0].grid(True)
    
    # Vth vs Ion/Ioff
    axs[1
