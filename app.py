import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from fpdf import FPDF

# -------------------------------
# Synthetic Demo Functions
# -------------------------------

def synthetic_parameters():
    """IRDS-aligned synthetic FinFET dataset for 3–5 nm nodes"""
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


def export_excel(df):
    """Export dataframe to Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="FinFET_Data")
    return output.getvalue()


def export_pdf(df, logo_path="logo.png"):
    """Export dataframe to PDF with logo"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Add logo if available
    try:
        pdf.image(logo_path, 10, 8, 33)  # x, y, width
    except:
        pass

    pdf.cell(200, 10, "Synthetic FinFET Parameters (3–5 nm)", ln=True, align="C")
    pdf.ln(20)

    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)

    # Header
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()

    # Rows
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(col_width, 10, str(val), border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin1")


def show_synthetic_demo():
    st.subheader("📊 Synthetic Demo (3–5 nm IRDS-aligned FinFET Parameters)")
    df = synthetic_parameters()
    st.dataframe(df, use_container_width=True)

    # Scaling plots
    st.markdown("### 📈 Scaling Trends")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(df["Lg (nm)"], df["gm (µS/µm)"], marker="o", color="cyan", linewidth=2)
    axes[0].invert_xaxis()
    axes[0].set_xlabel("Lg (nm)")
    axes[0].set_ylabel("gm (µS/µm)")
    axes[0].set_title("Lg vs gm")

    axes[1].plot(df["Vth (V)"], df["Ion/Ioff"], marker="s", color="magenta", linewidth=2)
    axes[1].set_xlabel("Vth (V)")
    axes[1].set_ylabel("Ion/Ioff")
    axes[1].set_title("Vth vs Ion/Ioff")

    st.pyplot(fig)

    # Downloads
    st.markdown("### 💾 Export Data")
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "synthetic_finfet.csv", "text/csv")
    st.download_button("⬇️ Download Excel", export_excel(df), "synthetic_finfet.xlsx")
    st.download_button("⬇️ Download PDF", export_pdf(df), "synthetic_finfet.pdf")


# -------------------------------
# Streamlit Page Layout
# -------------------------------

# Page config
st.set_page_config(page_title="FinFET Data Extractor", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #1c1c1c, #2e2e2e);
            color: #f0f0f0;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 0.6em 1.2em;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .css-18e3th9, .css-1d391kg {  /* Sidebar text */
            color: #f0f0f0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header with logo
st.image("logo.png", width=100)
st.title("FinFET Data Extractor")
st.caption("Upload → OCR → Extract Parameters or run Synthetic Demo")

# Sidebar navigation
menu = ["Synthetic Demo", "Upload & Extract (Coming Soon)"]
choice = st.sidebar.radio("Navigate", menu)

if choice == "Synthetic Demo":
    show_synthetic_demo()
else:
    st.info("📂 Upload and parameter extraction pipeline will appear here.")
