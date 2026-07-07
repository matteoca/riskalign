# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict, Any, List

def download_portfolio_data(tickers: List[str], start_date: str, end_date: str) -> tuple[pd.DataFrame, List[str]]:
    """
    Downloads historical close prices for a list of tickers from Yahoo Finance.
    Automatically handles the new yfinance structure where 'Close' represents adjusted prices.
    Tickers with no valid price data are dropped and reported.
    
    :param tickers: List of asset ticker symbols (e.g., ['AAPL', 'BTC-USD'])
    :param start_date: Start date string (YYYY-MM-DD)
    :param end_date: End date string (YYYY-MM-DD)
    :return: Tuple of (cleaned DataFrame with valid tickers as columns, list of dropped ticker symbols)
    """
    if not tickers:
        raise ValueError("The list of tickers cannot be empty.")
        
    try:
        print(f"Downloading historical data for tickers: {tickers}...")
        raw_data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        
        if raw_data.empty:
            raise ValueError("No data returned from Yahoo Finance for the specified tickers and date range.")
            
        # Extract 'Close' prices (automatically adjusted in recent yfinance versions)
        portfolio_data = raw_data['Close']
        
        # If only one ticker is requested, yfinance returns a Series. Convert it back to a DataFrame.
        if isinstance(portfolio_data, pd.Series):
            portfolio_data = portfolio_data.to_frame(name=tickers[0])
            
        # Handle missing data across different asset classes (e.g., weekends for Crypto vs Equity)
        # Forward-fill missing prices (hold last known price), then backward-fill any remaining NaNs at the start
        cleaned_data = portfolio_data.ffill().bfill()

        # Drop tickers that are still entirely NaN after filling (no valid data from Yahoo Finance)
        null_tickers = [col for col in cleaned_data.columns if cleaned_data[col].isna().all()]
        if null_tickers:
            print(f"Warning: Tickers {null_tickers} returned no valid price data and will be excluded from the analysis.")
            cleaned_data = cleaned_data.drop(columns=null_tickers)

        if cleaned_data.empty:
            raise ValueError("All tickers were dropped due to missing data. Cannot proceed with analysis.")

        return cleaned_data, null_tickers
        
    except Exception as e:
        raise RuntimeError(f"Failed to download or process market data: {e}")

