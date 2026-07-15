# Copyright (c) 2026 Matteo Calia. All rights reserved.
# Proprietary and confidential. Unauthorized use, copying, or distribution is strictly prohibited.

import yfinance as yf
from fpdf import FPDF
from datetime import date
from typing import Dict, Any
from src.quant_engine import get_ticker_display_name

# Cache for asset classification (persists across calls within same session)
_classification_cache: Dict[str, str] = {}

# Mapping from yfinance quoteType to Italian asset class labels
_QUOTE_TYPE_MAP = {
    "EQUITY": "Azionario",
    "ETF": "ETF",
    "MUTUALFUND": "Fondo",
    "CRYPTOCURRENCY": "Crypto",
    "CURRENCY": "Forex",
    "FUTURE": "Commodity",
    "INDEX": "Indice",
}


def classify_asset(ticker: str) -> str:
    """Classify a ticker into an asset class using cached yfinance data."""
    if ticker in _classification_cache:
        return _classification_cache[ticker]

    try:
        info = yf.Ticker(ticker).info
        quote_type = info.get("quoteType", "")
        asset_class = _QUOTE_TYPE_MAP.get(quote_type, "Altro")
    except Exception:
        asset_class = "Altro"

    _classification_cache[ticker] = asset_class
    return asset_class


def volatility_to_risk_label(vol: float) -> str:
    """Map individual annualized volatility to a risk label."""
    if vol < 0.05:
        return "Molto Basso"
    elif vol < 0.12:
        return "Basso"
    elif vol < 0.20:
        return "Medio"
    elif vol < 0.30:
        return "Alto"
    else:
        return "Molto Alto"


