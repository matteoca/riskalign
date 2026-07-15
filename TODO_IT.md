# 🗺️ RiskAlign: Sviluppo & Roadmap (Architettura B2B a 4 Livelli)

Questa roadmap riflette la transizione di RiskAlign da semplice calcolatore a **Motore di Risk Intelligence Componibile**, pensato per integrarsi nei processi di consulenti, banche e wealth manager.

## ⚙️ Livello 1: Risk Engine (Motore Quantitativo Core)
L'obiettivo di questo livello è calcolare le metriche dure del portafoglio.
- [x] **Gestione Rischio Valutario (FX Risk):** Implementare una conversione automatica in Euro per gli asset quotati in USD, per riflettere la reale volatilità subita dall'investitore europeo.
- [x] **Evoluzione del Value at Risk (VaR):** Passare dal VaR Parametrico al VaR Storico o a una simulazione Monte Carlo, per catturare meglio i "Cigni Neri" (fat tails).
- [x] **Volatilità Dinamica (EWMA):** Implementare una media mobile esponenziale per dare maggior peso agli eventi di mercato recenti.  σ²_t = λ·σ²_{t-1} + (1-λ)·r²_t
- [x] **Stress Testing Predefiniti:** Modulo per simulare scenari storici specifici sul portafoglio (es. "Come si sarebbe comportato durante il crollo Covid del 2020?").
- [x] **Backtesting del Drawdown:** Dato il portafoglio attuale, estrarre e mostrare il max drawdown storico reale per rendere tangibile il rischio vissuto in passato.
- [x] **Metriche Advisory (per Consulenti):**
  - [x] Maximum Drawdown storico (peggior calo peak-to-trough)
  - [x] Liquidity Risk (score basato su volume medio di scambio)
  - [x] Equity Exposure (% equity vs bond vs commodity vs altro)
  - [x] Concentrazione per titolo (Herfindahl-Hirschman Index)
  - [x] Concentrazione per settore (via yfinance `sector`)
  - [x] Concentrazione geografica (via yfinance `country`)

## 🧠 Livello 2: Behaviour Engine (Profilazione e Comportamento)
Andare oltre la compliance MiFID standard per mappare la vera tolleranza psicologica.
- [x] **Ampliamento Domande & Scoring Non Lineare:** Aggiunte domande per pilastro con pesi differenziati per maggiore discriminazione.
- [x] **Validazione Incoerenze:** Implementato modulo di consistency check per rilevare risposte contraddittorie.
- [ ] **Integrazione Bias Comportamentali:** Aggiungere metriche per misurare esplicitamente l'avversione alle perdite (Loss Aversion) e la probabilità di *panic selling*.
- [ ] **Cache del Profilo Utente:** Salvare il profilo compilato in sessione così che l'utente non debba ricompilarlo a ogni aggiornamento della pagina.

## 🎯 Livello 3: Matching Engine (Allineamento e KPI)
Il cuore del vantaggio competitivo: trasformare rischio e comportamento in una singola metrica di coerenza.
- [ ] **Risk Alignment Score (0-100):** Convertire l'attuale calcolo del "Delta" in un indice normalizzato da 0 a 100 (es. 95 = perfetto, 40 = fuori profilo) da usare come indicatore di business principale.
- [ ] **Confronto tra Scenari:** Permettere all'utente di salvare più portafogli e confrontarli side-by-side sullo stesso profilo MiFID, evidenziando quale configurazione ha uno *Score* migliore.
- [ ] **Storico delle Analisi:** Salvare i report generati con timestamp, per tracciare come evolve l'allineamento nel tempo se si modifica il portafoglio.

## 🤖 Livello 4: AI Copilot (Intelligence Generativa)
Usare l'LLM non per calcolare, ma per interpretare e spiegare i dati quantitativi al cliente.
- [ ] **Generazione Insight in Linguaggio Naturale:** Integrare un LLM che prenda in input i JSON del Risk Engine e generi un paragrafo testuale (es. "Il profilo è Moderato, ma la concentrazione Tech porta il rischio a Dinamico").
- [ ] **What-If Analysis & Azioni Correttive:** Permettere all'LLM di suggerire la mossa successiva (es. "Per tornare a uno score di 90, ridurre l'azionario del 10%"). Sostituisce e potenzia la classica *Sensitivity Analysis*.

## 🔌 Infrastruttura & Data Ingestion (L'Architettura API-First)
Rendere il motore "headless" e integrabile da terze parti (reti B2B).
- [ ] **Sviluppo Motore Headless (API REST):** Trasformare l'attuale backend in endpoint (es. FastAPI) che riceve JSON e restituisce l'Alignment Score e le metriche. Il frontend Streamlit diventerà solo uno dei client di questa API.
- [ ] **Smart CSV Parser:** Implementare un parser intelligente (potenzialmente guidato da LLM) in grado di riconoscere e mappare automaticamente i formati di export delle principali app bancarie.
- [ ] **Integrazione Open Banking:** Collegare un provider (es. Tink, Plaid) per l'ingestione automatica dei titoli bancari.
- [ ] **Deployment e Messa in Produzione:** Creazione file `requirements.txt` pulito, Dockerizzazione dell'app e configurazione GitHub Actions per test CI.

## 🖥️ UX & Front-End (Il Client Dimostrativo in Streamlit)
Migliorare la dashboard che i consulenti useranno durante gli incontri.
- [x] **Implementare il Caching dei Dati:** Uso di `@st.cache_data` per evitare ricaricamenti di mercato continui.
- [x] **Esportazione PDF:** Generazione e download di un report PDF pulito per il cliente.
- [ ] **Barra di Progresso Questionario & Riepilogo:** Mostrare l'avanzamento visivo nel Tab 1 e un recap del profilo nel Tab 3 prima del calcolo.
- [ ] **Mappa Geografica del Portafoglio:** Visualizzazione Plotly (world heatmap) della scomposizione geografica degli asset azionari.