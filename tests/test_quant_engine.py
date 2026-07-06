# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import pytest
import pandas as pd
import numpy as np
from src.quant_engine import compute_portfolio_volatility, compute_value_at_risk

# ==========================================
# FIXTURES (Test Data Setup)
# ==========================================
@pytest.fixture
def dummy_log_returns():
    """Creates a deterministic dummy DataFrame of log returns for testing math"""
    np.random.seed(42) # Ensure reproducible randomness
    dates = pd.date_range("2023-01-01", periods=100, freq="B")
    
    # Simulate low risk asset (A) and high risk asset (B)
    data = {
        "ASSET_A": np.random.normal(0.0001, 0.01, 100),
        "ASSET_B": np.random.normal(0.0005, 0.03, 100)
    }
    return pd.DataFrame(data, index=dates)

# ==========================================
# TESTING QUANTITATIVE MATH
# ==========================================
def test_compute_portfolio_volatility(dummy_log_returns):
    """Test that actual volatility accounts for diversification (should be < naive)"""
    weights = {"ASSET_A": 0.5, "ASSET_B": 0.5}
    
    result = compute_portfolio_volatility(dummy_log_returns, weights)
    
    assert "actual_volatility" in result
    assert "naive_volatility" in result
    assert result["diversification_benefit"] > 0.0 # Diversification MUST reduce risk
    assert result["actual_volatility"] < result["naive_volatility"]

def test_compute_value_at_risk():
    """Test the Parametric VaR calculation with known inputs"""
    actual_volatility = 0.20 # 20% annualized
    portfolio_value = 10000.0 # 10k Euros
    
    result = compute_value_at_risk(
        actual_volatility=actual_volatility, 
        portfolio_value=portfolio_value, 
        confidence_level=0.95, 
        time_horizon_days=21
    )
    
    # 20% annualized -> ~1.26% daily -> * 1.645 (Z) * sqrt(21) -> ~9.5% monthly VaR
    # 9.5% of 10,000 is approx 950
    assert result["var_percentage"] > 0.09
    assert result["var_percentage"] < 0.10
    assert result["var_absolute"] > 900
    assert result["var_absolute"] < 1000