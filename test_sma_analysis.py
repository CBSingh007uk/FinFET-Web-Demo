#!/usr/bin/env python3
"""
Test script for SMA Crossover Analysis
"""

import sys
sys.path.insert(0, '/home/runner/work/FinFET-Web-Demo/FinFET-Web-Demo')

from sma_crossover_analysis import SMACrossoverAnalyzer, format_analysis_table

def test_analysis():
    """Test the SMA crossover analysis"""
    print("Testing SMA Crossover Analysis...")
    print("=" * 60)
    
    # Test with 5 years of data for faster testing
    analyzer = SMACrossoverAnalyzer(years=5, sma_period=50)
    
    print("\n1. Testing data fetch (Daily)...")
    data = analyzer.fetch_data('1d')
    if data is not None:
        print(f"   ✓ Successfully fetched {len(data)} daily data points")
    else:
        print("   ✗ Failed to fetch data")
        return False
    
    print("\n2. Testing SMA calculation...")
    df = analyzer.calculate_sma(data)
    if df is not None and 'SMA' in df.columns:
        print(f"   ✓ Successfully calculated SMA")
        print(f"   ✓ SMA values: {df['SMA'].dropna().iloc[:5].values}")
    else:
        print("   ✗ Failed to calculate SMA")
        return False
    
    print("\n3. Testing crossover identification...")
    crossovers = analyzer.identify_crossovers(df)
    print(f"   ✓ Found {len(crossovers)} crossovers")
    if len(crossovers) > 0:
        print(f"   ✓ First crossover at index: {crossovers[0]}")
    
    print("\n4. Testing single crossover analysis...")
    if len(crossovers) > 0:
        analysis = analyzer.analyze_crossover(df, crossovers[0])
        if analysis is not None:
            print(f"   ✓ Entry Price: ${analysis['entry_price']:.2f}")
            print(f"   ✓ Points Captured: {analysis['points_captured']:.2f}")
            print(f"   ✓ Max Gain: {analysis['max_gain']:.2f}%")
            print(f"   ✓ Max Drawdown: {analysis['max_drawdown']:.2f}%")
            print(f"   ✓ Profitable: {analysis['profitable']}")
        else:
            print("   ✗ Failed to analyze crossover")
            return False
    
    print("\n5. Testing full analysis...")
    results = analyzer.run_full_analysis()
    if results is not None and len(results) > 0:
        print(f"   ✓ Successfully analyzed {len(results)} timeframes")
        print("\n   Results summary:")
        for idx, row in results.iterrows():
            print(f"   - {row['timeframe']}: {int(row['total_crossovers'])} crossovers, "
                  f"{row['winning_rate']:.1f}% win rate")
    else:
        print("   ✗ Failed to run full analysis")
        return False
    
    print("\n6. Testing table formatting...")
    formatted = format_analysis_table(results)
    if formatted is not None:
        print(f"   ✓ Successfully formatted results")
        print(f"   ✓ Columns: {list(formatted.columns)[:5]}...")
    else:
        print("   ✗ Failed to format table")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("\nSample Results:")
    print(formatted.to_string())
    
    return True

if __name__ == "__main__":
    try:
        success = test_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
