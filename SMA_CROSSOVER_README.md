# 50 SMA Crossover Analysis

This document describes the 50-period Simple Moving Average (SMA) crossover analysis feature for the S&P 500 index.

## Overview

This feature analyzes historical price data for the S&P 500 index to identify and evaluate 50-period SMA crossover points. When the price crosses above the 50 SMA (bullish crossover), it can signal a potential buying opportunity. This analysis evaluates the historical performance of such signals.

## Features

### Data Collection
- Fetches historical S&P 500 data (up to 20 years) from Yahoo Finance
- Supports multiple timeframes: 4-hour, Daily, Weekly, and Monthly
- Includes synthetic data fallback for testing when real data is unavailable

### Analysis Metrics

For each timeframe, the analysis calculates:

1. **Crossover Events**: Total number of times price crossed above the 50 SMA
2. **Price Behavior**:
   - How many times price touched SMA again after crossover
   - How many times price bounced away from SMA
   - Average bounce points

3. **Trading Performance**:
   - Average points captured if entering at crossover
   - Maximum and minimum points captured
   - Number of winning vs. losing trades
   - Winning rate percentage

4. **Risk Metrics**:
   - Average maximum gain percentage and points
   - Average maximum drawdown percentage and points
   - Suggested stop-loss levels based on historical drawdowns
   - Average recovery time (how long to return to entry price)

5. **Directional Analysis**:
   - Times price went down then recovered
   - Times price went up continuously

## Usage

### Running the Analysis

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Select "50 SMA Crossover Analysis" from the sidebar

3. Configure the analysis parameters:
   - **Years of Historical Data**: 5-20 years (default: 20)
   - **SMA Period**: 10-200 periods (default: 50)

4. Click "Run Analysis" to start

### Interpreting Results

The analysis provides:

1. **Summary Table**: Comprehensive view of all timeframes
2. **Key Metrics Dashboard**: High-level overview of performance
3. **Detailed Breakdowns**: Per-timeframe statistics
4. **Trading Recommendations**: Strategy suggestions based on results
5. **CSV Export**: Download results for further analysis

## Data Source

- **Primary**: Yahoo Finance (^GSPC ticker for S&P 500)
- **Fallback**: Synthetic data generation for demo/testing purposes
- **Note**: Intraday data (4-hour) is limited to ~730 days by Yahoo Finance API

## Technical Details

### Implementation

The analysis is implemented in `sma_crossover_analysis.py` with the following key components:

- `SMACrossoverAnalyzer`: Main analysis class
  - `fetch_data()`: Retrieves historical data
  - `calculate_sma()`: Computes SMA for given period
  - `identify_crossovers()`: Finds bullish crossover points
  - `analyze_crossover()`: Evaluates post-crossover behavior
  - `run_full_analysis()`: Executes analysis across all timeframes

### Dependencies

Required Python packages:
- `yfinance`: Historical market data
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `scipy`: Statistical analysis (optional)
- `streamlit`: Web interface
- `matplotlib`: Plotting

## Limitations

1. **Past Performance**: Historical results don't guarantee future performance
2. **Data Availability**: Intraday data limited to ~2 years
3. **Market Conditions**: Analysis doesn't account for fundamental changes
4. **Transaction Costs**: Results don't include fees, spreads, or slippage
5. **Look-ahead Bias**: Analysis uses historical data with perfect hindsight

## Disclaimer

This tool is for **educational and research purposes only**. It should not be considered as financial advice. Always:

- Conduct your own research
- Consider your risk tolerance
- Consult with financial advisors before making investment decisions
- Be aware that past performance doesn't indicate future results

## Example Output

```
Timeframe: Daily
Total Crossovers: 67
Winning Rate: 73.13%
Avg Points Captured: 370.89
Suggested Stop Loss: 8.24%
```

## Future Enhancements

Potential improvements:
- Additional technical indicators (RSI, MACD, etc.)
- Backtesting with actual trade execution logic
- Risk management scenarios (position sizing, etc.)
- Multiple SMA period comparisons
- Other market indices support
- Real-time alert system

## Support

For issues or questions, please refer to the main README.md or contact the repository maintainer.
