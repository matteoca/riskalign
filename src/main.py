# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import os
from datetime import date, timedelta
from typing import Dict, Any

import pandas as pd

# Import the specialized engines
from src.mifid_engine import calculate_mifid_profile
from src.quant_engine import run_quantitative_analysis
from src.matching_engine import run_matching_logic

def generate_full_risk_report(
    user_answers: Dict[str, str], 
    portfolio_weights: Dict[str, float], 
    portfolio_value: float, 
    yaml_config_path: str = "config/questionnaire.yaml",
    prices_df: pd.DataFrame = None
) -> Dict[str, Any]:
    """
    Master orchestrator function. Executes the MiFID profiling, quantitative risk 
    assessment, and the final matching logic to generate a comprehensive risk report.
    
    :param user_answers: Dictionary of user responses from the UI
    :param portfolio_weights: Dictionary of asset tickers and their weights
    :param portfolio_value: Total nominal value of the portfolio
    :param yaml_config_path: Path to the questionnaire configuration
    :return: A complete dictionary containing all analysis phases
    """
    print("Starting RiskAlign Engine Pipeline...")
    
    # ---------------------------------------------------------
    # PHASE 1: MiFID Qualitative Profiling
    # ---------------------------------------------------------
    print(" -> Running MiFID Engine...")
    mifid_results = calculate_mifid_profile(user_answers, yaml_config_path)
    user_sri = mifid_results['user_sri_profile']
    
    # Extract the specific answer for loss capacity to feed the Emergency Brake
    # Assuming the question ID in YAML is 'q_fin_loss_capacity'
    loss_capacity_answer = user_answers.get('q_fin_loss_capacity', 'a3') # Default to a3 (highest tolerance) if missing
    
    # ---------------------------------------------------------
    # PHASE 2: Quantitative Portfolio Analysis
    # ---------------------------------------------------------
    print(" -> Running Quantitative Engine (yfinance data fetch & matrix math)...")
    end_date = date.today()
    start_date = end_date - timedelta(days=5 * 365)
    quant_results = run_quantitative_analysis(
        weight_dict=portfolio_weights,
        portfolio_value=portfolio_value,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        prices_df=prices_df
    )
    
    actual_volatility = quant_results['volatility_analysis']['actual_volatility']
    var_percentage = quant_results['var_analysis']['var_percentage']
    
    # ---------------------------------------------------------
    # PHASE 3: Matching & Delta Assessment
    # ---------------------------------------------------------
    print(" -> Running Matching Engine...")
    matching_results = run_matching_logic(
        user_sri=user_sri,
        portfolio_volatility=actual_volatility,
        var_percentage=var_percentage,
        loss_capacity_answer=loss_capacity_answer
    )
    
    # ---------------------------------------------------------
    # FINAL OUTPUT PACKAGING
    # ---------------------------------------------------------
    print("Pipeline Execution Complete.\n")
    return {
        "mifid_profile": mifid_results,
        "quant_metrics": quant_results,
        "final_assessment": matching_results
    }

if __name__ == "__main__":
    # Ensure the script can find the config file regardless of where it's run from
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    config_path = os.path.join(project_root, 'config', 'questionnaire.yaml')
    
    # SIMULATION: A user with low loss tolerance but an aggressive portfolio
    mock_answers = {
        "q_exp_education": "a2",
        "q_exp_frequency": "a2",
        "q_exp_derivatives": "a1",
        "q_fin_income_stability": "a2",
        "q_fin_loss_capacity": "a1",  # Critical: Cannot bear losses
        "q_fin_wealth_pct": "a2",
        "q_fin_liquidity_need": "a2",
        "q_obj_horizon": "a3",
        "q_obj_target": "a2",
        "q_obj_reaction": "a2"
    }
    
    mock_portfolio = {
        "AAPL": 0.40,
        "MSFT": 0.30,
        "BTC-USD": 0.30  # High crypto exposure
    }
    
    mock_portfolio_value = 50000.0  # 50k Euros
    
    try:
        final_report = generate_full_risk_report(
            user_answers=mock_answers,
            portfolio_weights=mock_portfolio,
            portfolio_value=mock_portfolio_value,
            yaml_config_path=config_path
        )
        
        # Display the Final Executive Summary
        print("==================================================")
        print("            RISKALIGN EXECUTIVE REPORT            ")
        print("==================================================")
        
        mifid = final_report['mifid_profile']
        print(f"USER PROFILE:       SRI {mifid['user_sri_profile']} (Raw Score: {mifid['raw_weighted_score']})")
        print(f"MiFID Capping:      {'Triggered' if mifid['capping_triggered'] else 'Clear'}")
        print("-" * 50)
        
        quant = final_report['quant_metrics']
        vol = quant['volatility_analysis']['actual_volatility'] * 100
        var_abs = quant['var_analysis']['var_absolute']
        print(f"PORTFOLIO RISK:     Actual Volatility {vol:.2f}%")
        print(f"MONTHLY VaR (95%):  €{var_abs:,.2f}")
        print("-" * 50)
        
        match = final_report['final_assessment']
        print(f"ALIGNMENT DELTA:    {match['delta']:+}")
        print(f"STATUS COLOR:       {match['status_color']}")
        print(f"STATUS MESSAGE:     {match['status_label']}")
        
        if match['emergency_brake_active']:
            print(f"!!! EMERGENCY OVERRIDE: {match['emergency_brake_reason']}")
            
        print("==================================================")
        
    except Exception as e:
        print(f"Error during pipeline execution: {e}")