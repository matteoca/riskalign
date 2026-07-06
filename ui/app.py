# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import streamlit as st
import yaml
import os
import sys
import pandas as pd

# Aggiungiamo la root directory al path per importare i moduli backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import generate_full_risk_report

# ==========================================
# CONFIGURAZIONE PAGINA
# ==========================================
st.set_page_config(
    page_title="RiskAlign - WealthTech Engine",
    page_icon="⚖️",
    layout="wide"
)

# ==========================================
# FUNZIONI DI SUPPORTO
# ==========================================
@st.cache_data
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'questionnaire.yaml')
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

config = load_config()

# ==========================================
# INTERFACCIA UTENTE
# ==========================================
st.title("⚖️ RiskAlign")
st.subheader("Allineamento algoritmico tra Profilo MiFID e Rischio Quantitativo")

# Creiamo i tab per separare il flusso logico
tab1, tab2, tab3 = st.tabs(["📋 1. Profilo (MiFID)", "💼 2. Portafoglio", "🚦 3. Analisi e Semaforo"])

# --- TAB 1: QUESTIONARIO MIFID ---
with tab1:
    st.markdown("### Questionario di Profilazione")
    st.markdown("Rispondi alle seguenti domande per calcolare il tuo profilo di rischio (SRI).")
    
    # Inizializziamo il dizionario per salvare le risposte
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    with st.form("mifid_form"):
        for question in config['questions']:
            # Creiamo un dizionario per mappare il testo dell'opzione al suo ID
            options_dict = {opt['text']: opt['id'] for opt in question['options']}
            
            # Mostriamo i radio button
            selected_text = st.radio(
                label=question['text'],
                options=list(options_dict.keys()),
                key=question['id']
            )
            # Salviamo l'ID della risposta
            st.session_state.user_answers[question['id']] = options_dict[selected_text]
            
        submit_mifid = st.form_submit_button("Salva Profilo")
        if submit_mifid:
            st.success("Profilo salvato correttamente! Passa alla scheda Portafoglio.")

