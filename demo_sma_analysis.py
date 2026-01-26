#!/usr/bin/env python3
"""
Demo script to showcase the SMA Crossover Analysis output
"""

import sys
import os
import pandas as pd

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from sma_crossover_analysis import SMACrossoverAnalyzer, format_analysis_table

def main():
    """Run a quick demo of the analysis"""
    print("=" * 80)
    print("50-PERIOD SMA CROSSOVER ANALYSIS - S&P 500 INDEX")
    print("=" * 80)
    print()
    
    print("Initializing analyzer with 5 years of data (for faster demo)...")
    analyzer = SMACrossoverAnalyzer(years=5, sma_period=50)
    
    print("Running comprehensive analysis across multiple timeframes...")
    print("(This uses synthetic data since Yahoo Finance is unavailable in this environment)")
    print()
    
    results = analyzer.run_full_analysis()
    
    if results is not None and len(results) > 0:
        formatted = format_analysis_table(results)
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print()
        
        # Display summary
        print("📊 SUMMARY STATISTICS")
        print("-" * 80)
        print(f"Total Timeframes Analyzed: {len(results)}")
        print(f"Total Crossover Events: {int(results['total_crossovers'].sum())}")
        print(f"Average Winning Rate: {results['winning_rate'].mean():.2f}%")
        print(f"Average Points Captured: {results['avg_points_captured'].mean():.2f}")
        print(f"Average Suggested Stop Loss: {results['avg_suggested_stoploss'].mean():.2f}%")
        print()
        
        # Display detailed table
        print("\n📈 DETAILED BREAKDOWN BY TIMEFRAME")
        print("-" * 80)
        print()
        
        for idx, row in results.iterrows():
            # Skip timeframes with no crossovers
            if row['total_crossovers'] == 0:
                print(f"▸ {row['timeframe'].upper()} TIMEFRAME")
                print(f"  • No crossover events found in this timeframe")
                print(f"  • Data Period: {row['period_start'].strftime('%Y-%m-%d')} to {row['period_end'].strftime('%Y-%m-%d')}")
                print()
                continue
            
            print(f"▸ {row['timeframe'].upper()} TIMEFRAME")
            print(f"  • Total Crossovers: {int(row['total_crossovers'])}")
            print(f"  • Winning Rate: {row['winning_rate']:.2f}%")
            print(f"  • Winning Trades: {int(row['winning_trades'])} | Losing Trades: {int(row['losing_trades'])}")
            print(f"  • Avg Points Captured: {row['avg_points_captured']:.2f}")
            print(f"  • Max Points Captured: {row['max_points_captured']:.2f}")
            print(f"  • Min Points Captured: {row['min_points_captured']:.2f}")
            print(f"  • Avg Max Gain: {row['avg_max_gain']:.2f}% ({row['avg_max_gain_points']:.2f} pts)")
            print(f"  • Avg Max Drawdown: {row['avg_max_drawdown']:.2f}% ({row['avg_max_drawdown_points']:.2f} pts)")
            print(f"  • Suggested Stop Loss: {row['avg_suggested_stoploss']:.2f}%")
            
            if row['avg_days_to_recovery'] is not None and not pd.isna(row['avg_days_to_recovery']):
                print(f"  • Avg Days to Recovery: {row['avg_days_to_recovery']:.2f}")
            
            print(f"  • Price Behavior:")
            print(f"    - Touched SMA Again: {int(row['touched_sma_count'])} times")
            print(f"    - Bounced: {int(row['bounced_count'])} times (avg {row['avg_bounce_points']:.2f} pts)")
            print(f"    - Went Down Then Up: {int(row['went_down_then_up_count'])} times")
            print(f"    - Went Up Continuously: {int(row['went_up_continuously_count'])} times")
            print(f"  • Data Period: {row['period_start'].strftime('%Y-%m-%d')} to {row['period_end'].strftime('%Y-%m-%d')}")
            print()
        
        print("\n" + "=" * 80)
        print("KEY INSIGHTS")
        print("=" * 80)
        print()
        print("✓ The analysis shows crossover patterns across different timeframes")
        print("✓ Winning rates vary by timeframe - longer timeframes often show higher win rates")
        print("✓ Average drawdown suggests appropriate stop-loss levels")
        print("✓ Recovery time indicates how long positions may need to be held")
        print()
        print("⚠️  DISCLAIMER: This analysis is for educational purposes only.")
        print("   Past performance does not guarantee future results.")
        print("=" * 80)
        
        # Save to file
        csv_file = '/tmp/sma_crossover_results.csv'
        formatted.to_csv(csv_file, index=False)
        print(f"\n💾 Results saved to: {csv_file}")
        print()
        
    else:
        print("❌ No results generated. Please check the data and try again.")

if __name__ == "__main__":
    main()
