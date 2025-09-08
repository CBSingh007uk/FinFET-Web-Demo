import re
import os
import fitz  # PyMuPDF
import easyocr
import pandas as pd
from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image
import matplotlib.pyplot as plt

# -------------------------------
# Standardized parameter mapping
# -------------------------------
STANDARD_PARAMS = {
    "Lg": {"units": ["nm"], "standard_unit": "nm"},
    "Hfin": {"units": ["nm"], "standard_unit": "nm"},
    "Tfin": {"units": ["nm"], "standard_unit": "nm"},
    "Wfin": {"units": ["nm"], "standard_unit": "nm"},
    "EOT": {"units": ["nm"], "standard_unit": "nm"},
    "Vth": {"units": ["V"], "standard_unit": "V"},
    "Ion": {"units": ["uA", "A/cm2"], "standard_unit": "uA"},
    "Ioff": {"units": ["uA", "A/cm2"], "standard_unit": "uA"},
    "Ion/Ioff": {"units": [], "standard_unit": "ratio"},
    "SS": {"units": ["mV/dec"], "standard_unit": "mV/dec"},
    "DIBL": {"units": ["mV/V"], "standard_unit": "mV/V"},
    "IOFF": {"units": ["uA/um", "nA/um"], "standard_unit": "uA/um"},
}

UNIT_CONVERSIONS = {
    "nm": lambda x: x,
    "V": lambda x: x,
    "uA": lambda x: x,
    "A/cm2": lambda x: x * 1e6,  # → µA/cm²
    "mV/dec": lambda x: x,
    "mV/V": lambda x: x,
    "uA/um": lambda x: x,
    "nA/um": lambda x: x * 1e-3,  # → µA/um
}

# -------------------------------
# PDF and OCR Processing
# -------------------------------
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

def extract_text_from_image(image_path):
    """Extract text from an image using EasyOCR."""
    reader = easyocr.Reader(["en"])
    results = reader.readtext(image_path)
    return " ".join([res[1] for res in results])

# -------------------------------
# Parameter Extraction
# -------------------------------
def extract_parameters(text):
    """Extract parameters using regex."""
    patterns = {
        "Lg": r"Lg\s*=\s*([\d\.]+)\s*nm",
        "Hfin": r"Hfin\s*=\s*([\d\.]+)\s*nm",
        "Tfin": r"Tfin\s*=\s*([\d\.]+)\s*nm",
        "Wfin": r"Wfin\s*=\s*([\d\.]+)\s*nm",
        "EOT": r"EOT\s*=\s*([\d\.]+)\s*nm",
        "Vth": r"Vth\s*=?\s*([-+]?\d*\.?\d+)\s*V",
        "Ion": r"Ion\s*=\s*([\d\.eE+-]+)\s*(uA|A/cm2)",
        "Ioff": r"Ioff\s*=\s*([\d\.eE+-]+)\s*(uA|A/cm2)",
        "Ion/Ioff": r"Ion/Ioff\s*=?\s*([\d\.eE+-]+)",
        "SS": r"SS\s*=\s*([\d\.]+)\s*mV/dec",
        "DIBL": r"DIBL\s*=\s*([\d\.]+)\s*mV/V",
        "IOFF": r"IOFF\s*=?\s*([\d\.]+)\s*(uA/um|nA/um)",
    }

    extracted = {}
    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                extracted[param] = f"{match.group(1)} {match.group(2)}"
            else:
                extracted[param] = match.group(1)
    return extracted

def normalize_value_with_unit(param, raw_value):
    """Normalize extracted value into standard unit."""
    if param not in STANDARD_PARAMS or raw_value is None:
        return None
    try:
        if any(u in raw_value for u in ["nm", "V", "uA", "A/cm2", "mV/dec", "mV/V", "uA/um", "nA/um"]):
            num = float(re.findall(r"[-+]?\d*\.?\d+[eE]?[+-]?\d*", raw_value)[0])
            for unit in STANDARD_PARAMS[param]["units"]:
                if unit in raw_value:
                    return UNIT_CONVERSIONS[unit](num)
        else:
            return float(raw_value)
    except Exception:
        return None
    return None

# -------------------------------
# Table & Figure Extraction
# -------------------------------
def extract_tables_from_pdf(pdf_path):
    """Placeholder: Extract tables from PDF (requires Camelot/Tabula)."""
    return None

def extract_figures_from_pdf(pdf_path, output_folder="figures"):
    """Extract figures from PDF as images."""
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path)
    paths = []
    for i, img in enumerate(images):
        out_path = os.path.join(output_folder, f"page_{i+1}.png")
        img.save(out_path, "PNG")
        paths.append(out_path)
    return paths

# -------------------------------
# Main Processing
# -------------------------------
def process_file(file_path):
    """Process a single PDF or image."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)

    params_raw = extract_parameters(text)

    params_normalized = {}
    for p, val in params_raw.items():
        params_normalized[p] = normalize_value_with_unit(p, val)

    return params_raw, params_normalized, text

# -------------------------------
# Run pipeline
# -------------------------------
if __name__ == "__main__":
    folder = "pdfs"
    results_raw = []
    results_norm = []

    for fname in os.listdir(folder):
        if not fname.endswith(".pdf"):
            continue
        fpath = os.path.join(folder, fname)
        print(f"Processing {fname}...")

        raw, norm, text = process_file(fpath)

        raw["Source"] = fname
        norm["Source"] = fname

        results_raw.append(raw)
        results_norm.append(norm)

    df_raw = pd.DataFrame(results_raw)
    df_norm = pd.DataFrame(results_norm)

    df_raw.to_csv("params_raw.csv", index=False)
    df_norm.to_csv("params_normalized.csv", index=False)

    print("✅ Extraction complete. Files saved: params_raw.csv, params_normalized.csv")