# --- TAB 2: PORTAFOGLIO (Input in Valore Assoluto) ---
# --- TAB 2: PORTAFOGLIO (Input da CSV o Manuale) ---
with tab2:
    st.markdown("### Inserimento Portafoglio")
    st.markdown("Popola il tuo portafoglio caricando un file CSV o inserendo gli asset manualmente.")
    
    # 1. Dizionario dei Ticker (il tuo database precompilato)
    POPULAR_TICKERS = {
        "IE00B4L5Y983": "iShares Core MSCI World (Azionario Globale)",
        "VWCE.DE": "Vanguard FTSE All-World (Azionario Globale)",
        "SPY": "SPDR S&P 500 ETF (Azionario USA)",
        "QQQ": "Invesco QQQ Trust (Nasdaq 100)",
        "CSSPX.MI": "iShares Core S&P 500 UCITS (USA - Borsa Italiana)",
        "SEGA.MI": "iShares Core € Govt Bond UCITS (Titoli di Stato Europa)",
        "TLT": "iShares 20+ Year Treasury Bond (Titoli di Stato USA)",
        "AGG": "iShares Core US Aggregate Bond (Obbligazionario USA)",
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corp.",
        "NVDA": "NVIDIA Corp.",
        "GOOGL": "Alphabet Inc. (Google)",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "META": "Meta Platforms (Facebook)",
        "BRK-B": "Berkshire Hathaway",
        "ENEL.MI": "Enel S.p.A.",
        "ENI.MI": "Eni S.p.A.",
        "ISP.MI": "Intesa Sanpaolo S.p.A.",
        "UCG.MI": "UniCredit S.p.A.",
        "RACE.MI": "Ferrari N.V.",
        "STLAM.MI": "Stellantis N.V.",
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
        "GLD": "SPDR Gold Shares (Oro fisico)",
        "SLV": "iShares Silver Trust (Argento fisico)",
        "EURUSD=X": "Euro / Dollaro Statunitense (Forex)"
    }
    
    # Inizializzazione DataFrame di sessione se vuoto
    if 'portfolio_df' not in st.session_state:
        st.session_state.portfolio_df = pd.DataFrame(columns=["Ticker", "Controvalore (€)"])

    # Sotto-tab interne per dividere le modalità di inserimento
    input_mode = st.radio("Scegli la modalità di inserimento:", ["📁 Carica File CSV", "➕ Inserimento Manuale Asset"], horizontal=True)

    # --- MODALITÀ A: CARICAMENTO CSV ---
    if input_mode == "📁 Carica File CSV":
        st.markdown("#### Importazione da Excel / CSV")
        st.info("ℹ️ Il file deve essere un CSV separato da virgole o punto e virgola, contenente due colonne nominate esattamente: **Ticker** e **Controvalore**.")
        
        # Bottone per scaricare un modello di esempio (UX eccellente)
        template_df = pd.DataFrame([{"Ticker": "AAPL", "Controvalore": 10000.0}, {"Ticker": "VWCE.DE", "Controvalore": 25000.0}])
        csv_template = template_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Modello CSV di Esempio",
            data=csv_template,
            file_name="modello_portafoglio.csv",
            mime="text/csv"
        )
        
        uploaded_file = st.file_uploader("Trascina qui il tuo file portafoglio (.csv)", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Proviamo a leggere il file gestendo sia virgole che punti e virgola
                df_loaded = pd.read_csv(uploaded_file, sep=None, engine='python')
                
                # Normalizzazione dei nomi delle colonne per evitare problemi di maiuscole/minuscole
                df_loaded.columns = [c.strip().capitalize() for c in df_loaded.columns]
                
                # Rinominiamo per mappare lo standard interno
                if "Controvalore" in df_loaded.columns:
                    df_loaded = df_loaded.rename(columns={"Controvalore": "Controvalore (€)"})
                
                # Validazione strutturale
                if "Ticker" in df_loaded.columns and "Controvalore (€)" in df_loaded.columns:
                    # Pulizia dati: ticker in maiuscolo e rimozione righe vuote
                    df_loaded["Ticker"] = df_loaded["Ticker"].astype(str).str.upper().str.strip()
                    df_loaded["Controvalore (€)"] = pd.to_numeric(df_loaded["Controvalore (€)"], errors='coerce')
                    df_loaded = df_loaded.dropna(subset=["Ticker", "Controvalore (€)"])
                    
                    if st.button("✅ Applica e Sovrascrivi Portafoglio"):
                        st.session_state.portfolio_df = df_loaded[["Ticker", "Controvalore (€)"]]
                        st.success(f"Importati con successo {len(df_loaded)} asset!")
                        st.rerun()
                else:
                    st.error("Errore: Il file non contiene le colonne 'Ticker' e 'Controvalore'. Verifica il file di esempio.")
            except Exception as e:
                st.error(f"Errore nella lettura del file: {e}")

    # --- MODALITÀ B: INSERIMENTO MANUALE ---
    else:
        st.markdown("#### Aggiungi singolo Asset")
        with st.expander("Apri pannello di aggiunta", expanded=True):
            col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
            
            with col_t1:
                options = ["Seleziona..."] + list(POPULAR_TICKERS.keys()) + ["Altro (Inserimento manuale)"]
                selected_option = st.selectbox(
                    "Scegli un asset:", 
                    options=options,
                    format_func=lambda x: f"{x} - {POPULAR_TICKERS[x]}" if x in POPULAR_TICKERS else x
                )
                
                if selected_option == "Altro (Inserimento manuale)":
                    custom_ticker = st.text_input("Inserisci il Ticker Yahoo Finance (es. TSLA, NVDA):").upper().strip()
                else:
                    custom_ticker = ""
                    
            with col_t2:
                new_amount = st.number_input("Controvalore (€)", min_value=0.0, step=1000.0, format="%.2f")
                
            with col_t3:
                st.write("") 
                st.write("")
                if st.button("Aggiungi Asset", use_container_width=True):
                    final_ticker = custom_ticker if selected_option == "Altro (Inserimento manuale)" else selected_option
                    
                    if final_ticker and final_ticker != "Seleziona..." and new_amount > 0:
                        new_row = pd.DataFrame([{"Ticker": final_ticker, "Controvalore (€)": new_amount}])
                        st.session_state.portfolio_df = pd.concat([st.session_state.portfolio_df, new_row], ignore_index=True)
                        st.rerun()
                    else:
                        st.warning("Compila tutti i campi prima di aggiungere.")

    st.divider()

    # --- GESTIONE PORTAFOGLIO: RESET / SALVA / CARICA ---
    col_mgmt1, col_mgmt2, col_mgmt3 = st.columns([1, 2, 2])

    with col_mgmt1:
        if st.button("🗑️ Reset Portafoglio", use_container_width=True):
            st.session_state.portfolio_df = pd.DataFrame(columns=["Ticker", "Controvalore (€)"])
            st.session_state.pop("portfolio_weights", None)
            st.session_state.pop("portfolio_value", None)
            st.rerun()

    with col_mgmt2:
        save_name = st.text_input("Nome portafoglio da salvare:", placeholder="es. portafoglio_2025")
        if st.button("💾 Salva Portafoglio", use_container_width=True):
            if not st.session_state.portfolio_df.empty and save_name.strip():
                save_path = os.path.join(os.path.dirname(__file__), '..', 'data', f"{save_name.strip()}.csv")
                st.session_state.portfolio_df.to_csv(save_path, index=False)
                st.success(f"Portafoglio salvato come **{save_name.strip()}.csv**")
            elif not save_name.strip():
                st.warning("Inserisci un nome prima di salvare.")
            else:
                st.warning("Il portafoglio è vuoto, nulla da salvare.")

    with col_mgmt3:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        saved_files = [f[:-4] for f in os.listdir(data_dir) if f.endswith('.csv')]
        if saved_files:
            selected_file = st.selectbox("Carica un portafoglio salvato:", options=[""] + saved_files)
            if st.button("📂 Carica", use_container_width=True):
                if selected_file:
                    load_path = os.path.join(data_dir, f"{selected_file}.csv")
                    st.session_state.portfolio_df = pd.read_csv(load_path)
                    st.success(f"Portafoglio **{selected_file}** caricato.")
                    st.rerun()
        else:
            st.info("Nessun portafoglio salvato disponibile.")

    st.divider()

    # 4. Visualizzazione e calcolo pesi (comune a entrambi i metodi di input)
    st.markdown("**Il tuo Portafoglio Attuale:**")
    
    if not st.session_state.portfolio_df.empty:
        # Consentiamo all'utente di modificare gli importi o cancellare righe direttamente dall'editor
        edited_df = st.data_editor(
            st.session_state.portfolio_df, 
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", required=True, disabled=True),
                "Controvalore (€)": st.column_config.NumberColumn("Controvalore (€)", required=True, min_value=1.0, format="€ %.2f")
            }
        )
        # Sincronizziamo lo stato
        st.session_state.portfolio_df = edited_df
        
        total_value = edited_df["Controvalore (€)"].sum()
        st.metric("Controvalore Totale Portafoglio", f"€ {total_value:,.2f}")
        
        if total_value > 0:
            st.markdown("**Distribuzione percentuale calcolata:**")
            display_df = edited_df.copy()
            display_df["Peso (%)"] = (display_df["Controvalore (€)"] / total_value) * 100
            st.dataframe(display_df.style.format({"Peso (%)": "{:.2f}%"}), use_container_width=True)
            
            # Impacchettamento dati finale per src/main.py
            st.session_state.portfolio_weights = {
                row["Ticker"]: row["Controvalore (€)"] / total_value 
                for index, row in edited_df.iterrows()
            }
            st.session_state.portfolio_value = total_value
    else:
        st.info("Il portafoglio è vuoto. Carica un file CSV o usa l'inserimento manuale per iniziare.")

