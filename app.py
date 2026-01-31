# app.py - Minimal Working Demo
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# ---------------------------
# Logo
# ---------------------------
logo_path = "logo.png"  # Make sure logo.png is in the same folder
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)
    st.image(logo_path, width=200)
else:
    st.sidebar.write("Logo not found")

# ---------------------------
# Sidebar Option
# ---------------------------
st.sidebar.header("Demo Mode")
option = st.sidebar.selectbox(
    "Select Demo Mode:",
    
)

# ---------------------------
# Synthetic Demo Data
# ---------------------------
def synthetic_parameters():
    data = [
        {"Node":"7nm","Lg (nm)":15,"gm (µS/µm)":2600,"Vth (V)":0.32,"Ion/Ioff":2.5e6},
        {"Node":"5nm","Lg (nm)":12,"gm (µS/µm)":2800,"Vth (V)":0.30,"Ion/Ioff":3.0e6},
        {"Node":"4nm","Lg (nm)":9,"gm (µS/µm)":3100,"Vth (V)":0.28,"Ion/Ioff":4.0e6},
        {"Node":"3nm","Lg (nm)":7,"gm (µS/µm)":3400,"Vth (V)":0.25,"Ion/Ioff":5.0e6},
        {"Node":"2nm","Lg (nm)":5,"gm (µS/µm)":3600,"Vth (V)":0.22,"Ion/Ioff":6.0e6},
    ]
    return pd.DataFrame(data)

# ---------------------------
# Plot Scaling Demo
# ---------------------------
def plot_scaling(df):
    fig, axs = plt.subplots(1, 2, figsize=(10,4))
    axs[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], 'o-')
    axs[0].set_xlabel("Lg (nm)")
    axs[0].set_ylabel("gm (µS/µm)")
    axs[0].set_title("Lg vs gm")

    axs[1].plot(df["Vth (V)"], df["Ion/Ioff"], 's-')
    axs[1].set_xlabel("Vth (V)")
    axs[1].set_ylabel("Ion/Ioff")
    axs[1].set_title("Vth vs Ion/Ioff")

    plt.tight_layout()
    st.pyplot(fig)

# ---------------------------
# Run Demo
# ---------------------------
if option == "Synthetic Demo":
    st.header("Synthetic FinFET Demo")
    df = synthetic_parameters()
    st.subheader("Parameters Table")
    st.dataframe(df)
    st.subheader("Scaling Plots")
    plot_scaling(df)

