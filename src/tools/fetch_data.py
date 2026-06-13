import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_data(ticker: str, period: str = "1y") -> str:
    """
    Fetches OHLCV data for a given ticker.
    
    Args:
        ticker: Stock symbol e.g. 'AAPL', '^NSEI' for Nifty 50
        period: Time period e.g. '1y', '2y', '5y', '6mo'
    
    Returns:
        String summary of the data for the LLM to read
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return f"No data found for ticker {ticker}"
        
        # compute basic stats
        df['Returns'] = df['Close'].pct_change()
        df['Cumulative_Return'] = (1 + df['Returns']).cumprod() - 1
        
        summary = f"""
Data fetched for {ticker} over {period}:
- Start date: {df.index[0].strftime('%Y-%m-%d')}
- End date: {df.index[-1].strftime('%Y-%m-%d')}
- Total trading days: {len(df)}
- Starting price: ${df['Close'].iloc[0]:.2f}
- Ending price: ${df['Close'].iloc[-1]:.2f}
- Cumulative return: {df['Cumulative_Return'].iloc[-1]*100:.2f}%
- Average daily return: {df['Returns'].mean()*100:.4f}%
- Daily return std dev: {df['Returns'].std()*100:.4f}%
- Max single day gain: {df['Returns'].max()*100:.2f}%
- Max single day loss: {df['Returns'].min()*100:.2f}%
- Average daily volume: {df['Volume'].mean():,.0f}

Recent 5 days:
{df[['Close', 'Returns', 'Volume']].tail(5).to_string()}
        """
        return summary.strip()
    
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"