# --- TAB 3: DASHBOARD SEMAFORO ---
with tab3:
    st.markdown("### Report di Allineamento")
    
    if st.button("🚀 Calcola Rischio e Allineamento", type="primary"):
        if not st.session_state.user_answers:
            st.error("Per favore, compila e salva il questionario MiFID prima di procedere.")
        elif 'portfolio_weights' not in st.session_state or not st.session_state.portfolio_weights:
            st.error("Per favore, inserisci almeno un asset nel portafoglio.")
        else:
            with st.spinner("Analisi quantitativa in corso (download dati da mercato storici)..."):
                try:
                    # Invocazione del motore unificato (src/main.py)
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'questionnaire.yaml')
                    report = generate_full_risk_report(
                        user_answers=st.session_state.user_answers,
                        portfolio_weights=st.session_state.portfolio_weights,
                        portfolio_value=st.session_state.portfolio_value,
                        yaml_config_path=config_path
                    )
                    
                    mifid = report['mifid_profile']
                    quant = report['quant_metrics']
                    match = report['final_assessment']

                    # --- DISCLAIMER TICKER ESCLUSI ---
                    if quant.get('dropped_tickers'):
                        dropped = ', '.join(quant['dropped_tickers'])
                        st.warning(f"⚠️ **Attenzione:** I seguenti ticker non hanno restituito dati storici validi e sono stati esclusi dall'analisi: **{dropped}**. I pesi del portafoglio sono stati ricalcolati di conseguenza. I risultati si riferiscono esclusivamente agli asset per cui i dati erano disponibili.")

                    # --- RENDER DELLA DASHBOARD ---
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info("👤 **Profilo Investitore (MiFID)**")
                        st.metric("SRI Utente", f"{mifid['user_sri_profile']} / 7")
                        if mifid['capping_triggered']:
                            st.warning("⚠️ **Freno di Prudenza Attivo:** Il tuo SRI è stato limitato a causa della tua situazione finanziaria o necessità di liquidità.")
                            
                    with col2:
                        st.info("📈 **Rischio Reale del Portafoglio**")
                        st.metric("Volatilità Annualizzata", f"{quant['volatility_analysis']['actual_volatility']*100:.2f}%")
                        st.metric("VaR Mensile (95%)", f"€ {quant['var_analysis']['var_absolute']:,.2f}")
                    
                    st.divider()
                    
                    # --- IL SEMAFORO ---
                    st.markdown("### 🚦 Esito di Allineamento")
                    
                    color_map = {
                        "RED": ("🔴", "Rischio Critico (Portafoglio bloccato)"),
                        "YELLOW": ("🟡", "Allerta (Rischio superiore al profilo)"),
                        "GREEN": ("🟢", "Perfettamente Allineato"),
                        "GRAY": ("⚪", "Sotto-esposizione Lieve"),
                        "BLUE": ("🔵", "Sotto-esposizione Severa (Rischio inflazione)")
                    }
                    
                    icon, label = color_map.get(match['status_color'], ("❓", "Errore Sconosciuto"))
                    
                    st.header(f"{icon} {label}")
                    st.write(f"**Delta (Scostamento):** {match['delta']:+.2f}")
                    st.write(f"**SRI Continuo Calcolato (Portafoglio):** {match['portfolio_continuous_sri']:.2f}")
                    
                    if match['emergency_brake_active']:
                        st.error(f"🛑 **BLOCCO DI EMERGENZA (VaR):** {match['emergency_brake_reason']}")
                        
                except Exception as e:
                    st.error(f"Si è verificato un errore durante l'elaborazione quantitativa: {e}")