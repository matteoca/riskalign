# ⚖️ RiskAlign

A WealthTech engine for algorithmic alignment between an investor's MiFID II risk profile and the quantitative risk of their portfolio.

## What it does

RiskAlign runs a three-phase pipeline:

1. **MiFID Engine** — Scores the investor across three pillars (Experience, Financial Situation, Objectives) and maps the result to an SRI profile on a 1–7 scale. Includes a financial safety cap: if the investor's financial situation is below a critical threshold, the SRI is forcefully capped regardless of psychological preferences.

2. **Quant Engine** — Downloads 5 years of historical market data via Yahoo Finance, computes log returns, the covariance matrix, and derives the portfolio's actual annualized volatility and monthly parametric VaR (95%).

3. **Matching Engine** — Converts portfolio volatility into a continuous SRI using ESMA PRIIPs brackets, calculates the mismatch delta against the investor's profile, and outputs a traffic-light verdict (🔵 → 🟢 → 🟡 → 🔴). A VaR Emergency Brake can override the verdict to RED if the portfolio's downside risk exceeds the investor's declared loss tolerance.

## Project structure

```
riskalign/
├── config/
│   └── questionnaire.yaml   # Questionnaire structure, pillar weights, capping rules
├── src/
│   ├── main.py              # Pipeline orchestrator
│   ├── mifid_engine.py      # MiFID qualitative profiling
│   ├── quant_engine.py      # Quantitative risk analysis
│   └── matching_engine.py   # Delta & traffic-light logic
├── ui/
│   └── app.py               # Streamlit web interface
├── tests/                   # pytest test suite
└── notebooks/               # Jupyter notebooks for prototyping
```

## Setup

```bash
# Create and activate virtual environment (Python 3.13)
py -3.13 -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the app

```bash
streamlit run ui/app.py
```

## Running tests

```bash
pytest tests/
```

## Notes

- The questionnaire (`config/questionnaire.yaml`) is fully data-driven. Pillar weights, capping thresholds, and questions can be modified without touching the engine code.
- The UI is currently in Italian; the backend is in English. Multi-language support is planned.
