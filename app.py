import streamlit as st

st.title("Matplotlib Test App")

try:
    import matplotlib.pyplot as plt
    import numpy as np

    st.success("✅ Matplotlib imported successfully!")

    # Simple test plot
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y, label="sin(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()

    st.pyplot(fig)

except ModuleNotFoundError as e:
    st.error(f"❌ Matplotlib not installed: {e}")
