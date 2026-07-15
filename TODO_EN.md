# 🗺️ RiskAlign: Development & Roadmap (4-Layer B2B Architecture)

This roadmap reflects RiskAlign's transition from a simple calculator to a **Composable Risk Intelligence Engine**, designed to integrate into the workflows of advisors, banks, and wealth managers.

## ⚙️ Layer 1: Risk Engine (Core Quantitative Engine)
The goal of this layer is to compute the hard metrics of the portfolio.
- [x] **FX Risk Management:** Implement automatic EUR conversion for USD-quoted assets to reflect the real volatility experienced by the European investor.
- [x] **Value at Risk Evolution:** Move from Parametric VaR to Historical VaR or Monte Carlo simulation, to better capture "Black Swan" events (fat tails).
- [x] **Dynamic Volatility (EWMA):** Implement an exponentially weighted moving average to give more weight to recent market events.  σ²_t = λ·σ²_{t-1} + (1-λ)·r²_t
- [x] **Predefined Stress Tests:** Module to simulate specific historical scenarios on the portfolio (e.g. "How would it have performed during the Covid crash of 2020?").
- [x] **Drawdown Backtesting:** Given the current portfolio, extract and display the real historical max drawdown to make past risk tangible.
- [x] **Advisory Metrics (for Advisors):**
  - [x] Historical Maximum Drawdown (worst peak-to-trough decline)
  - [x] Liquidity Risk (score based on average trading volume)
  - [x] Equity Exposure (% equity vs bond vs commodity vs other)
  - [x] Concentration by title (Herfindahl-Hirschman Index)
  - [x] Concentration by sector (via yfinance `sector`)
  - [x] Geographic concentration (via yfinance `country`)

## 🧠 Layer 2: Behaviour Engine (Profiling & Behaviour)
Go beyond standard MiFID compliance to map the investor's true psychological tolerance.
- [x] **Expanded Questions & Non-Linear Scoring:** Added questions per pillar with differentiated weights for greater discrimination.
- [x] **Inconsistency Validation:** Implemented a consistency check module to detect contradictory answers.
- [ ] **Behavioural Bias Integration:** Add metrics to explicitly measure Loss Aversion and the probability of *panic selling*.
- [ ] **User Profile Caching:** Persist the completed profile in session so the user does not have to re-fill the questionnaire on every page refresh.

## 🎯 Layer 3: Matching Engine (Alignment & KPIs)
The core competitive advantage: transforming risk and behaviour into a single coherence metric.
- [ ] **Risk Alignment Score (0-100):** Convert the current "Delta" calculation into a normalized index from 0 to 100 (e.g. 95 = perfect, 40 = out of profile) to be used as the primary business indicator.
- [ ] **Scenario Comparison:** Allow the user to save multiple portfolios and compare them side-by-side against the same MiFID profile, highlighting which configuration has a better *Score*.
- [ ] **Analysis History:** Save generated reports with timestamps, to track how alignment evolves over time as the portfolio changes.

## 🤖 Layer 4: AI Copilot (Generative Intelligence)
Use the LLM not to calculate, but to interpret and explain quantitative data to the client.
- [ ] **Natural Language Insight Generation:** Integrate an LLM that takes the Risk Engine JSON output and generates a textual paragraph (e.g. "The profile is Moderate, but the Tech concentration pushes risk to Dynamic").
- [ ] **What-If Analysis & Corrective Actions:** Allow the LLM to suggest the next move (e.g. "To return to a score of 90, reduce equity exposure by 10%"). Replaces and enhances the classic *Sensitivity Analysis*.

## 🔌 Infrastructure & Data Ingestion (API-First Architecture)
Make the engine "headless" and integrable by third parties (B2B networks).
- [ ] **Headless Engine Development (REST API):** Transform the current backend into endpoints (e.g. FastAPI) that receive JSON and return the Alignment Score and metrics. The Streamlit frontend will become just one of this API's clients.
- [ ] **Smart CSV Parser:** Implement an intelligent parser (potentially LLM-driven) capable of automatically recognizing and mapping export formats from major banking apps.
- [ ] **Open Banking Integration:** Connect a provider (e.g. Tink, Plaid) for automatic ingestion of securities positions from the user's bank account.
- [ ] **Deployment & Production:** Create a clean `requirements.txt`, Dockerize the app, and configure GitHub Actions for CI testing.

## 🖥️ UX & Front-End (The Demonstrative Streamlit Client)
Improve the dashboard that advisors will use during client meetings.
- [x] **Implement Data Caching:** Use `@st.cache_data` to avoid continuous market data reloads.
- [x] **PDF Export:** Generation and download of a clean PDF report for the client.
- [ ] **Questionnaire Progress Bar & Summary:** Show visual progress in Tab 1 and a profile recap in Tab 3 before calculation.
- [x] **Portfolio Geographic Map:** Plotly visualization (world heatmap) of the geographic breakdown of equity assets.
