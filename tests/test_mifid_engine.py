# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import pytest
from src.mifid_engine import calculate_mifid_profile, validate_consistency


def test_mifid_capping_logic(mocker):
    """
    Test that a financially weak profile gets forcefully capped to a low SRI,
    regardless of aggressive psychological answers.
    """
    mock_config = {
        "metadata": {
            "pillars": {
                "experience": {"weight": 0.4},
                "financial_situation": {
                    "weight": 0.3,
                    "enforce_capping": True,
                    "cap_threshold_score": 1.5,
                    "max_allowed_sri": 2
                }
            },
            "consistency_rules": []
        },
        "questions": [
            {"id": "q1", "pillar": "experience", "intra_weight": 1.0, "options": [{"id": "a1", "score": 5}]},
            {"id": "q2", "pillar": "financial_situation", "intra_weight": 1.0, "options": [{"id": "a2", "score": 1}]}
        ]
    }

    mocker.patch("src.mifid_engine.load_questionnaire", return_value=mock_config)

    mock_answers = {"q1": "a1", "q2": "a2"}
    result = calculate_mifid_profile(mock_answers, "dummy_path.yaml")

    assert result["capping_triggered"] is True
    assert result["user_sri_profile"] == 2
    assert result["pillar_averages"]["financial_situation"] == 1.0


def test_non_linear_scoring(mocker):
    """
    Test that intra-pillar weights are applied correctly.
    A high-weight question should dominate the pillar average.
    """
    mock_config = {
        "metadata": {
            "pillars": {
                "experience": {"weight": 1.0}
            },
            "consistency_rules": []
        },
        "questions": [
            {"id": "q1", "pillar": "experience", "intra_weight": 0.80, "options": [{"id": "a1", "score": 1}]},
            {"id": "q2", "pillar": "experience", "intra_weight": 0.20, "options": [{"id": "a1", "score": 5}]}
        ]
    }

    mocker.patch("src.mifid_engine.load_questionnaire", return_value=mock_config)

    result = calculate_mifid_profile({"q1": "a1", "q2": "a1"}, "dummy.yaml")

    # Expected: (1*0.80 + 5*0.20) / (0.80 + 0.20) = 1.8
    assert result["pillar_averages"]["experience"] == 1.8


def test_consistency_validation():
    """
    Test that contradictory answers trigger the appropriate warning.
    """
    mock_config = {
        "metadata": {
            "consistency_rules": [
                {
                    "rule_id": "test_rule",
                    "description": "Test contradiction",
                    "condition_a": {"question": "q1", "answer": "a1"},
                    "condition_b": {"question": "q2", "answer": "a3"},
                    "warning": "Contradiction detected between q1 and q2."
                }
            ]
        }
    }

    # Contradictory answers
    warnings = validate_consistency({"q1": "a1", "q2": "a3"}, mock_config)
    assert len(warnings) == 1
    assert "Contradiction detected" in warnings[0]

    # Non-contradictory answers
    warnings = validate_consistency({"q1": "a1", "q2": "a1"}, mock_config)
    assert len(warnings) == 0


def test_consistency_warnings_in_profile(mocker):
    """
    Test that consistency warnings are included in the profile output.
    """
    mock_config = {
        "metadata": {
            "pillars": {
                "experience": {"weight": 1.0}
            },
            "consistency_rules": [
                {
                    "rule_id": "test",
                    "description": "test",
                    "condition_a": {"question": "q1", "answer": "a1"},
                    "condition_b": {"question": "q2", "answer": "a1"},
                    "warning": "Test warning message."
                }
            ]
        },
        "questions": [
            {"id": "q1", "pillar": "experience", "intra_weight": 0.5, "options": [{"id": "a1", "score": 3}]},
            {"id": "q2", "pillar": "experience", "intra_weight": 0.5, "options": [{"id": "a1", "score": 3}]}
        ]
    }

    mocker.patch("src.mifid_engine.load_questionnaire", return_value=mock_config)

    result = calculate_mifid_profile({"q1": "a1", "q2": "a1"}, "dummy.yaml")

    assert len(result["consistency_warnings"]) == 1
    assert "Test warning" in result["consistency_warnings"][0]
