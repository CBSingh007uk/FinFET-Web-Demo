import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Minimal Test App 🚀")

x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
st.pyplot(fig)
