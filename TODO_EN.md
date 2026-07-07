## 🛠️ Phase 1: Technical & UX Optimization (Short Term)
[x] Implement Data Caching: Currently, if the user changes a MiFID questionnaire answer, the dashboard reloads data from yfinance. Use @st.cache_data to store downloaded prices and avoid redundant API calls (speeds up the app by ~90%).

[x] PDF Export: Add a button in the UI (Tab 3) to generate and download a clean, formatted PDF report — essential for B2B use cases (the advisor delivering the document to the client).

[ ] FX Risk Management: Currently the calculations assume all assets are denominated in the base currency. Implement automatic EUR conversion for USD-quoted assets to reflect the real volatility experienced by the European investor.

## 📋 Phase 1.5: MiFID Questionnaire Enhancement
[x] Expand Questions: Add at least 2 questions per pillar to improve profiling granularity, while keeping the questionnaire lean and not burdensome for the user.

[x] Non-Linear Scoring: Replace the intra-pillar arithmetic mean with a weighted scoring system per question, giving more relevance to questions with higher discriminating power (e.g. loss capacity > time horizon).

[x] Inconsistency Validation: Implement a consistency check module that detects contradictory answers (e.g. "I have never invested" + "I actively trade derivatives daily") and raises a warning to the user or advisor.

## 📊 Phase 2: Quantitative Engine Enhancement (Mid Term)
[ ] Value at Risk Evolution: Move from Parametric VaR (which assumes a Normal distribution of returns) to Historical VaR or a Monte Carlo simulation, to better capture "Black Swan" events (fat tails).

[ ] Dynamic Volatility (EWMA): Implement an exponentially weighted moving average to give more weight to recent market events compared to those from 5 years ago.

[ ] Predefined Stress Tests: Add a module to simulate specific historical scenarios on the portfolio (e.g. "How would this portfolio have performed during the Covid crash of 2020 or the 2022 inflation spike?").

## 📥 Phase 2.5: Smart Portfolio Import
[ ] Smart CSV Parser: Implement an intelligent parser for portfolio CSV uploads, capable of automatically recognizing export formats from major banking apps (e.g. Fineco, Directa, Degiro, Interactive Brokers). Evaluate using an LLM to infer column mappings (ticker, quantity, market value) when the format is non-standard.

## 🚀 Phase 3: Infrastructure & Production Deployment
[ ] Dependency Freeze: Generate a clean requirements.txt (removing unused libraries) to guarantee environment reproducibility.

[ ] Dockerization: Write a Dockerfile to containerize the application and make it OS-agnostic.

[ ] Continuous Integration (CI): Configure GitHub Actions to automatically run the test suite (pytest) on every new commit.

[ ] Public Deployment: Publish the application on a Cloud platform (e.g. Streamlit Community Cloud, Heroku or AWS EC2) to make it accessible via URL.

## 🔌 Phase 4: Business Integrations (Long Term)
[ ] Open Banking API: Integrate a provider (e.g. Tink, Plaid) for automatic ingestion of securities positions directly from the user's bank account.

[ ] REST API for Report: Expose an API endpoint (e.g. FastAPI) allowing third-party systems to invoke the RiskAlign pipeline and download the alignment report in JSON or PDF format, enabling integration with CRMs, advisory platforms, and external applications.

## ✨ Nice to Have
[ ] Portfolio Geographic Map: Display a choropleth world heatmap showing the geographic distribution of the portfolio. For individual stocks, derive the country from the exchange or headquarters (via yfinance). For common ETFs, maintain a static dictionary with the geographic breakdown. Render with Plotly choropleth integrated in Streamlit.
