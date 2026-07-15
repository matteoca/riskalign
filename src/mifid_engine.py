# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import yaml
from typing import Dict, Any, List

def load_questionnaire(yaml_path: str) -> Dict[str, Any]:
    """
    Loads and deserializes the YAML questionnaire configuration file.
    """
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Configuration file '{yaml_path}' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")


def validate_consistency(user_answers: Dict[str, str], config: Dict[str, Any]) -> List[str]:
    """
    Checks user answers against consistency rules defined in the YAML metadata.
    Returns a list of warning messages for contradictory answer pairs.
    """
    warnings = []
    rules = config['metadata'].get('consistency_rules', [])

    for rule in rules:
        cond_a = rule['condition_a']
        cond_b = rule['condition_b']

        q_a = cond_a['question']
        q_b = cond_b['question']

        if user_answers.get(q_a) == cond_a['answer'] and user_answers.get(q_b) == cond_b['answer']:
            warnings.append(rule['warning'])

    return warnings


def calculate_mifid_profile(user_answers: Dict[str, str], yaml_path: str) -> Dict[str, Any]:
    """
    Calculates the MiFID risk profile (SRI scale 1-7) based on user answers.
    Uses non-linear intra-pillar weighting when available.

    :param user_answers: Dictionary mapping question IDs to option IDs.
    :param yaml_path: Path to the questionnaire.yaml file.
    :return: Dictionary containing the calculated SRI profile, pillar averages, flags, and warnings.
    """
    config = load_questionnaire(yaml_path)
    questions = config['questions']
    metadata = config['metadata']

    # 1. Run consistency validation
    consistency_warnings = validate_consistency(user_answers, config)

    # 2. Build question lookup
    questions_dict = {q['id']: q for q in questions}

    # 3. Calculate weighted score per pillar (non-linear if intra_weight is defined)
    pillar_weighted_scores: Dict[str, float] = {pillar: 0.0 for pillar in metadata['pillars'].keys()}
    pillar_total_weights: Dict[str, float] = {pillar: 0.0 for pillar in metadata['pillars'].keys()}

    for q_id, ans_id in user_answers.items():
        if q_id not in questions_dict:
            continue

        q_data = questions_dict[q_id]
        pillar = q_data['pillar']
        intra_weight = q_data.get('intra_weight', 1.0)

        # Find the score for the selected answer
        score = None
        for option in q_data['options']:
            if option['id'] == ans_id:
                score = option['score']
                break

        if score is None:
            print(f"Warning: Invalid answer ID '{ans_id}' for question '{q_id}'.")
            continue

        pillar_weighted_scores[pillar] += score * intra_weight
        pillar_total_weights[pillar] += intra_weight

    # 4. Compute pillar averages (normalized by total intra-weights)
    pillar_averages: Dict[str, float] = {}
    for pillar in metadata['pillars'].keys():
        if pillar_total_weights[pillar] > 0:
            pillar_averages[pillar] = pillar_weighted_scores[pillar] / pillar_total_weights[pillar]
        else:
            pillar_averages[pillar] = 1.0  # Fallback to minimum

    # 5. Calculate the final inter-pillar weighted score (1-5 scale)
    weighted_score = 0.0
    for pillar, meta in metadata['pillars'].items():
        weighted_score += pillar_averages[pillar] * meta['weight']

    # 6. Map to SRI scale (1-7) via linear interpolation
    # Formula: SRI = 1 + (weighted_score - 1) * (7 - 1) / (5 - 1)
    raw_sri = 1 + (weighted_score - 1) * 6 / 4
    sri_profile = max(1, min(7, round(raw_sri)))

    # 7. Apply Capping Logic (Financial Safety Block)
    capping_triggered = False
    fin_meta = metadata['pillars'].get('financial_situation')

    if fin_meta and fin_meta.get('enforce_capping', False):
        if pillar_averages.get('financial_situation', 5.0) <= fin_meta['cap_threshold_score']:
            if sri_profile > fin_meta['max_allowed_sri']:
                sri_profile = fin_meta['max_allowed_sri']
                capping_triggered = True

    # 8. Structure the output
    return {
        "user_sri_profile": sri_profile,
        "raw_weighted_score": round(weighted_score, 2),
        "pillar_averages": {k: round(v, 2) for k, v in pillar_averages.items()},
        "capping_triggered": capping_triggered,
        "consistency_warnings": consistency_warnings
    }


if __name__ == "__main__":
    mock_answers = {
        "q_exp_education": "a3",
        "q_exp_frequency": "a4",
        "q_exp_derivatives": "a4",
        "q_exp_duration": "a3",
        "q_exp_diversification": "a4",
        "q_fin_income_stability": "a1",
        "q_fin_loss_capacity": "a1",
        "q_fin_wealth_pct": "a1",
        "q_fin_liquidity_need": "a1",
        "q_fin_debt_obligations": "a1",
        "q_obj_horizon": "a3",
        "q_obj_target": "a3",
        "q_obj_reaction": "a3",
        "q_obj_inflation_fear": "a2",
        "q_obj_max_acceptable_loss": "a3"
    }

    results = calculate_mifid_profile(mock_answers, "config/questionnaire.yaml")

    print("--- RISK PROFILING ENGINE SANITY CHECK ---")
    print(f"Pillar Averages: {results['pillar_averages']}")
    print(f"Raw Weighted Score (1-5): {results['raw_weighted_score']}")
    print(f"Final SRI Profile (1-7): {results['user_sri_profile']}")
    print(f"Capping Triggered?: {results['capping_triggered']}")
    if results['consistency_warnings']:
        print(f"Consistency Warnings: {results['consistency_warnings']}")
