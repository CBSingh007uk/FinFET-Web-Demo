# app.py - Minimal Working Demo
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from sma_crossover_analysis import SMACrossoverAnalyzer, format_analysis_table

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
    ["Synthetic Demo", "50 SMA Crossover Analysis"]
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

elif option == "50 SMA Crossover Analysis":
    st.header("50-Period SMA Crossover Analysis - S&P 500 Index")
    
    st.info("""
    **Data Source Notice:** This analysis attempts to fetch real S&P 500 data from Yahoo Finance. 
    If the data is unavailable (e.g., due to network restrictions), synthetic demo data will be used instead.
    """)
    
    st.write("Analysis of price crossovers with 50-period Simple Moving Average on S&P 500 index")
    
    # Configuration options
    st.sidebar.subheader("Analysis Configuration")
    years = st.sidebar.slider("Years of Historical Data", min_value=5, max_value=20, value=20, step=1)
    sma_period = st.sidebar.number_input("SMA Period", min_value=10, max_value=200, value=50, step=10)
    
    # Run analysis button
    if st.button("Run Analysis", type="primary"):
        with st.spinner("Fetching data and analyzing crossovers... This may take a few minutes."):
            try:
                # Initialize analyzer
                analyzer = SMACrossoverAnalyzer(years=years, sma_period=sma_period)
                
                # Run full analysis
                results_df = analyzer.run_full_analysis()
                
                if results_df is not None and len(results_df) > 0:
                    # Format results
                    formatted_df = format_analysis_table(results_df)
                    
                    st.success("Analysis Complete!")
                    
                    # Display summary
                    st.subheader("Analysis Summary")
                    st.write(f"**Period Analyzed:** {years} years")
                    st.write(f"**SMA Period:** {sma_period}")
                    st.write(f"**Index:** S&P 500 (^GSPC)")
                    
                    # Display main results table
                    st.subheader("Comprehensive Analysis Results")
                    st.dataframe(formatted_df, use_container_width=True)
                    
                    # Key insights
                    st.subheader("Key Insights")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Timeframes Analyzed", len(results_df))
                        st.metric("Total Crossovers", int(results_df['total_crossovers'].sum()))
                    
                    with col2:
                        avg_winning_rate = results_df['winning_rate'].mean()
                        st.metric("Average Winning Rate", f"{avg_winning_rate:.2f}%")
                        avg_points = results_df['avg_points_captured'].mean()
                        st.metric("Avg Points Captured", f"{avg_points:.2f}")
                    
                    with col3:
                        avg_drawdown = results_df['avg_max_drawdown'].mean()
                        st.metric("Avg Max Drawdown", f"{avg_drawdown:.2f}%")
                        avg_stoploss = results_df['avg_suggested_stoploss'].mean()
                        st.metric("Suggested Stop Loss", f"{avg_stoploss:.2f}%")
                    
                    # Detailed breakdown by timeframe
                    st.subheader("Breakdown by Timeframe")
                    
                    for idx, row in results_df.iterrows():
                        with st.expander(f"📊 {row['timeframe']} Timeframe Details"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Trading Statistics:**")
                                st.write(f"- Total Crossovers: {int(row['total_crossovers'])}")
                                st.write(f"- Winning Trades: {int(row['winning_trades'])}")
                                st.write(f"- Losing Trades: {int(row['losing_trades'])}")
                                st.write(f"- Winning Rate: {row['winning_rate']:.2f}%")
                                st.write(f"- Avg Points Captured: {row['avg_points_captured']:.2f}")
                                st.write(f"- Max Points Captured: {row['max_points_captured']:.2f}")
                                st.write(f"- Min Points Captured: {row['min_points_captured']:.2f}")
                            
                            with col2:
                                st.write("**Risk Analysis:**")
                                st.write(f"- Avg Max Gain: {row['avg_max_gain']:.2f}%")
                                st.write(f"- Avg Max Drawdown: {row['avg_max_drawdown']:.2f}%")
                                st.write(f"- Suggested Stop Loss: {row['avg_suggested_stoploss']:.2f}%")
                                if row['avg_days_to_recovery'] is not None and not np.isnan(row['avg_days_to_recovery']):
                                    st.write(f"- Avg Days to Recovery: {row['avg_days_to_recovery']:.2f}")
                                else:
                                    st.write(f"- Avg Days to Recovery: N/A")
                            
                            st.write("**Behavior Analysis:**")
                            st.write(f"- Times Price Touched SMA Again: {int(row['touched_sma_count'])}")
                            st.write(f"- Times Price Bounced: {int(row['bounced_count'])}")
                            st.write(f"- Avg Bounce Points: {row['avg_bounce_points']:.2f}")
                            st.write(f"- Went Down Then Up: {int(row['went_down_then_up_count'])} times")
                            st.write(f"- Went Up Continuously: {int(row['went_up_continuously_count'])} times")
                    
                    # Trading recommendations
                    st.subheader("📈 Trading Recommendations")
                    st.info("""
                    **Based on the analysis:**
                    
                    1. **Stop Loss Strategy:** Use the suggested stop loss percentages shown for each timeframe to manage risk.
                    
                    2. **Position Sizing:** Consider the average drawdown when determining position size.
                    
                    3. **Timeframe Selection:** Compare winning rates across timeframes to identify the most profitable periods.
                    
                    4. **Recovery Time:** Factor in the average recovery time when planning holding periods.
                    
                    5. **Risk-Reward:** Review the average max gain vs. max drawdown to assess risk-reward ratios.
                    
                    **Disclaimer:** This analysis is for educational purposes only. Past performance does not guarantee future results.
                    """)
                    
                    # Download option
                    csv = formatted_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"sma_crossover_analysis_{years}years.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.error("No crossover data found. Please try different parameters.")
            
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
                st.write("Please check your internet connection and try again.")
    
    else:
        st.info("👆 Click 'Run Analysis' to start the 50-period SMA crossover analysis on S&P 500 index.")
        st.write("""
        ### What This Analysis Does:
        
        This tool analyzes 50-period Simple Moving Average (SMA) crossovers with price on the S&P 500 index across multiple timeframes:
        
        - **4-Hour** (limited to ~2 years of data)
        - **Daily**
        - **Weekly**
        - **Monthly**
        
        ### Metrics Calculated:
        
        1. **Total Crossovers:** Number of times price crossed above the 50 SMA
        2. **Price Behavior:** How many times price went back to touch SMA vs. bounced away
        3. **Points Captured:** Average and maximum points that could be captured from each crossover
        4. **Winning Rate:** Percentage of profitable trades if entered at crossover
        5. **Stop Loss Suggestions:** Optimal stop loss levels based on historical drawdowns
        6. **Recovery Analysis:** How long it took for price to recover when it went down
        7. **Directional Behavior:** Whether price went up continuously or dipped then recovered
        
        ### How to Use:
        
        1. Adjust the configuration in the sidebar (years of data, SMA period)
        2. Click "Run Analysis" 
        3. Review the comprehensive results table
        4. Explore detailed breakdowns for each timeframe
        5. Download the results for further analysis
        
        **Note:** Analysis uses historical data from Yahoo Finance. Data availability may vary by timeframe.
        """)