def calculate_log_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates daily logarithmic returns for the given price history DataFrame.
    Formula: R_t = ln(P_t / P_{t-1})
    """
    log_returns = np.log(prices_df / prices_df.shift(1)).dropna()
    return log_returns

def compute_portfolio_volatility(log_returns: pd.DataFrame, weight_dict: Dict[str, float]) -> Dict[str, float]:
    """
    Computes annualized individual volatilities, naive portfolio volatility,
    actual portfolio volatility (using covariance matrix), and the diversification benefit.
    
    :param log_returns: DataFrame of daily log returns
    :param weight_dict: Dictionary mapping tickers to their percentage weights (0.0 to 1.0)
    :return: Dictionary containing key risk metrics
    """
    # Align weights array exactly with the column order of the log_returns DataFrame
    columns = log_returns.columns
    weights = np.array([weight_dict[col] for col in columns])
    
    # Calculate individual annualized volatilities (assuming 252 trading days)
    individual_annual_vols = log_returns.std() * np.sqrt(252)
    
    # Calculate Naive Volatility (weighted sum of individual risks)
    naive_volatility = np.sum(weights * individual_annual_vols.values)
    
    # Calculate Actual Volatility using matrix algebra: W^T * Sigma * W
    cov_matrix_daily = log_returns.cov()
    cov_matrix_annual = cov_matrix_daily * 252
    portfolio_variance = np.dot(weights.T, np.dot(cov_matrix_annual, weights))
    actual_volatility = np.sqrt(portfolio_variance)
    
    # Calculate the diversification benefit
    diversification_benefit = naive_volatility - actual_volatility
    
    return {
        "actual_volatility": actual_volatility,
        "naive_volatility": naive_volatility,
        "diversification_benefit": diversification_benefit,
        "individual_volatilities": individual_annual_vols.to_dict()
    }

def compute_value_at_risk(actual_volatility: float, portfolio_value: float, 
                           confidence_level: float = 0.95, time_horizon_days: int = 21) -> Dict[str, float]:
    """
    Calculates the Parametric Value at Risk (VaR) for a given portfolio value and time horizon.
    
    :param actual_volatility: Annualized actual portfolio volatility
    :param portfolio_value: Total value of the portfolio in nominal currency (e.g., Euros)
    :param confidence_level: Confidence level (default 95%)
    :param time_horizon_days: Time horizon in trading days (default 21 days = 1 month)
    :return: Dictionary with percentage and absolute VaR values
    """
    # Convert annualized volatility back to daily volatility
    daily_volatility = actual_volatility / np.sqrt(252)
    
    # Calculate the Z-score for the given confidence level (one-tailed)
    z_score = np.abs(norm.ppf(1 - confidence_level))
    
    # Scale daily volatility to the time horizon using the square root of time
    var_percentage = z_score * daily_volatility * np.sqrt(time_horizon_days)
    var_absolute = portfolio_value * var_percentage
    
    return {
        "var_percentage": var_percentage,
        "var_absolute": var_absolute,
        "confidence_level": confidence_level,
        "horizon_days": time_horizon_days
    }

def run_quantitative_analysis(weight_dict: Dict[str, float], portfolio_value: float, 
                              start_date: str, end_date: str,
                              prices_df: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Orchestrator function that executes the full quantitative pipeline.
    If prices_df is provided, skips the download step (used for caching).
    """
    tickers = list(weight_dict.keys())
    
    # 1. Download data (or use cached), collecting any tickers dropped due to missing data
    if prices_df is None:
        prices_df, dropped_tickers = download_portfolio_data(tickers, start_date, end_date)
    else:
        # Detect dropped tickers from pre-fetched data
        null_tickers = [col for col in prices_df.columns if prices_df[col].isna().all()]
        prices_df = prices_df.drop(columns=null_tickers)
        dropped_tickers = null_tickers

    # 2. Rebuild weight_dict excluding dropped tickers and renormalize to sum to 1.0
    active_weights = {t: w for t, w in weight_dict.items() if t not in dropped_tickers}
    total_weight = sum(active_weights.values())
    active_weights = {t: w / total_weight for t, w in active_weights.items()}

    # 3. Run the rest of the pipeline with the cleaned data
    log_returns = calculate_log_returns(prices_df)
    risk_metrics = compute_portfolio_volatility(log_returns, active_weights)
    var_metrics = compute_value_at_risk(risk_metrics["actual_volatility"], portfolio_value)
    
    # 4. Package all outputs, including alerts for dropped tickers
    return {
        "volatility_analysis": risk_metrics,
        "var_analysis": var_metrics,
        "dropped_tickers": dropped_tickers
    }

if __name__ == "__main__":
    # Sanity Check Block to test the engine standalone
    mock_portfolio = {
        "AAPL": 0.40,
        "MSFT": 0.30,
        "IE00B4L5Y983": 0.20,
        "BTC-USD": 0.10
    }
    mock_value = 100000.0
    
    results = run_quantitative_analysis(
        weight_dict=mock_portfolio, 
        portfolio_value=mock_value,
        start_date="2021-01-01", 
        end_date="2026-01-01"
    )
    
    print("\n--- QUANTITATIVE ENGINE SANITY CHECK SUCCESSFUL ---")
    v_analysis = results["volatility_analysis"]
    var_analysis = results["var_analysis"]
    
    print(f"Actual Portfolio Volatility: {v_analysis['actual_volatility']*100:.2f}%")
    print(f"Diversification Benefit:     {v_analysis['diversification_benefit']*100:.2f}%")
    print(f"Monthly 95% VaR (Nominal):   €{var_analysis['var_absolute']:,.2f}")