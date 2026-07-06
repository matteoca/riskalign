# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import yaml
from typing import Dict, Any, List

def load_questionnaire(yaml_path: str) -> Dict[str, Any]:
    """
    Loads and deserializes the YAML questionnaire configuration file.
    
    :param yaml_path: Path to the questionnaire.yaml file.
    :return: Dictionary containing the questionnaire structure.
    """
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Configuration file '{yaml_path}' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

def calculate_mifid_profile(user_answers: Dict[str, str], yaml_path: str) -> Dict[str, Any]:
    """
    Calculates the MiFID risk profile (SRI scale 1-7) based on user answers.
    
    :param user_answers: Dictionary mapping question IDs to option IDs.
                         Example: {"q_exp_derivatives": "a1", "q_fin_loss_capacity": "a3"}
    :param yaml_path: Path to the questionnaire.yaml file.
    :return: Dictionary containing the calculated SRI profile, pillar averages, and flags.
    """
    config = load_questionnaire(yaml_path)
    questions = config['questions']
    metadata = config['metadata']

    # 1. Initialize containers for pillar scores
    pillar_scores: Dict[str, List[int]] = {pillar: [] for pillar in metadata['pillars'].keys()}
    questions_dict = {q['id']: q for q in questions}

    # 2. Map user answers to their respective numerical scores
    for q_id, ans_id in user_answers.items():
        if q_id in questions_dict:
            q_data = questions_dict[q_id]
            pillar = q_data['pillar']
            
            # Find the score associated with the selected option
            score_found = False
            for option in q_data['options']:
                if option['id'] == ans_id:
                    pillar_scores[pillar].append(option['score'])
                    score_found = True
                    break
            
            if not score_found:
                print(f"Warning: Invalid answer ID '{ans_id}' for question '{q_id}'.")

    # 3. Calculate the arithmetic mean for each individual pillar
    pillar_averages: Dict[str, float] = {}
    for pillar, scores in pillar_scores.items():
        # Fallback to minimum score (1.0) if a pillar has no answers to avoid division by zero
        pillar_averages[pillar] = sum(scores) / len(scores) if scores else 1.0

    # 4. Calculate the final weighted score (1-5 scale)
    weighted_score = 0.0
    for pillar, meta in metadata['pillars'].items():
        weighted_score += pillar_averages[pillar] * meta['weight']

    # 5. Mathematical mapping to the SRI scale (1-7) via linear interpolation
    # Formula: SRI = 1 + (weighted_score - 1) * (7 - 1) / (5 - 1)
    raw_sri = 1 + (weighted_score - 1) * 6 / 4
    sri_profile = max(1, min(7, round(raw_sri)))

    # 6. Apply Capping Logic (Financial Safety Block)
    capping_triggered = False
    fin_meta = metadata['pillars']['financial_situation']
    
    if fin_meta.get('enforce_capping', False):
        # Check if the financial situation score is below the critical threshold
        if pillar_averages['financial_situation'] <= fin_meta['cap_threshold_score']:
            # Forcefully cap the profile if the calculated SRI is too aggressive
            if sri_profile > fin_meta['max_allowed_sri']:
                sri_profile = fin_meta['max_allowed_sri']
                capping_triggered = True

    # 7. Structure the output dictionary
    return {
        "user_sri_profile": sri_profile,
        "raw_weighted_score": round(weighted_score, 2),
        "pillar_averages": {k: round(v, 2) for k, v in pillar_averages.items()},
        "capping_triggered": capping_triggered
    }

if __name__ == "__main__":
    # Mock user answers simulating an aggressive mindset but weak financial capacity
    mock_answers = {
        "q_exp_education": "a3",        # High expertise (5)
        "q_exp_frequency": "a4",        # Active trader (5)
        "q_exp_derivatives": "a4",      # Uses derivatives (5)
        
        "q_fin_income_stability": "a1",  # Unstable income (1)
        "q_fin_loss_capacity": "a1",     # Cannot bear losses (1)
        "q_fin_wealth_pct": "a1",        # Investing >70% of total wealth (1)
        
        "q_obj_horizon": "a3",          # Long term (5)
        "q_obj_target": "a3",           # Maximum growth (5)
        "q_obj_reaction": "a4"          # Buys the dips (5)
    }
    
    # Run sanity check pointing to the configuration file
    results = calculate_mifid_profile(mock_answers, "config/questionnaire.yaml")
    
    print("--- RISK PROFILING ENGINE SANITY CHECK ---")
    print(f"Pillar Averages: {results['pillar_averages']}")
    print(f"Raw Weighted Score (1-5): {results['raw_weighted_score']}")
    print(f"Final SRI Profile (1-7): {results['user_sri_profile']}")
    print(f"Capping Triggered?: {results['capping_triggered']}")