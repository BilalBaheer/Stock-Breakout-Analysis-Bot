import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# Create a Ticker object
aapl = yf.Ticker("AAPL")

# Test different date ranges
test_ranges = [
    ('2023-01-01', '2023-12-31', 'Full Year 2023'),
    ('2023-12-01', '2023-12-31', 'December 2023'),
    ('2023-11-01', '2023-12-31', 'Last 2 months of 2023')
]

print("Ticker Info:")
print(aapl.info.get('regularMarketPrice'))
print("\nTesting history() method:")

for start_date, end_date, description in test_ranges:
    print(f"\nTesting {description}")
    print(f"Date range: {start_date} to {end_date}")
    
    try:
        # Try using the history method instead
        data = aapl.history(
            start=start_date,
            end=end_date,
            interval='1d'
        )
        
        if not data.empty:
            print(f"Success! Retrieved {len(data)} days of data")
            print(f"Date range in data: {data.index.min()} to {data.index.max()}")
            print(f"Columns: {data.columns.tolist()}")
            print("\nFirst few rows:")
            print(data.head(3))
        else:
            print("No data retrieved")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("-" * 80)

# Test different tickers
test_tickers = ['NVDA', 'TSLA', 'META', 'MSFT']
start_date = '2023-01-01'
end_date = '2023-12-31'

print("Testing multiple tickers for breakout patterns...")
print("-" * 80)

for ticker in test_tickers:
    print(f"\nAnalyzing {ticker}")
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    
    if not data.empty:
        # Calculate basic statistics
        avg_volume = data['Volume'].mean()
        avg_daily_change = abs(data['Close'].pct_change()).mean() * 100
        volatility = data['Close'].pct_change().std() * 100
        
        print(f"Average Daily Volume: {avg_volume:,.0f}")
        print(f"Average Daily Change: {avg_daily_change:.2f}%")
        print(f"Volatility: {volatility:.2f}%")
        
        # Find significant volume spikes
        volume_ma = data['Volume'].rolling(window=20).mean()
        volume_spikes = data[data['Volume'] > volume_ma * 2]
        
        print(f"Number of 2x volume spikes: {len(volume_spikes)}")
        
        if len(volume_spikes) > 0:
            print("\nTop 3 volume spike days:")
            volume_ratio = data['Volume'] / volume_ma
            top_spikes = volume_ratio.nlargest(3)
            for date, ratio in top_spikes.items():
                price_change = data.loc[date, 'Close'] / data.loc[date, 'Open'] - 1
                print(f"Date: {date.strftime('%Y-%m-%d')}, Volume Ratio: {ratio:.2f}x, Price Change: {price_change:.2f}%")
    
    print("-" * 80)
