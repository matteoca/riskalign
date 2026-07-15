# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import pytest
from src.matching_engine import calculate_continuous_sri, evaluate_delta_status, run_matching_logic

# ==========================================
# TESTING CONTINUOUS SRI MATH
# ==========================================
def test_calculate_continuous_sri_midpoint():
    """Test that a volatility exactly in the middle of SRI 4 (12% to 20%) returns 4.5"""
    volatility = 0.16
    sri = calculate_continuous_sri(volatility)
    assert sri == 4.5

def test_calculate_continuous_sri_extremes():
    """Test extreme boundaries and capping logic"""
    assert calculate_continuous_sri(0.002) >= 1.0  # Very low vol
    assert calculate_continuous_sri(0.950) == 7.0  # Extremely high vol (capped)

# ==========================================
# TESTING DELTA THRESHOLDS
# ==========================================
def test_evaluate_delta_status():
    """Test the traffic light assignment based on mathematical deltas"""
    assert evaluate_delta_status(-2.0)[0] == "BLUE"
    assert evaluate_delta_status(-1.0)[0] == "GRAY"
    assert evaluate_delta_status(0.0)[0] == "GREEN"
    assert evaluate_delta_status(1.0)[0] == "YELLOW"
    assert evaluate_delta_status(2.0)[0] == "RED"

# ==========================================
# TESTING EMERGENCY BRAKE (VAR OVERRIDE)
# ==========================================
def test_var_emergency_brake_triggered():
    """Test that the Red light is forced if VaR exceeds user loss capacity"""
    # User is SRI 4, Portfolio is SRI 4 (Delta 0 = GREEN expected)
    # BUT VaR is 8% and user chose "a1" (zero loss tolerance, max 5%)
    result = run_matching_logic(
        user_sri=4.0, 
        portfolio_volatility=0.16, 
        var_percentage=0.08, 
        loss_capacity_answer="a1"
    )
    
    assert result["delta"] == 0.5
    assert result["status_color"] == "RED"
    assert result["emergency_brake_active"] is True
    assert "tolleranza dichiarata di zero perdite" in result["emergency_brake_reason"]

def test_var_emergency_brake_cleared():
    """Test that the Emergency Brake does not trigger for high-tolerance users"""
    # Same portfolio, but user answered "a3" (High tolerance)
    result = run_matching_logic(
        user_sri=4.0, 
        portfolio_volatility=0.16, 
        var_percentage=0.08, 
        loss_capacity_answer="a3"
    )
    
    assert result["status_color"] == "GREEN"  # Normal delta mapping applies
    assert result["emergency_brake_active"] is False