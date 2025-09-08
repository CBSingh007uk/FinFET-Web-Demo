# finfet_web_demo_full.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# ---------------------------
# Logo
# ---------------------------
logo_path = "logo.png"  # Ensure logo.png is in the main folder
st.sidebar.image(logo_path, width=150)
st.image(logo_path, width=200, use_column_width=False)

# ---------------------------
# Sidebar: Common Options
# ---------------------------
st.sidebar.header("FinFET Data Extractor Demo")
demo_option = st.sidebar.selectbox(
    "Select Demo Mode:",
    ["Synthetic Demo", "Local PDF", "Browse PDF"]
)

# ---------------------------
# Synthetic Demo Data
# ---------------------------
def synthetic_parameters():
    data = [
        {"Node":"7nm","Lg (nm)":15,"Hfin (nm)":40,"EOT (nm)":0.60,"ID (A/cm²)":1.8e4,
         "Vth (V)":0.32,"Ion/Ioff":2.5e6,"gm (µS/µm)":2600,"Rsd (Ω·µm)":80,"Cgg (fF/µm)":1.0,"Delay (ps)":1.2},
        {"Node":"5nm","Lg (nm)":12,"Hfin (nm)":45,"EOT (nm)":0.55,"ID (A/cm²)":2.0e4,
         "Vth (V)":0.30,"Ion/Ioff":3.0e6,"gm":2800,"Rsd":70,"Cgg":1.2,"Delay":1.0},
        {"Node":"4nm","Lg (nm)":9,"Hfin (nm)":50,"EOT (nm)":0.50,"ID (A/cm²)":2.3e4,
         "Vth (V)":0.28,"Ion/Ioff":4.0e6,"gm":3100,"Rsd":60,"Cgg":1.4,"Delay":0.8},
        {"Node":"3nm","Lg (nm)":7,"Hfin (nm)":55,"EOT (nm)":0.48,"ID (A/cm²)":2.6e4,
         "Vth (V)":0.25,"Ion/Ioff":5.0e6,"gm":3400,"Rsd":50,"Cgg":1.6,"Delay":0.6},
        {"Node":"2nm","Lg (nm)":5,"Hfin (nm)":60,"EOT (nm)":0.45,"ID (A/cm²)":3.0e4,
         "Vth (V)":0.22,"Ion/Ioff":6.0e6,"gm":3600,"Rsd":40,"Cgg":1.8,"Delay":0.5},
        {"Node":"1nm","Lg (nm)":3,"Hfin (nm)":65,"EOT (nm)":0.42,"ID (A/cm²)":3.5e4,
         "Vth (V)":0.20,"Ion/Ioff":7.0e6,"gm":3800,"Rsd":35,"Cgg":2.0,"Delay":0.4},
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
# Plotting Utilities
# ---------------------------
def plot_scaling(df):
    fig, axs = plt.subplots(1,3,figsize=(15,4))
    
    # Lg vs gm
    axs[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], 'o-', color='blue')
    axs[0].set_xlabel("Lg (nm)"); axs[0].set_ylabel("gm (µS/µm)")
    
    # Vth vs Ion/Ioff
    axs[1].plot(df["Vth (V)"], df["Ion/Ioff"], 's-', color='green')
    axs[1].set_xlabel("Vth (V)"); axs[1].set_ylabel("Ion/Ioff")
    
    # Delay vs Cgg
    axs[2].plot(df["Delay (ps)"], df["Cgg (fF/µm)"], 'd-', color='red')
    axs[2].set_xlabel("Delay (ps)"); axs[2].set_ylabel("Cgg (fF/µm)")
    
    plt.tight_layout()
    st.pyplot(fig)

def plot_id_vg_synthetic():
    Vg = np.linspace(0,1,100)
    currents = {
        "7nm": 1.5e-4*(np.exp(5*Vg)-1),
        "5nm": 1.8e-4*(np.exp(5*Vg)-1),
        "4nm": 2.0e-4*(np.exp(5*Vg)-1),
        "3nm": 2.2e-4*(np.exp(5*Vg)-1),
        "2nm": 2.5e-4*(np.exp(5*Vg)-1),
        "1nm": 2.8e-4*(np.exp(5*Vg)-1)
    }
    fig, ax = plt.subplots()
    for node, Id in currents.items():
        ax.plot(Vg, Id, label=f"{node}")
    ax.set_xlabel("Vg (V)"); ax.set_ylabel("Id (A/cm²)")
    ax.set_title("Synthetic Id–Vg Curves")
    ax.legend()
    st.pyplot(fig)

# ---------------------------
# Option Handlers
# ---------------------------
if demo_option == "Synthetic Demo":
    st.header("Synthetic FinFET Demo")
    df = synthetic_parameters()
    st.subheader("Parameters Table")
    st.dataframe(df)
    st.subheader("Scaling Plots")
    plot_scaling(df)
    st.subheader("Synthetic Id–Vg Curves")
    plot_id_vg_synthetic()

elif demo_option == "Local PDF":
    st.header("Local PDF Extraction")
    pdf_choice = st.sidebar.selectbox("Select PDF:", list(pdf_options.keys()))
    pdf_file = pdf_options[pdf_choice]
    st.write(f"Selected PDF: {pdf_file}")
    st.warning("Automatic curve extraction from PDF is not yet implemented in this demo. Tables may be random text depending on PDF quality.")

elif demo_option == "Browse PDF":
    st.header("Browse and Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF", type="pdf")
    if uploaded_file is not None:
        st.write(f"Uploaded PDF: {uploaded_file.name}")
        st.warning("Automatic curve extraction from PDF is not yet implemented in this demo. Tables may be random text depending on PDF quality.")
