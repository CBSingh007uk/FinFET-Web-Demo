"""
SMA Crossover Analysis Module
Analyzes 50-period SMA crossovers with price on S&P 500 index
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class SMACrossoverAnalyzer:
    """Analyzes 50-period SMA crossovers for S&P 500 index"""
    
    def __init__(self, years=20, sma_period=50):
        """
        Initialize analyzer
        
        Args:
            years: Number of years of historical data
            sma_period: SMA period (default 50)
        """
        self.years = years
        self.sma_period = sma_period
        self.ticker = "^GSPC"  # S&P 500 index
        
    def fetch_data(self, interval='1d'):
        """
        Fetch historical data from Yahoo Finance
        
        Args:
            interval: Data interval ('1d', '1wk', '1mo', '1h', '4h')
        
        Returns:
            DataFrame with OHLCV data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * self.years)
        
        # For hourly/4hr data, we need to adjust the period
        if interval in ['1h', '4h']:
            # Yahoo Finance limits intraday data to 730 days
            start_date = end_date - timedelta(days=729)
        
        try:
            data = yf.download(self.ticker, start=start_date, end=end_date, 
                             interval=interval, progress=False)
            
            # If download fails or returns empty, return synthetic demo data
            if data is None or len(data) == 0:
                print(f"⚠ Using synthetic demo data for {interval} (Yahoo Finance unavailable)")
                return self._generate_synthetic_data(interval)
            
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            print(f"⚠ Using synthetic demo data for {interval}")
            return self._generate_synthetic_data(interval)
    
    def _generate_synthetic_data(self, interval='1d'):
        """
        Generate synthetic S&P 500-like data for demonstration
        
        Args:
            interval: Data interval
        
        Returns:
            DataFrame with synthetic OHLCV data
        """
        # Determine number of periods based on interval
        if interval == '1h':
            periods = 730 * 24  # ~730 days of hourly data
            freq = 'h'
        elif interval == '4h':
            periods = 730 * 6  # ~730 days of 4-hour data
            freq = '4h'
        elif interval == '1d':
            periods = 365 * self.years  # Daily data
            freq = 'D'
        elif interval == '1wk':
            periods = 52 * self.years  # Weekly data
            freq = 'W'
        elif interval == '1mo':
            periods = 12 * self.years  # Monthly data
            freq = 'MS'  # Month Start instead of 'M'
        else:
            periods = 365 * self.years
            freq = 'D'
        
        # Generate date range
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=periods, freq=freq)
        
        # Ensure all arrays match the actual length of dates
        actual_periods = len(dates)
        
        # Generate synthetic price data with realistic S&P 500 characteristics
        np.random.seed(42)  # For reproducibility
        
        # Start at a realistic S&P 500 price
        initial_price = 3000
        
        # Generate returns with trend and volatility
        trend = 0.0003  # Slight upward trend
        volatility = 0.015  # Daily volatility ~1.5%
        
        returns = np.random.normal(trend, volatility, actual_periods)
        prices = initial_price * np.exp(np.cumsum(returns))
        
        # Add some cyclical patterns (simulate market cycles)
        cycle = 200 * np.sin(np.linspace(0, 4 * np.pi, actual_periods))
        prices = prices + cycle
        
        # Generate OHLC data
        high = prices * (1 + np.random.uniform(0, 0.01, actual_periods))
        low = prices * (1 - np.random.uniform(0, 0.01, actual_periods))
        open_price = prices + np.random.uniform(-10, 10, actual_periods)
        close_price = prices
        volume = np.random.uniform(3e9, 5e9, actual_periods)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close_price,
            'Volume': volume
        }, index=dates)
        
        return df
    
    def calculate_sma(self, data):
        """Calculate SMA for the given data"""
        if data is None or len(data) < self.sma_period:
            return None
        
        df = data.copy()
        df['SMA'] = df['Close'].rolling(window=self.sma_period).mean()
        return df
    
    def identify_crossovers(self, df):
        """
        Identify price crossover points with SMA
        
        Returns:
            List of crossover indices where price crosses above SMA
        """
        if df is None or 'SMA' not in df.columns:
            return []
        
        # Remove NaN values
        df = df.dropna(subset=['SMA'])
        
        if len(df) < 2:
            return []
        
        # Identify bullish crossovers (price crosses above SMA)
        crossovers = []
        for i in range(1, len(df)):
            prev_below = df['Close'].iloc[i-1] < df['SMA'].iloc[i-1]
            curr_above = df['Close'].iloc[i] >= df['SMA'].iloc[i]
            
            if prev_below and curr_above:
                crossovers.append(i)
        
        return crossovers
    
    def analyze_crossover(self, df, crossover_idx, lookforward_periods=100):
        """
        Analyze behavior after a crossover
        
        Args:
            df: DataFrame with price and SMA data
            crossover_idx: Index of crossover point
            lookforward_periods: Number of periods to analyze after crossover
        
        Returns:
            Dictionary with analysis results
        """
        if crossover_idx >= len(df) - 1:
            return None
        
        entry_price = df['Close'].iloc[crossover_idx]
        entry_sma = df['SMA'].iloc[crossover_idx]
        
        # Analyze future price movement
        end_idx = min(crossover_idx + lookforward_periods, len(df))
        future_data = df.iloc[crossover_idx:end_idx]
        
        analysis = {
            'entry_price': entry_price,
            'entry_sma': entry_sma,
            'entry_date': df.index[crossover_idx],
            'touched_sma_again': False,
            'days_to_touch_sma': None,
            'bounced': False,
            'bounce_points': 0,
            'max_gain': 0,
            'max_gain_points': 0,
            'max_drawdown': 0,
            'max_drawdown_points': 0,
            'days_to_recovery': None,
            'final_price': None,
            'points_captured': 0,
            'profitable': False,
            'suggested_stoploss_pct': 0,
            'went_down_then_up': False,
            'went_up_continuously': False
        }
        
        max_price = entry_price
        min_price = entry_price
        touched_sma = False
        recovery_date = None
        
        for i in range(1, len(future_data)):
            current_price = future_data['Close'].iloc[i]
            current_sma = future_data['SMA'].iloc[i]
            
            # Track max and min
            if current_price > max_price:
                max_price = current_price
            if current_price < min_price:
                min_price = current_price
            
            # Check if price touched SMA again
            if not touched_sma and current_price <= current_sma:
                touched_sma = True
                analysis['touched_sma_again'] = True
                analysis['days_to_touch_sma'] = i
            
            # Check for recovery to entry price
            if current_price < entry_price and recovery_date is None:
                pass  # Still below entry
            elif current_price >= entry_price and min_price < entry_price and recovery_date is None:
                recovery_date = i
                analysis['days_to_recovery'] = i
        
        # Calculate metrics
        analysis['max_gain'] = ((max_price - entry_price) / entry_price) * 100
        analysis['max_gain_points'] = max_price - entry_price
        analysis['max_drawdown'] = ((min_price - entry_price) / entry_price) * 100
        analysis['max_drawdown_points'] = min_price - entry_price
        
        # Final price (end of analysis period or last available)
        analysis['final_price'] = future_data['Close'].iloc[-1]
        analysis['points_captured'] = analysis['final_price'] - entry_price
        analysis['profitable'] = analysis['points_captured'] > 0
        
        # Determine bounce behavior
        if min_price >= entry_price * 0.98:  # Stayed above 2% below entry
            analysis['bounced'] = True
            analysis['bounce_points'] = analysis['max_gain_points']
            analysis['went_up_continuously'] = True
        elif analysis['days_to_recovery'] is not None:
            analysis['went_down_then_up'] = True
        
        # Suggested stop loss (based on maximum drawdown, add 1% buffer)
        if analysis['max_drawdown'] < -1:
            analysis['suggested_stoploss_pct'] = abs(analysis['max_drawdown']) + 1
        else:
            analysis['suggested_stoploss_pct'] = 2  # Default 2%
        
        return analysis
    
    def analyze_timeframe(self, interval, timeframe_name):
        """
        Analyze crossovers for a specific timeframe
        
        Args:
            interval: Yahoo Finance interval string
            timeframe_name: Human-readable timeframe name
        
        Returns:
            Dictionary with summary statistics
        """
        print(f"Analyzing {timeframe_name}...")
        
        # Fetch data
        data = self.fetch_data(interval)
        if data is None or len(data) == 0:
            return None
        
        # Calculate SMA
        df = self.calculate_sma(data)
        if df is None:
            return None
        
        # Identify crossovers
        crossovers = self.identify_crossovers(df)
        
        if len(crossovers) == 0:
            return {
                'timeframe': timeframe_name,
                'total_crossovers': 0,
                'data_points': len(df),
                'period_start': df.index[0] if len(df) > 0 else None,
                'period_end': df.index[-1] if len(df) > 0 else None
            }
        
        # Analyze each crossover
        analyses = []
        for idx in crossovers:
            result = self.analyze_crossover(df, idx)
            if result is not None:
                analyses.append(result)
        
        if len(analyses) == 0:
            return None
        
        # Compile statistics
        summary = {
            'timeframe': timeframe_name,
            'total_crossovers': len(analyses),
            'touched_sma_count': sum(1 for a in analyses if a['touched_sma_again']),
            'bounced_count': sum(1 for a in analyses if a['bounced']),
            'avg_bounce_points': np.mean([a['bounce_points'] for a in analyses if a['bounced']]) if any(a['bounced'] for a in analyses) else 0,
            'avg_points_captured': np.mean([a['points_captured'] for a in analyses]),
            'max_points_captured': max([a['points_captured'] for a in analyses]),
            'min_points_captured': min([a['points_captured'] for a in analyses]),
            'winning_trades': sum(1 for a in analyses if a['profitable']),
            'losing_trades': sum(1 for a in analyses if not a['profitable']),
            'winning_rate': (sum(1 for a in analyses if a['profitable']) / len(analyses)) * 100,
            'avg_max_gain': np.mean([a['max_gain'] for a in analyses]),
            'avg_max_gain_points': np.mean([a['max_gain_points'] for a in analyses]),
            'avg_max_drawdown': np.mean([a['max_drawdown'] for a in analyses]),
            'avg_max_drawdown_points': np.mean([a['max_drawdown_points'] for a in analyses]),
            'avg_suggested_stoploss': np.mean([a['suggested_stoploss_pct'] for a in analyses]),
            'avg_days_to_recovery': np.mean([a['days_to_recovery'] for a in analyses if a['days_to_recovery'] is not None]) if any(a['days_to_recovery'] is not None for a in analyses) else None,
            'went_down_then_up_count': sum(1 for a in analyses if a['went_down_then_up']),
            'went_up_continuously_count': sum(1 for a in analyses if a['went_up_continuously']),
            'data_points': len(df),
            'period_start': df.index[0],
            'period_end': df.index[-1]
        }
        
        return summary
    
    def run_full_analysis(self):
        """
        Run analysis for all timeframes
        
        Returns:
            DataFrame with summary for all timeframes
        """
        timeframes = [
            ('1d', 'Daily'),
            ('1wk', 'Weekly'),
            ('1mo', 'Monthly'),
        ]
        
        # Note: 4-hour data is limited to ~730 days on Yahoo Finance
        # We'll try to include it but note the limitation
        try:
            four_hour_data = self.fetch_data('1h')  # Use 1h as proxy
            if four_hour_data is not None and len(four_hour_data) > 0:
                # Resample to 4-hour
                four_hour_data = four_hour_data.resample('4H').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                if len(four_hour_data) >= self.sma_period:
                    timeframes.insert(0, ('4h_resampled', '4-Hour'))
        except:
            print("4-hour data not available, skipping...")
        
        results = []
        for interval, name in timeframes:
            if interval == '4h_resampled':
                # Special handling for resampled 4-hour data
                df = self.calculate_sma(four_hour_data)
                if df is not None:
                    crossovers = self.identify_crossovers(df)
                    if len(crossovers) > 0:
                        analyses = []
                        for idx in crossovers:
                            result = self.analyze_crossover(df, idx)
                            if result is not None:
                                analyses.append(result)
                        
                        if len(analyses) > 0:
                            summary = {
                                'timeframe': name,
                                'total_crossovers': len(analyses),
                                'touched_sma_count': sum(1 for a in analyses if a['touched_sma_again']),
                                'bounced_count': sum(1 for a in analyses if a['bounced']),
                                'avg_bounce_points': np.mean([a['bounce_points'] for a in analyses if a['bounced']]) if any(a['bounced'] for a in analyses) else 0,
                                'avg_points_captured': np.mean([a['points_captured'] for a in analyses]),
                                'max_points_captured': max([a['points_captured'] for a in analyses]),
                                'min_points_captured': min([a['points_captured'] for a in analyses]),
                                'winning_trades': sum(1 for a in analyses if a['profitable']),
                                'losing_trades': sum(1 for a in analyses if not a['profitable']),
                                'winning_rate': (sum(1 for a in analyses if a['profitable']) / len(analyses)) * 100,
                                'avg_max_gain': np.mean([a['max_gain'] for a in analyses]),
                                'avg_max_gain_points': np.mean([a['max_gain_points'] for a in analyses]),
                                'avg_max_drawdown': np.mean([a['max_drawdown'] for a in analyses]),
                                'avg_max_drawdown_points': np.mean([a['max_drawdown_points'] for a in analyses]),
                                'avg_suggested_stoploss': np.mean([a['suggested_stoploss_pct'] for a in analyses]),
                                'avg_days_to_recovery': np.mean([a['days_to_recovery'] for a in analyses if a['days_to_recovery'] is not None]) if any(a['days_to_recovery'] is not None for a in analyses) else None,
                                'went_down_then_up_count': sum(1 for a in analyses if a['went_down_then_up']),
                                'went_up_continuously_count': sum(1 for a in analyses if a['went_up_continuously']),
                                'data_points': len(df),
                                'period_start': df.index[0],
                                'period_end': df.index[-1]
                            }
                            results.append(summary)
            else:
                summary = self.analyze_timeframe(interval, name)
                if summary is not None:
                    results.append(summary)
        
        if len(results) == 0:
            return None
        
        return pd.DataFrame(results)


