# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import pytest
from src.mifid_engine import calculate_mifid_profile

def test_mifid_capping_logic(mocker):
    """
    Test that a financially weak profile gets forcefully capped to a low SRI,
    regardless of their aggressive psychological answers.
    """
    # We mock the configuration loading to inject a deterministic setup
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
            }
        },
        "questions": [
            {"id": "q1", "pillar": "experience", "options": [{"id": "a1", "score": 5}]},
            {"id": "q2", "pillar": "financial_situation", "options": [{"id": "a2", "score": 1}]}
        ]
    }
    
    mocker.patch("src.mifid_engine.load_questionnaire", return_value=mock_config)
    
    mock_answers = {"q1": "a1", "q2": "a2"}
    
    # Execute
    result = calculate_mifid_profile(mock_answers, "dummy_path.yaml")
    
    # Assertions
    assert result["capping_triggered"] is True
    assert result["user_sri_profile"] == 2 # Capped at max_allowed_sri
    assert result["pillar_averages"]["financial_situation"] == 1.0