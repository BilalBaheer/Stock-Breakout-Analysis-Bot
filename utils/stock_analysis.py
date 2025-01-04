import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_stock_breakout(ticker, start_date, end_date, volume_threshold, price_threshold, holding_period):
    """
    Analyze stock breakouts based on volume and price thresholds.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (str): Start date for analysis (YYYY-MM-DD)
        end_date (str): End date for analysis (YYYY-MM-DD)
        volume_threshold (float): Volume threshold percentage (e.g., 200 for 200%)
        price_threshold (float): Price change threshold percentage
        holding_period (int): Number of days to hold the position
    
    Returns:
        pd.DataFrame: Analysis results
    """
    try:
        # Parse input dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Add buffer days for moving average calculation
        buffer_days = 30
        analysis_start = start_dt - timedelta(days=buffer_days)
        
        print(f"Fetching data for {ticker} from {analysis_start} to {end_dt}")
        
        try:
            # Create a Ticker object and fetch data
            stock = yf.Ticker(ticker)
            stock_data = stock.history(
                start=analysis_start.strftime('%Y-%m-%d'),
                end=end_dt.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            print(f"\nData retrieved:")
            print(f"Shape: {stock_data.shape}")
            
            if not stock_data.empty:
                print(f"Date range: {stock_data.index.min()} to {stock_data.index.max()}")
                print(f"Number of trading days: {len(stock_data)}")
            else:
                print("No data was retrieved")
                return None
                
        except Exception as e:
            print(f"Error downloading data: {str(e)}")
            return None
        
        if stock_data.empty:
            print(f"No data found for {ticker} between {analysis_start} and {end_dt}")
            return None
            
        print(f"\nProcessing {len(stock_data)} days of data...")
        
        if len(stock_data) < 20:  # Need at least 20 days for moving average
            print(f"Insufficient data: only {len(stock_data)} days available, need at least 20 days")
            return None

        # Calculate 20-day average volume
        stock_data['Volume_20MA'] = stock_data['Volume'].rolling(window=20).mean()
        print(f"Calculated 20-day moving average. First few values:\n{stock_data['Volume_20MA'].head()}")
        
        # Calculate daily returns
        stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
        print(f"Calculated daily returns. First few values:\n{stock_data['Daily_Return'].head()}")
        
        # Calculate volume ratio
        stock_data['Volume_Ratio'] = (stock_data['Volume'] / stock_data['Volume_20MA']) * 100
        
        # Find breakout days
        breakout_days = stock_data[
            (stock_data['Volume_Ratio'] > volume_threshold) &
            (stock_data['Daily_Return'] > price_threshold)
        ]
        
        # Calculate forward returns
        results = []
        for date in breakout_days.index:
            entry_price = stock_data.loc[date, 'Close']
            
            # Get the price after holding period
            future_date = date + timedelta(days=holding_period)
            future_data = stock_data[stock_data.index > date][:holding_period]
            
            if not future_data.empty:
                exit_price = future_data['Close'].iloc[-1]
                return_pct = ((exit_price - entry_price) / entry_price) * 100
                
                results.append({
                    'Entry_Date': date.strftime('%Y-%m-%d'),
                    'Volume_Ratio': stock_data.loc[date, 'Volume_Ratio'],
                    'Daily_Return': stock_data.loc[date, 'Daily_Return'],
                    'Entry_Price': entry_price,
                    'Exit_Date': future_data.index[-1].strftime('%Y-%m-%d'),
                    'Exit_Price': exit_price,
                    'Return_Percent': return_pct
                })
        
        if not results:
            return pd.DataFrame()
            
        results_df = pd.DataFrame(results)
        
        # Add summary statistics
        summary_stats = {
            'Total_Trades': len(results),
            'Average_Return': results_df['Return_Percent'].mean(),
            'Win_Rate': (results_df['Return_Percent'] > 0).mean() * 100,
            'Best_Trade': results_df['Return_Percent'].max(),
            'Worst_Trade': results_df['Return_Percent'].min()
        }
        
        return results_df
        
    except Exception as e:
        print(f"Error in analyze_stock_breakout: {str(e)}")
        return None