def generate_pdf_report(report: Dict[str, Any], portfolio_weights: Dict[str, float],
                        portfolio_value: float) -> bytes:
    """
    Generates a PDF report from the full RiskAlign pipeline output.
    Returns the PDF as bytes (ready for download or API response).
    """
    mifid = report['mifid_profile']
    quant = report['quant_metrics']
    match = report['final_assessment']
    vol_analysis = quant['volatility_analysis']
    var_analysis = quant['var_analysis']

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- HEADER ---
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "RiskAlign - Report di Allineamento", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generato il {date.today().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # --- SEZIONE 1: PROFILO MIFID ---
    _section_title(pdf, "1. Profilo Investitore (MiFID II)")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"SRI Utente: {mifid['user_sri_profile']} / 7", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Punteggio Ponderato Grezzo: {mifid['raw_weighted_score']}", new_x="LMARGIN", new_y="NEXT")

    pillar_labels = {
        "experience": "Esperienza",
        "financial_situation": "Situazione Finanziaria",
        "objectives_and_preferences": "Obiettivi e Preferenze"
    }
    for pillar, avg in mifid['pillar_averages'].items():
        label = pillar_labels.get(pillar, pillar)
        pdf.cell(0, 7, f"  - {label}: {avg}/5.0", new_x="LMARGIN", new_y="NEXT")

    if mifid['capping_triggered']:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "  ** Freno di Prudenza Attivo: SRI limitato per situazione finanziaria critica.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- SEZIONE 2: RISCHIO QUANTITATIVO ---
    _section_title(pdf, "2. Rischio Quantitativo del Portafoglio")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Controvalore Totale: EUR {portfolio_value:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Volatilita' Storica (5Y): {vol_analysis['actual_volatility']*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    if 'ewma_volatility' in vol_analysis:
        pdf.cell(0, 7, f"Volatilita' EWMA (RiskMetrics, lambda={vol_analysis.get('ewma_lambda', 0.94)}): {vol_analysis['ewma_volatility']*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Volatilita' Naive (senza diversificazione): {vol_analysis['naive_volatility']*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Beneficio Diversificazione: {vol_analysis['diversification_benefit']*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"VaR Parametrico Mensile (95%): EUR {var_analysis['var_absolute']:,.2f} ({var_analysis['var_percentage']*100:.2f}%)", new_x="LMARGIN", new_y="NEXT")
    if 'var_historical' in quant:
        hvar = quant['var_historical']
        pdf.cell(0, 7, f"VaR Storico Mensile (95%): EUR {hvar['var_absolute']:,.2f} ({hvar['var_percentage']*100:.2f}%)", new_x="LMARGIN", new_y="NEXT")
    if 'max_drawdown' in quant:
        mdd = quant['max_drawdown']
        mdd_line = f"Max Drawdown: {mdd['max_drawdown']*100:.2f}% (da {mdd['peak_date']} a {mdd['trough_date']})"
        if mdd['recovery_date']:
            mdd_line += f" | Recupero: {mdd['recovery_date']}"
        else:
            mdd_line += " | Non ancora recuperato"
        pdf.cell(0, 7, mdd_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- SEZIONE 3: ESITO ALLINEAMENTO ---
    _section_title(pdf, "3. Esito di Allineamento")
    pdf.set_font("Helvetica", "", 11)

    color_labels = {
        "RED": "ROSSO - Rischio Critico",
        "YELLOW": "GIALLO - Allerta",
        "GREEN": "VERDE - Perfettamente Allineato",
        "GRAY": "GRIGIO - Sotto-esposizione Lieve",
        "BLUE": "BLU - Sotto-esposizione Severa"
    }
    status = color_labels.get(match['status_color'], match['status_color'])
    pdf.cell(0, 7, f"Semaforo: {status}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"SRI Continuo Portafoglio: {match['portfolio_continuous_sri']:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Delta (Scostamento): {match['delta']:+.2f}", new_x="LMARGIN", new_y="NEXT")

    if match['emergency_brake_active']:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, f"  BLOCCO DI EMERGENZA: {match['emergency_brake_reason']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- SEZIONE 4: STRESS TEST ---
    _section_title(pdf, "4. Stress Test Storici")
    pdf.set_font("Helvetica", "", 11)
    stress_tests = quant.get('stress_tests', [])
    if stress_tests:
        import math
        for st_result in stress_tests:
            ret_val = st_result['portfolio_return']
            if ret_val is not None and not math.isnan(ret_val):
                ret = ret_val * 100
                line = f"{st_result['label']} ({st_result['period']}): {ret:+.2f}%"
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 7, line)
                if st_result['excluded_tickers']:
                    excluded_names = [f"{get_ticker_display_name(t)} ({t})" for t in st_result['excluded_tickers']]
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 5, f"Titoli esclusi: {', '.join(excluded_names)}")
                    pdf.set_font("Helvetica", "", 11)
            else:
                note = st_result.get('note', 'Dati insufficienti per questo periodo.')
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 7, f"{st_result['label']}: N/D - {note}")
    else:
        pdf.cell(0, 7, "Nessuno scenario configurato.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- SEZIONE 5: METRICHE ADVISORY ---
    if quant.get('advisory_metrics'):
        _section_title(pdf, "5. Metriche Advisory")
        pdf.set_font("Helvetica", "", 11)
        adv = quant['advisory_metrics']

        pdf.cell(0, 7, f"HHI Concentrazione Titoli: {adv['hhi_title']:.0f} / 10000", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"Esposizione Bassa Liquidita': {adv['low_liquidity_exposure']:.1f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Esposizione per Classe di Asset:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for cls, w in sorted(adv['asset_class_breakdown'].items(), key=lambda x: -x[1]):
            pdf.cell(0, 6, f"  {cls}: {w*100:.1f}%", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Concentrazione per Settore:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for sec, w in sorted(adv['sector_breakdown'].items(), key=lambda x: -x[1]):
            pdf.cell(0, 6, f"  {sec}: {w*100:.1f}%", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Concentrazione Geografica:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for country, w in sorted(adv['country_breakdown'].items(), key=lambda x: -x[1]):
            pdf.cell(0, 6, f"  {country}: {w*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # --- SEZIONE 6: COMPOSIZIONE PER ASSET CLASS ---
    _section_title(pdf, "6. Composizione per Classe di Asset")
    pdf.set_font("Helvetica", "", 11)

    class_weights: Dict[str, float] = {}
    for ticker, weight in portfolio_weights.items():
        asset_class = classify_asset(ticker)
        class_weights[asset_class] = class_weights.get(asset_class, 0.0) + weight

    for asset_class, weight in sorted(class_weights.items(), key=lambda x: -x[1]):
        pdf.cell(0, 7, f"  {asset_class}: {weight*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- SEZIONE 7: DETTAGLIO RISCHIO PER SINGOLO ASSET ---
    _section_title(pdf, "7. Rischiosita' Individuale degli Asset")
    pdf.set_font("Helvetica", "", 10)

    # Table header
    _table_row(pdf, ["Ticker", "Peso", "Classe", "Vol. Annua", "Rischio"], bold=True)

    individual_vols = vol_analysis.get('individual_volatilities', {})
    for ticker, weight in portfolio_weights.items():
        vol = individual_vols.get(ticker, 0.0)
        asset_class = classify_asset(ticker)
        risk_label = volatility_to_risk_label(vol)
        _table_row(pdf, [
            ticker,
            f"{weight*100:.1f}%",
            asset_class,
            f"{vol*100:.1f}%",
            risk_label
        ])

    # --- DISCLAIMER ---
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4,
        "Disclaimer: Questo report e' generato automaticamente dal motore RiskAlign a scopo informativo. "
        "Non costituisce consulenza finanziaria personalizzata. Le performance passate non sono indicative "
        "di risultati futuri. Il VaR e' una misura statistica e non rappresenta la perdita massima possibile."
    )

    if quant.get('dropped_tickers'):
        pdf.ln(3)
        dropped = ', '.join(quant['dropped_tickers'])
        pdf.multi_cell(0, 4,
            f"Nota: I seguenti ticker sono stati esclusi dall'analisi per mancanza di dati storici: {dropped}. "
            "I pesi sono stati ricalcolati di conseguenza."
        )

    return bytes(pdf.output())


def _section_title(pdf: FPDF, title: str):
    """Render a section title with underline."""
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(50, 50, 50)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
    pdf.ln(3)


def _table_row(pdf: FPDF, cells: list, bold: bool = False):
    """Render a simple table row."""
    pdf.set_font("Helvetica", "B" if bold else "", 10)
    col_widths = [35, 20, 35, 30, 30]
    for i, cell in enumerate(cells):
        pdf.cell(col_widths[i], 6, cell, border=1, align="C")
    pdf.ln()
