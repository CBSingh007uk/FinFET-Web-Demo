# FinFET Data Extractor Web App

## Features

This application provides two main functionalities:

1. **Synthetic FinFET Demo**: Visualization of FinFET scaling parameters
2. **50 SMA Crossover Analysis**: Comprehensive analysis of 50-period Simple Moving Average crossovers on the S&P 500 index across multiple timeframes

## Run Locally
1. Clone the folder and activate your Python environment:
```bash
python -m venv env
.\env\Scripts\activate   # Windows
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## 50 SMA Crossover Analysis

This feature analyzes historical S&P 500 data to identify and evaluate 50-period SMA crossover opportunities. See [SMA_CROSSOVER_README.md](SMA_CROSSOVER_README.md) for detailed documentation.

### Quick Start
- Select "50 SMA Crossover Analysis" from the sidebar
- Configure analysis parameters (years, SMA period)
- Click "Run Analysis"
- Review comprehensive results and download CSV

### Key Metrics
- Total crossover events
- Winning rate and points captured
- Risk analysis (max gain, max drawdown)
- Suggested stop-loss levels
- Recovery time analysis
- Directional behavior tracking
