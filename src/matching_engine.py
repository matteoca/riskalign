# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

from typing import Dict, Any, Tuple

# PRIIPs ESMA Volatility thresholds for SRI classes
# Format: (Min Volatility, Max Volatility)
ESMA_THRESHOLDS = {
    1: (0.000, 0.005),
    2: (0.005, 0.050),
    3: (0.050, 0.120),
    4: (0.120, 0.200),
    5: (0.200, 0.300),
    6: (0.300, 0.800),
    7: (0.800, 9.999) # Capped at a theoretical extreme
}

def calculate_continuous_sri(volatility: float) -> float:
    """
    Converts annualized portfolio volatility into a continuous SRI score (1.0 to 7.0)
    using linear interpolation within the ESMA PRIIPs brackets.
    """
    for sri_level, (vol_min, vol_max) in ESMA_THRESHOLDS.items():
        if vol_min <= volatility <= vol_max:
            if sri_level == 7:
                return 7.0 # Max out at 7.0
            
            # Linear interpolation formula
            fraction = (volatility - vol_min) / (vol_max - vol_min)
            return float(sri_level + fraction)
            
    # Fallback for extreme negative or zero inputs
    return 1.0

def evaluate_delta_status(delta: float) -> Tuple[str, str]:
    """
    Evaluates the risk mismatch (Delta) and assigns a status color and label.
    """
    if delta <= -1.5:
        return "BLUE", "Severe Under-exposure (Inefficient)"
    elif -1.5 < delta <= -0.5:
        return "GRAY", "Mild Under-exposure"
    elif -0.5 < delta <= 0.5:
        return "GREEN", "Perfectly Aligned"
    elif 0.5 < delta <= 1.5:
        return "YELLOW", "Mild Over-exposure (Warning)"
    else:
        return "RED", "Critical Over-exposure (Danger)"

def run_matching_logic(user_sri: float, portfolio_volatility: float, 
                       var_percentage: float, loss_capacity_answer: str) -> Dict[str, Any]:
    """
    Compares the user's MiFID profile with the portfolio's actual quantitative risk.
    Applies the Delta logic and the VaR Emergency Brake.
    
    :param user_sri: The final SRI calculated from the MiFID engine (1 to 7)
    :param portfolio_volatility: The actual annualized volatility (e.g., 0.185 for 18.5%)
    :param var_percentage: The absolute percentage of VaR (e.g., 0.06 for 6%)
    :param loss_capacity_answer: The specific answer ID given by the user regarding loss tolerance
    :return: Dictionary containing the final matching report
    """
    # 1. Convert volatility to Continuous SRI
    portfolio_sri = calculate_continuous_sri(portfolio_volatility)
    
    # 2. Calculate the mismatch (Delta)
    delta = portfolio_sri - user_sri
    
    # 3. Determine base status from Delta
    color, label = evaluate_delta_status(delta)
    
    # 4. VaR Emergency Brake (Override Logic)
    override_triggered = False
    override_reason = ""
    
    # Mapping assumed from questionnaire YAML:
    # "a1" = Cannot bear losses (Max tolerance ~5%)
    # "a2" = Can bear moderate/temporary losses (Max tolerance ~15%)
    # "a3" = Can bear significant losses
    if loss_capacity_answer == "a1" and var_percentage > 0.05:
        color = "RED"
        label = "Critical Over-exposure (VaR Override)"
        override_triggered = True
        override_reason = f"Portfolio 1-Month VaR is {var_percentage*100:.1f}%, exceeding your absolute zero-loss tolerance."
        
    elif loss_capacity_answer == "a2" and var_percentage > 0.15:
        color = "RED"
        label = "Critical Over-exposure (VaR Override)"
        override_triggered = True
        override_reason = f"Portfolio 1-Month VaR is {var_percentage*100:.1f}%, exceeding your moderate loss tolerance."

    # 5. Build and return the final report
    return {
        "user_sri": round(user_sri, 2),
        "portfolio_continuous_sri": round(portfolio_sri, 2),
        "delta": round(delta, 2),
        "status_color": color,
        "status_label": label,
        "emergency_brake_active": override_triggered,
        "emergency_brake_reason": override_reason
    }

if __name__ == "__main__":
    # --- SANITY CHECK ---
    print("====== MATCHING ENGINE TEST ======")
    
    # Scenario: Moderate user (SRI 3), but portfolio is very risky (Volatility 26%)
    mock_user_sri = 3.0
    mock_port_vol = 0.26 # 26% volatility -> falls in bucket 5 (20%-30%) -> expected SRI ~ 5.6
    mock_var = 0.08      # 8% monthly VaR
    mock_loss_cap = "a1" # User cannot bear losses
    
    result = run_matching_logic(mock_user_sri, mock_port_vol, mock_var, mock_loss_cap)
    
    print(f"User Profile (MiFID):    {result['user_sri']}")
    print(f"Portfolio Profile (SRI): {result['portfolio_continuous_sri']}")
    print(f"Mismatch Delta:          {result['delta']:+}")
    print(f"Final Status:            {result['status_color']} - {result['status_label']}")
    
    if result['emergency_brake_active']:
        print(f"OVERRIDE TRIGGERED:      {result['emergency_brake_reason']}")