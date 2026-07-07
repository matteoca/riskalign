## 🛠️ Fase 1: Ottimizzazione Tecnica e UX (Breve Termine)
[x] Implementare il Caching dei Dati: Attualmente, se l'utente cambia una risposta del questionario MiFID, la dashboard ricarica i dati da yfinance. Usare @st.cache_data per memorizzare i prezzi scaricati ed evitare chiamate API ridondanti (velocizza l'app del 90%).

[ ] Esportazione PDF: Aggiungere un bottone nella UI (Tab 3) per generare e scaricare un report in PDF pulito e formattato, fondamentale per l'uso B2B (il consulente che consegna il documento al cliente).

[ ] Gestione Rischio Valutario (FX Risk): Attualmente i calcoli assumono che tutti gli asset siano nella valuta di base. Implementare una conversione automatica in Euro per gli asset quotati in USD, per riflettere la reale volatilità subita dall'investitore europeo.

## 📋 Fase 1.5: Potenziamento Questionario MiFID
[ ] Ampliamento Domande: Aggiungere almeno 2 domande per pilastro per migliorare la granularità della profilazione, mantenendo il questionario snello e non oneroso per l'utente.

[ ] Scoring Non Lineare: Sostituire la media aritmetica intra-pilastro con un sistema di pesi differenziati per domanda, dando più rilevanza alle domande con maggiore potere discriminante (es. capacità di perdita > orizzonte temporale).

[ ] Validazione Incoerenze: Implementare un modulo di consistency check che rilevi risposte contraddittorie (es. "non ho mai investito" + "faccio trading giornaliero con derivati") e segnali un warning all'utente o al consulente.

## 📊 Fase 2: Potenziamento del Motore Quantitativo (Medio Termine)
[ ] Evoluzione del Value at Risk (VaR): Passare dal VaR Parametrico (che assume una distribuzione Normale dei rendimenti) al VaR Storico o a una simulazione Monte Carlo, per catturare meglio i "Cigni Neri" (fat tails).

[ ] Volatilità Dinamica (EWMA): Implementare una media mobile esponenziale per dare maggior peso agli eventi di mercato recenti rispetto a quelli di 5 anni fa.

[ ] Stress Testing Predefiniti: Inserire un modulo per simulare scenari storici specifici sul portafoglio (es. "Come si sarebbe comportato durante il crollo Covid del 2020 o l'inflazione del 2022?").

## 📥 Fase 2.5: Smart Import Portafoglio
[ ] Smart CSV Parser: Implementare un parser intelligente per il caricamento del portafoglio da CSV, in grado di riconoscere automaticamente i formati di export delle principali app bancarie (es. Fineco, Directa, Degiro, Interactive Brokers). Valutare l'uso di un LLM per inferire la mappatura delle colonne (ticker, quantità, controvalore) quando il formato non è standard.

## 🚀 Fase 3: Infrastruttura e Messa in Produzione (Deployment)
[ ] Congelamento delle Dipendenze: Generare un file requirements.txt pulito (rimuovendo le librerie non usate) per garantire la riproducibilità dell'ambiente.

[ ] Dockerizzazione: Scrivere un Dockerfile per incapsulare l'applicazione e renderla agnostica rispetto al sistema operativo.

[ ] Continuous Integration (CI): Configurare GitHub Actions per far girare in automatico la suite di test (pytest) a ogni nuovo commit.

[ ] Deployment Pubblico: Pubblicare l'applicazione su una piattaforma Cloud (es. Streamlit Community Cloud, Heroku o AWS EC2) per renderla accessibile tramite URL.

## 🔌 Fase 4: Integrazioni Business (Lungo Termine)
[ ] Open Banking API: Integrare un provider (es. Tink, Plaid) per l'ingestione automatica delle posizioni titoli direttamente dal conto corrente dell'utente.

[ ] API REST per Report: Esporre un endpoint API (es. FastAPI) che consenta a sistemi terzi di invocare la pipeline RiskAlign e scaricare il report di allineamento in formato JSON o PDF, abilitando l'integrazione con CRM, piattaforme di consulenza e applicazioni esterne.