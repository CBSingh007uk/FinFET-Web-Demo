# ------------------------
# Helper: extract parameters using flexible regex
# ------------------------
def extract_parameters(text):
    params = {}

    patterns = {
        'Lg (nm)': r"Lg\s*[:=≃≈~]?\s*([\d\.]+)\s*\(?\s*nm\)?",
        'Hfin (nm)': r"Hfin\s*[:=≃≈~]?\s*([\d\.]+)\s*\(?\s*nm\)?",
        'EOT (nm)': r"EOT\s*[:=≃≈~]?\s*([\d\.]+)\s*\(?\s*nm\)?",
        'Vth (V)': r"Vth\s*[:=≃≈~]?\s*([\d\.]+)\s*\(?\s*V\)?",
        'ID (A/cm2)': r"(?:Id|ID|I_D|max Id|max ID|ID_max)\s*[:=≃≈~]?\s*([\d\.]+)\s*\(?\s*A/cm2\)?",
        'Ion/Ioff': r"Ion/Ioff\s*[:=≃≈~]?\s*([\deE\+\-\.]+)"
    }

    for key, pattern in patterns.items():
        try:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                val = match.group(1)
                # Convert to float where possible
                try:
                    val = float(val)
                except:
                    pass
                params[key] = val
        except:
            continue

    return pd.DataFrame([params]) if params else pd.DataFrame()
