# finfet_streamlit_demo.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
from pdf2image import convert_from_path
import camelot

# ------------------------
# Logo
# ------------------------
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")
st.image("logo.png", width=200)

# ------------------------
# Sidebar Options
# ------------------------
st.sidebar.title("FinFET Demo Options")

demo_option = st.sidebar.radio("Choose Input Option:",
                               ["Synthetic Demo", "Predefined PDF", "Browse PDF"])

pdf_options = {
    "Arxiv 1905.11207 v3": "pdfs/1905.11207v3.pdf",
    "Arxiv 2007.13168 v4": "pdfs/2007.13168v4.pdf",
    "Arxiv 2007.14448 v1": "pdfs/2007.14448v1.pdf",
    "Arxiv 2407.18187 v1": "pdfs/2407.18187v1.pdf",
    "Arxiv 2501.15190 v1": "pdfs/2501.15190v1.pdf"
}

uploaded_file = None
selected_pdf = None

if demo_option == "Predefined PDF":
    selected_pdf = st.sidebar.selectbox("Select PDF", list(pdf_options.keys()))
elif demo_option == "Browse PDF":
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

# ------------------------
# Synthetic Demo Dataset
# ------------------------
def synthetic_parameters():
    """Enhanced synthetic FinFET dataset"""
    data = [
        {"Node":"7 nm","Lg (nm)":15,"Hfin (nm)":40,"EOT (nm)":0.6,"ID (A/cm²)":1.8e4,"Vth (V)":0.32,"Ion/Ioff":2.5e6,"gm (µS/µm)":2600},
        {"Node":"5 nm","Lg (nm)":12,"Hfin (nm)":45,"EOT (nm)":0.55,"ID (A/cm²)":2.0e4,"Vth (V)":0.30,"Ion/Ioff":3.0e6,"gm (µS/µm)":2800},
        {"Node":"4 nm","Lg (nm)":9,"Hfin (nm)":50,"EOT (nm)":0.50,"ID (A/cm²)":2.3e4,"Vth (V)":0.28,"Ion/Ioff":4.0e6,"gm (µS/µm)":3100},
        {"Node":"3 nm","Lg (nm)":7,"Hfin (nm)":55,"EOT (nm)":0.48,"ID (A/cm²)":2.6e4,"Vth (V)":0.25,"Ion/Ioff":5.0e6,"gm (µS/µm)":3400},
        {"Node":"2 nm","Lg (nm)":5,"Hfin (nm)":60,"EOT (nm)":0.45,"ID (A/cm²)":2.9e4,"Vth (V)":0.22,"Ion/Ioff":6.0e6,"gm (µS/µm)":3600},
    ]
    return pd.DataFrame(data)

# ------------------------
# Automatic Id-Vg Curve Detection
# ------------------------
def extract_id_vg_from_image(img_pil):
    """Detect curves in an image automatically and return Vg vs Id"""
    img = np.array(img_pil.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3),0)
    edges = cv2.Canny(gray,50,150)
    contours,_ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    curves = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 50:
            continue
        xs, ys = cnt[:,0,0], cnt[:,0,1]
        # invert y-axis for plotting
        ys = np.max(ys) - ys
        curves.append({"x": xs, "y": ys})
    return curves

# ------------------------
# Display Scaling Plots
# ------------------------
def plot_scaling(df):
    st.subheader("Scaling Plots")
    fig, ax = plt.subplots(2,2, figsize=(12,8))
    # Lg vs gm
    ax[0,0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker='o')
    ax[0,0].set_xlabel("Lg (nm)"); ax[0,0].set_ylabel("gm (µS/µm)")
    ax[0,0].set_title("Lg vs gm")
    # Vth vs Ion/Ioff
    ax[0,1].plot(df["Vth (V)"], df["Ion/Ioff"], marker='o', color='green')
    ax[0,1].set_xlabel("Vth (V)"); ax[0,1].set_ylabel("Ion/Ioff")
    ax[0,1].set_title("Vth vs Ion/Ioff")
    # ID vs Lg
    ax[1,0].plot(df["Lg (nm)"], df["ID (A/cm²)"], marker='o', color='red')
    ax[1,0].set_xlabel("Lg (nm)"); ax[1,0].set_ylabel("ID (A/cm²)")
    ax[1,0].set_title("ID vs Lg")
    # gm vs Ion/Ioff
    ax[1,1].plot(df["gm (µS/µm)"], df["Ion/Ioff"], marker='o', color='orange')
    ax[1,1].set_xlabel("gm (µS/µm)"); ax[1,1].set_ylabel("Ion/Ioff")
    ax[1,1].set_title("gm vs Ion/Ioff")
    plt.tight_layout()
    st.pyplot(fig)

# ------------------------
# Main Display
# ------------------------
if demo_option == "Synthetic Demo":
    df = synthetic_parameters()
    st.subheader("Synthetic FinFET Dataset")
    st.dataframe(df)
    plot_scaling(df)
    # Generate synthetic Id-Vg curve
    st.subheader("Synthetic Id-Vg Curves")
    Vg = np.linspace(0,1,50)
    for idx, row in df.iterrows():
        Id = row["ID (A/cm²)"] * (1-np.exp(-Vg/row["Vth (V)"]))
        st.line_chart(pd.DataFrame({"Vg": Vg, f"Id Node {row['Node']}": Id}).set_index("Vg"))

elif demo_option == "Predefined PDF" or demo_option == "Browse PDF":
    if demo_option == "Predefined PDF" and selected_pdf:
        pdf_path = pdf_options[selected_pdf]
    elif demo_option == "Browse PDF" and uploaded_file:
        pdf_path = uploaded_file
    else:
        pdf_path = None

    if pdf_path:
        st.subheader("PDF Processing Results")
        # Convert PDF to images
        try:
            if isinstance(pdf_path, str):
                pages = convert_from_path(pdf_path, dpi=300)
            else:
                pages = convert_from_path(pdf_path, dpi=300, first_page=0)
        except Exception as e:
            st.error(f"PDF to Image conversion failed: {e}")
            pages = []

        all_curves = []
        for i, img in enumerate(pages):
            st.markdown(f"**Page {i+1}**")
            curves = extract_id_vg_from_image(img)
            if curves:
                st.success(f"Detected {len(curves)} curve(s) automatically")
                for j,c in enumerate(curves):
                    df_curve = pd.DataFrame({"Vg (a.u.)": c["x"], "Id (a.u.)": c["y"]})
                    st.line_chart(df_curve.set_index("Vg (a.u.)"))
            else:
                st.warning("No curves detected automatically. PDF quality may be low or axes not clear.")

        # Table extraction with Camelot
        if isinstance(pdf_path, str):
            try:
                tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
                st.subheader("Extracted Tables")
                if tables:
                    for ti, table in enumerate(tables):
                        st.write(f"Table {ti+1}")
                        st.dataframe(table.df)
                else:
                    st.warning("No tables detected. Try clearer PDFs.")
            except Exception as e:
                st.warning(f"Table extraction failed: {e}")
