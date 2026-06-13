import numpy as np
from scipy import stats
import yfinance as yf

def compute_stats(ticker: str, period: str = "1y", hypothesis: str = "momentum") -> str:
    """
    Runs statistical tests on financial data.
    
    Args:
        ticker: Stock symbol e.g. '^NSEI'
        period: Time period e.g. '1y', '2y'
        hypothesis: Type of test - 'momentum', 'mean_reversion', 'normality'
    
    Returns:
        String with statistical test results
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return f"No data found for {ticker}"
        
        returns = df['Close'].pct_change().dropna().values
        
        if hypothesis == "momentum":
            # test if past winners keep winning
            # split into first and second half
            mid = len(returns) // 2
            first_half = returns[:mid]
            second_half = returns[mid:]
            
            # correlation between consecutive returns (autocorrelation)
            autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
            
            # t-test: is mean return significantly positive?
            t_stat, p_value = stats.ttest_1samp(returns, 0)
            
            # momentum: does first half performance predict second half?
            min_len = min(len(first_half), len(second_half))
            corr, corr_p = stats.pearsonr(first_half[:min_len], second_half[:min_len])
            
            result = f"""
Momentum Analysis for {ticker} over {period}:

1. Return Autocorrelation: {autocorr:.4f}
   → {'Positive autocorrelation suggests momentum effect' if autocorr > 0 else 'Negative autocorrelation suggests mean reversion'}

2. T-test (mean return vs zero):
   - T-statistic: {t_stat:.4f}
   - P-value: {p_value:.4f}
   - Mean daily return: {returns.mean()*100:.4f}%
   → {'Statistically significant positive returns' if p_value < 0.05 and returns.mean() > 0 else 'Returns not statistically different from zero' if p_value >= 0.05 else 'Statistically significant negative returns'}

3. Half-period correlation (momentum persistence):
   - Correlation: {corr:.4f}
   - P-value: {corr_p:.4f}
   → {'Strong momentum signal' if corr > 0.3 and corr_p < 0.05 else 'Weak or no momentum signal'}

Conclusion: {'Momentum effect present' if autocorr > 0 and p_value < 0.05 else 'Momentum effect not confirmed'}
            """

        elif hypothesis == "mean_reversion":
            # augmented dickey-fuller style test using autocorrelation
            autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
            
            # test if returns revert to mean
            t_stat, p_value = stats.ttest_1samp(returns, returns.mean())
            
            result = f"""
Mean Reversion Analysis for {ticker} over {period}:

1. Return Autocorrelation: {autocorr:.4f}
   → {'Negative autocorrelation supports mean reversion' if autocorr < 0 else 'Positive autocorrelation, mean reversion less likely'}

2. Mean return: {returns.mean()*100:.4f}%
3. Std deviation: {returns.std()*100:.4f}%

Conclusion: {'Mean reversion signal present' if autocorr < -0.05 else 'Mean reversion not strongly supported'}
            """

        elif hypothesis == "normality":
            # shapiro-wilk test for normality
            stat, p_value = stats.shapiro(returns[:500])  # shapiro works best under 5000 samples
            skewness = stats.skew(returns)
            kurtosis = stats.kurtosis(returns)
            
            result = f"""
Normality Analysis for {ticker} over {period}:

1. Shapiro-Wilk Test:
   - Statistic: {stat:.4f}
   - P-value: {p_value:.4f}
   → {'Returns are normally distributed' if p_value > 0.05 else 'Returns are NOT normally distributed (fat tails present)'}

2. Skewness: {skewness:.4f}
   → {'Left skewed (more negative extremes)' if skewness < 0 else 'Right skewed (more positive extremes)'}

3. Excess Kurtosis: {kurtosis:.4f}
   → {'Fat tails present (leptokurtic)' if kurtosis > 0 else 'Thin tails (platykurtic)'}

Conclusion: {'Normal distribution assumed safe' if p_value > 0.05 else 'Fat tails confirmed — normal distribution assumption violated'}
            """
        
        else:
            result = f"Unknown hypothesis type: {hypothesis}. Use 'momentum', 'mean_reversion', or 'normality'."
        
        return result.strip()
    
    except Exception as e:
        return f"Error computing stats: {str(e)}"