def format_analysis_table(df):
    """
    Format the analysis results into a readable table
    
    Args:
        df: DataFrame with analysis results
    
    Returns:
        Formatted DataFrame
    """
    if df is None or len(df) == 0:
        return None
    
    # Create a formatted version
    formatted = pd.DataFrame()
    formatted['Timeframe'] = df['timeframe']
    formatted['Total Crossovers'] = df['total_crossovers']
    formatted['Touched SMA Again'] = df['touched_sma_count']
    formatted['Bounced Count'] = df['bounced_count']
    formatted['Avg Bounce Points'] = df['avg_bounce_points'].round(2)
    formatted['Avg Points Captured'] = df['avg_points_captured'].round(2)
    formatted['Max Points Captured'] = df['max_points_captured'].round(2)
    formatted['Min Points Captured'] = df['min_points_captured'].round(2)
    formatted['Winning Trades'] = df['winning_trades']
    formatted['Losing Trades'] = df['losing_trades']
    formatted['Winning Rate (%)'] = df['winning_rate'].round(2)
    formatted['Avg Max Gain (%)'] = df['avg_max_gain'].round(2)
    formatted['Avg Max Gain Points'] = df['avg_max_gain_points'].round(2)
    formatted['Avg Max Drawdown (%)'] = df['avg_max_drawdown'].round(2)
    formatted['Avg Max Drawdown Points'] = df['avg_max_drawdown_points'].round(2)
    formatted['Suggested Stop Loss (%)'] = df['avg_suggested_stoploss'].round(2)
    formatted['Avg Days to Recovery'] = df['avg_days_to_recovery'].round(2)
    formatted['Went Down Then Up'] = df['went_down_then_up_count']
    formatted['Went Up Continuously'] = df['went_up_continuously_count']
    formatted['Data Period'] = df.apply(lambda row: f"{row['period_start'].strftime('%Y-%m-%d')} to {row['period_end'].strftime('%Y-%m-%d')}", axis=1)
    
    return formatted
