## 🛠️ Fase 1: Ottimizzazione Tecnica e UX (Breve Termine)
[ ] Implementare il Caching dei Dati: Attualmente, se l'utente cambia una risposta del questionario MiFID, la dashboard ricarica i dati da yfinance. Usare @st.cache_data per memorizzare i prezzi scaricati ed evitare chiamate API ridondanti (velocizza l'app del 90%).

[ ] Esportazione PDF: Aggiungere un bottone nella UI (Tab 3) per generare e scaricare un report in PDF pulito e formattato, fondamentale per l'uso B2B (il consulente che consegna il documento al cliente).

[ ] Gestione Rischio Valutario (FX Risk): Attualmente i calcoli assumono che tutti gli asset siano nella valuta di base. Implementare una conversione automatica in Euro per gli asset quotati in USD, per riflettere la reale volatilità subita dall'investitore europeo.

## 📊 Fase 2: Potenziamento del Motore Quantitativo (Medio Termine)
[ ] Evoluzione del Value at Risk (VaR): Passare dal VaR Parametrico (che assume una distribuzione Normale dei rendimenti) al VaR Storico o a una simulazione Monte Carlo, per catturare meglio i "Cigni Neri" (fat tails).

[ ] Volatilità Dinamica (EWMA): Implementare una media mobile esponenziale per dare maggior peso agli eventi di mercato recenti rispetto a quelli di 5 anni fa.

[ ] Stress Testing Predefiniti: Inserire un modulo per simulare scenari storici specifici sul portafoglio (es. "Come si sarebbe comportato durante il crollo Covid del 2020 o l'inflazione del 2022?").

## 🚀 Fase 3: Infrastruttura e Messa in Produzione (Deployment)
[ ] Congelamento delle Dipendenze: Generare un file requirements.txt pulito (rimuovendo le librerie non usate) per garantire la riproducibilità dell'ambiente.

[ ] Dockerizzazione: Scrivere un Dockerfile per incapsulare l'applicazione e renderla agnostica rispetto al sistema operativo.

[ ] Continuous Integration (CI): Configurare GitHub Actions per far girare in automatico la suite di test (pytest) a ogni nuovo commit.

[ ] Deployment Pubblico: Pubblicare l'applicazione su una piattaforma Cloud (es. Streamlit Community Cloud, Heroku o AWS EC2) per renderla accessibile tramite URL.

🔌 Fase 4: Integrazioni Business (Lungo Termine)
[ ] Open Banking API: Integrare un provider (es. Tink, Plaid) per l'ingestione automatica delle posizioni titoli direttamente dal conto corrente dell'utente.