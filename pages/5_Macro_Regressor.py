import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Import screener engine
sys.path.insert(0, os.path.dirname(__file__))
from screener_engine import (
    run_screener_part1,
    run_regression_vs_macro,
    load_macro_sheet,
    get_display_cols,
    get_windows,
    LOOKBACK_MAP,
)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE
# ─────────────────────────────────────────────────────────────────────────────
SIDEBAR_BG   = "#0a1628"
SIDEBAR_PAN  = "#0f2040"
ACCENT       = "#00aaff"
TEXT_SIDE    = "#e8f4fd"
TEXT_MUTED_S = "#7a9cc0"
GRID_S       = "#1a3a5c"

BG_MAIN   = "#ffffff"
BG_PANEL  = "#f4f7fb"
TEXT_MAIN = "#1a2a3a"
TEXT_MUTED= "#6b7c93"
GRID_C    = "#e2e8f0"
BLUE      = "#1a6fbd"
BLUE2     = "#2196f3"
GREEN     = "#00875a"
RED       = "#d32f2f"
YELLOW    = "#f9a825"

CURRENCIES = ['EUR6', 'ESTR', 'USD', 'GBP', 'AUD6', 'NZD', 'CHF', 'CAD', 'JPY', 'SEK', 'NOK']
LOOKBACKS  = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '10Y']

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG_MAIN};
    color: {TEXT_MAIN};
}}
.stApp {{ background-color: {BG_MAIN}; }}

section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG};
    border-right: 1px solid {GRID_S};
}}
section[data-testid="stSidebar"] * {{ color: {TEXT_SIDE} !important; }}
section[data-testid="stSidebar"] .stSelectbox > div > div {{
    background-color: {SIDEBAR_PAN};
    border: 1px solid {GRID_S};
    border-radius: 3px;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background-color: {ACCENT};
    color: {SIDEBAR_BG};
    border: none;
    border-radius: 3px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    width: 100%;
    padding: 0.5rem;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: #33bbff;
    box-shadow: 0 0 10px rgba(0,170,255,0.4);
}}
.header-bar {{
    background-color: {BG_PANEL};
    border-left: 3px solid {BLUE};
    padding: 0.5rem 0.9rem;
    margin-bottom: 0.8rem;
    border-radius: 0 3px 3px 0;
    border-top: 1px solid {GRID_C};
    border-bottom: 1px solid {GRID_C};
    border-right: 1px solid {GRID_C};
}}
.header-bar h2 {{
    margin: 0;
    font-size: 0.95rem;
    color: {BLUE};
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}}
.section-title {{
    background-color: {BG_PANEL};
    border-left: 3px solid {BLUE};
    border-top: 1px solid {GRID_C};
    border-bottom: 1px solid {GRID_C};
    border-right: 1px solid {GRID_C};
    padding: 0.35rem 0.7rem;
    margin: 1rem 0 0.4rem 0;
    border-radius: 0 3px 3px 0;
    font-size: 0.72rem;
    font-weight: 700;
    color: {BLUE};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
hr {{ border-color: {GRID_C}; margin: 0.4rem 0; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
for key, val in [
    ('scr_results',      None),
    ('scr_ccys',         ['EUR6']),
    ('scr_lookback',     '1Y'),
    ('scr_macro_asset',  None),
    ('scr_run_done',     False),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT MACRO
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def get_macro_assets():
    try:
        df = load_macro_sheet()
        return list(df.columns), df
    except Exception as e:
        st.error(f"Impossible de charger la feuille MACRO : {e}")
        return [], pd.DataFrame()

macro_assets, df_macro = get_macro_assets()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='color:{ACCENT};font-size:0.68rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>RELATIVE VALUE SCREENER</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:8px 0 4px;'>CURRENCY</div>", unsafe_allow_html=True)

    selected_ccys = st.multiselect(
        "CCY",
        CURRENCIES,
        default=st.session_state['scr_ccys'],
        key='scr_ccys',
        label_visibility='collapsed'
    )

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>LOOKBACK RÉGRESSION</div>", unsafe_allow_html=True)
    selected_lb = st.selectbox("Lookback", LOOKBACKS,
                               index=LOOKBACKS.index(st.session_state.get('scr_lookback', '1Y')),
                               key='scr_lookback', label_visibility='collapsed')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>MACRO ASSET</div>", unsafe_allow_html=True)
    if macro_assets:
        default_macro = st.session_state.get('scr_macro_asset') or macro_assets[0]
        if default_macro not in macro_assets:
            default_macro = macro_assets[0]
        selected_macro = st.selectbox("Macro", macro_assets,
                                      index=macro_assets.index(default_macro),
                                      key='scr_macro_asset', label_visibility='collapsed')
    else:
        st.error("Feuille MACRO introuvable")
        selected_macro = None

    st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)
    run_button = st.button("▶  RUN SCREENER", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
ccy_title = ", ".join(selected_ccys) if selected_ccys else "—"
title = f"{ccy_title}  ·  {selected_macro or '—'}  ·  {selected_lb}"
st.markdown(f"<div class='header-bar'><h2>Relative Value Screener — {title}</h2></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────
if run_button and selected_macro and selected_ccys:
    progress = st.progress(0, text="Chargement des structures...")

    try:
        macro_series = df_macro[selected_macro].dropna()
        all_results = []

        total_ccy = len(selected_ccys)

        for j, ccy in enumerate(selected_ccys, start=1):

            def prog_cb(current, total, ccy=ccy, j=j):
                base = int((j - 1) / total_ccy * 100)
                span = int(1 / total_ccy * 100)
                inner_pct = int(current / total * span) if total > 0 else 0
                pct = min(base + inner_pct, 99)
                progress.progress(pct, text=f"{ccy} — Structure {current}/{total}...")

            df_part1 = run_screener_part1(ccy, selected_lb, progress_callback=prog_cb)

            if df_part1.empty:
                continue

            df_full_ccy = run_regression_vs_macro(df_part1, macro_series, selected_lb)

            all_results.append(df_full_ccy)

        progress.progress(100, text="Terminé !")
        progress.empty()

        if all_results:
            df_full = pd.concat(all_results, ignore_index=True)
            st.session_state['scr_results'] = df_full
            st.session_state['scr_run_done'] = True
            st.success(f"✅ {len(df_full)} structures calculées pour {', '.join(selected_ccys)}")
        else:
            st.session_state['scr_results'] = None
            st.session_state['scr_run_done'] = False
            st.warning("Aucune structure trouvée pour les CCY sélectionnées.")

    except Exception as e:
        progress.empty()
        st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────────────────────────────────────
# AFFICHAGE RÉSULTATS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state['scr_run_done'] and st.session_state['scr_results'] is not None:

    df_full  = st.session_state['scr_results']
    lb_label = st.session_state['scr_lookback']
    windows  = get_windows(lb_label)

    # ── Colonnes à afficher (sans _series)
    display_cols = get_display_cols(lb_label, with_regression=True)
    display_cols = [c for c in display_cols if c in df_full.columns]

    # ─────────────────────────────────────────────────────────────────────
    # FILTRES
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Filtres</div>", unsafe_allow_html=True)

    # Détecter les colonnes disponibles pour filtres
    resid_z_col   = f"Resid_Z_{lb_label}" if f"Resid_Z_{lb_label}" in df_full.columns else "Resid_Z_1M"
    resid_pct_col = f"Resid_Pct_{lb_label}" if f"Resid_Pct_{lb_label}" in df_full.columns else "Resid_Pct_1M"

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        min_r2 = st.slider("R² minimum", 0.0, 1.0, 0.0, 0.05, key='scr_f_r2')

    with col_f2:
        resid_vals = df_full['Resid_Last'].dropna()
        r_max = float(max(abs(resid_vals.min()), abs(resid_vals.max()))) if len(resid_vals) > 0 else 10.0
        r_max = round(r_max, 1)
        resid_range = st.slider(
            "Résidu last (exclure zone)",
            -r_max, r_max, (-r_max * 0.1, r_max * 0.1), r_max / 50,
            key='scr_f_resid',
            help="Exclut les résidus dans cette plage — garde les extrêmes"
        )

    with col_f3:
        z_vals = df_full[resid_z_col].dropna() if resid_z_col in df_full.columns else pd.Series([])
        z_max = float(max(abs(z_vals.min()), abs(z_vals.max()))) if len(z_vals) > 0 else 3.0
        z_max = min(round(z_max, 1), 5.0)
        z_range = st.slider(
            f"Z-score résidu {lb_label} (exclure zone)",
            -z_max, z_max, (-0.5, 0.5), 0.1,
            key='scr_f_z',
            help="Exclut les z-scores dans cette plage — garde les extrêmes"
        )

    with col_f4:
        corr_range = st.slider(
            "Corr 252j (exclure zone)",
            -1.0, 1.0, (-0.3, 0.3), 0.05,
            key='scr_f_corr',
            help="Exclut les corrélations dans cette plage"
        )

    # ── Appliquer les filtres
    mask = pd.Series([True] * len(df_full), index=df_full.index)

    if 'R2' in df_full.columns:
        mask &= df_full['R2'].fillna(0) >= min_r2

    if 'Resid_Last' in df_full.columns:
        mask &= (
            (df_full['Resid_Last'] < resid_range[0]) |
            (df_full['Resid_Last'] > resid_range[1])
        )

    if resid_z_col in df_full.columns:
        mask &= (
            (df_full[resid_z_col] < z_range[0]) |
            (df_full[resid_z_col] > z_range[1])
        )

    if 'Corr_252d' in df_full.columns:
        mask &= (
            (df_full['Corr_252d'] < corr_range[0]) |
            (df_full['Corr_252d'] > corr_range[1])
        )

    filtered_df = df_full[mask].copy()

    st.markdown(f"<div style='color:{TEXT_MUTED};font-size:0.72rem;margin-bottom:6px;font-family:JetBrains Mono,monospace;'>{len(filtered_df)} structures · R² ≥ {min_r2:.2f}</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # TABLEAU
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Résultats</div>", unsafe_allow_html=True)

    cols_to_show = ['CCY'] + [c for c in display_cols if c in filtered_df.columns and c not in ['CCY', '_series']]

    # Arrondir pour affichage
    df_display = filtered_df[cols_to_show].copy()
    for col in df_display.select_dtypes(include=[np.number]).columns:
        df_display[col] = df_display[col].round(4)

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────────────────────────────
    # BARRE DE RECHERCHE → DÉTAIL
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Analyse détaillée</div>", unsafe_allow_html=True)

    filtered_df = filtered_df.copy()
    filtered_df['Display_Name'] = filtered_df['CCY'] + " | " + filtered_df['Structure']
    
    structure_list = filtered_df['Display_Name'].tolist()
    
    if structure_list:
        selected_struct = st.selectbox(
            "Sélectionner une structure :",
            options=structure_list,
            key='scr_selected_struct'
        )
    
        row = filtered_df[filtered_df['Display_Name'] == selected_struct].iloc[0]
        s   = row.get('_series')

        if s is not None and isinstance(s, pd.Series) and selected_macro and not df_macro.empty:

            macro_s = df_macro[selected_macro].dropna()
            lookback_days = LOOKBACK_MAP.get(lb_label, 252)

            # Aligner
            merged = pd.concat([s.rename('Y'), macro_s.rename('X')], axis=1).dropna()

            # Régression sur lookback
            merged_lb = merged.iloc[-lookback_days:] if len(merged) > lookback_days else merged
            from scipy import stats as sp_stats
            slope, intercept, r_val, _, _ = sp_stats.linregress(
                merged_lb['X'].values, merged_lb['Y'].values
            )
            y_hat  = slope * merged_lb['X'].values + intercept
            resid  = pd.Series(
                merged_lb['Y'].values - y_hat,
                index=merged_lb.index
            )

            # ── Couleurs temporelles pour scatter
            y_all   = merged_lb['Y'].values
            x_all   = merged_lb['X'].values
            dates   = merged_lb.index

            last_date         = dates[-1]
            three_months_ago  = last_date - pd.DateOffset(months=3)
            nine_months_ago   = last_date - pd.DateOffset(months=9)

            mask_old    = dates < nine_months_ago
            mask_green  = (dates >= nine_months_ago) & (dates < three_months_ago)
            mask_yellow = (dates >= three_months_ago) & (dates < last_date)
            mask_last   = dates == last_date

            # ─────────────────────────────────────────────────────────
            # SCATTER + RÉSIDUS
            # ─────────────────────────────────────────────────────────
            col_scatter, col_resid = st.columns(2)

            with col_scatter:
                fig_sc = go.Figure()

                if mask_old.any():
                    fig_sc.add_trace(go.Scatter(
                        x=x_all[mask_old], y=y_all[mask_old],
                        mode='markers',
                        marker=dict(color='#b0bec5', size=4, opacity=0.5),
                        name='Historique (>9m)', showlegend=True
                    ))
                if mask_green.any():
                    fig_sc.add_trace(go.Scatter(
                        x=x_all[mask_green], y=y_all[mask_green],
                        mode='markers',
                        marker=dict(color='#43a047', size=5, opacity=0.75,
                                    line=dict(color='white', width=0.5)),
                        name='9-3 mois', showlegend=True
                    ))
                if mask_yellow.any():
                    fig_sc.add_trace(go.Scatter(
                        x=x_all[mask_yellow], y=y_all[mask_yellow],
                        mode='markers',
                        marker=dict(color=YELLOW, size=5, opacity=0.85,
                                    line=dict(color='white', width=0.5)),
                        name='3 derniers mois', showlegend=True
                    ))
                if mask_last.any():
                    fig_sc.add_trace(go.Scatter(
                        x=x_all[mask_last], y=y_all[mask_last],
                        mode='markers+text',
                        marker=dict(color=RED, size=12, symbol='circle',
                                    line=dict(color='white', width=1.5)),
                        text=[f"  {y_all[mask_last][0]:.2f}"],
                        textposition='middle right',
                        textfont=dict(size=9, color=RED),
                        name='Dernier point', showlegend=True
                    ))

                # Ligne régression
                x_line = np.linspace(x_all.min(), x_all.max(), 200)
                y_line = slope * x_line + intercept
                fig_sc.add_trace(go.Scatter(
                    x=x_line, y=y_line,
                    mode='lines',
                    line=dict(color=BLUE, width=1.4, dash='dash'),
                    name=f"β={slope:.3f}  R²={r_val**2:.3f}",
                    showlegend=True
                ))

                fig_sc.update_layout(
                    height=380,
                    paper_bgcolor=BG_MAIN, plot_bgcolor=BG_PANEL,
                    font=dict(family='Inter', size=9, color=TEXT_MAIN),
                    margin=dict(l=50, r=20, t=30, b=40),
                    title=dict(text=f"Scatter — {row['CCY']} | {row['Structure']} vs {selected_macro}",
                               font=dict(size=10, color=TEXT_MUTED), x=0),
                    legend=dict(font=dict(size=8), bgcolor='rgba(0,0,0,0)',
                                orientation='h', x=0, y=-0.22),
                    xaxis_title=selected_macro,
                    yaxis_title=selected_struct,
                    hovermode=False
                )
                ax = dict(showgrid=True, gridcolor=GRID_C, gridwidth=0.5,
                          zeroline=False, linecolor=GRID_C,
                          tickfont=dict(size=8, color=TEXT_MUTED))
                fig_sc.update_xaxes(**ax)
                fig_sc.update_yaxes(**ax)
                st.plotly_chart(fig_sc, use_container_width=True, config={'displayModeBar': False})

            with col_resid:
                fig_r = go.Figure()

                # Fill pos/neg
                fig_r.add_trace(go.Scatter(
                    x=resid.index, y=[v if v >= 0 else 0 for v in resid.values],
                    fill='tozeroy', fillcolor='rgba(211,47,47,0.08)',
                    line=dict(width=0), showlegend=False, hoverinfo='skip'
                ))
                fig_r.add_trace(go.Scatter(
                    x=resid.index, y=[v if v < 0 else 0 for v in resid.values],
                    fill='tozeroy', fillcolor='rgba(0,135,90,0.08)',
                    line=dict(width=0), showlegend=False, hoverinfo='skip'
                ))

                # Ligne résidus
                fig_r.add_trace(go.Scatter(
                    x=resid.index, y=resid.values,
                    mode='lines',
                    line=dict(color=BLUE2, width=1.3),
                    name='Résidus', showlegend=False
                ))

                # Zéro
                fig_r.add_hline(y=0, line=dict(color=GRID_C, width=0.8, dash='dot'))

                # ±2σ
                mu_r, sd_r = resid.mean(), resid.std()
                fig_r.add_hline(y=mu_r + 2*sd_r,
                                line=dict(color='rgba(211,47,47,0.5)', width=1, dash='dash'))
                fig_r.add_hline(y=mu_r - 2*sd_r,
                                line=dict(color='rgba(211,47,47,0.5)', width=1, dash='dash'))

                # Dernier point annoté
                fig_r.add_trace(go.Scatter(
                    x=[resid.index[-1]], y=[resid.iloc[-1]],
                    mode='markers+text',
                    marker=dict(color=RED, size=8, line=dict(color='white', width=1.2)),
                    text=[f"  {resid.iloc[-1]:+.2f}"],
                    textposition='middle right',
                    textfont=dict(size=8.5, color=RED, family='JetBrains Mono'),
                    showlegend=False
                ))

                fig_r.update_layout(
                    height=380,
                    paper_bgcolor=BG_MAIN, plot_bgcolor=BG_PANEL,
                    font=dict(family='Inter', size=9, color=TEXT_MAIN),
                    margin=dict(l=50, r=60, t=30, b=40),
                    title=dict(text=f"Résidus — {row['CCY']} | {row['Structure']}",
                               font=dict(size=10, color=TEXT_MUTED), x=0),
                    hovermode=False
                )
                ax_r = dict(showgrid=True, gridcolor=GRID_C, gridwidth=0.5,
                            zeroline=False, linecolor=GRID_C,
                            tickfont=dict(size=8, color=TEXT_MUTED))
                fig_r.update_xaxes(**ax_r, tickangle=-35)
                fig_r.update_yaxes(**ax_r, title_text='Résidus (bp)')
                st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})

            # ── Métriques rapides sous les graphiques
            st.markdown("<div class='section-title'>Métriques clés</div>", unsafe_allow_html=True)
            mc = st.columns(6)
            def _m(col, label, val, fmt=".4f"):
                v = f"{val:{fmt}}" if pd.notna(val) else "N/A"
                col.metric(label, v)

            _m(mc[0], "R²",           row.get('R2', np.nan),          ".4f")
            _m(mc[1], "Résidu last",  row.get('Resid_Last', np.nan),  ".2f")
            _m(mc[2], "Carry 3M",     row.get('Carry_3M', np.nan),    ".2f")
            _m(mc[3], "Carry/Vol",    row.get('Carry_Vol', np.nan),   ".3f")
            _m(mc[4], "Half-Life",    row.get('Half_Life', np.nan),   ".1f")
            _m(mc[5], "Corr 252j",    row.get('Corr_252d', np.nan),   ".3f")

        else:
            st.warning("Série non disponible pour cette structure.")

    else:
        st.info("Aucune structure ne correspond aux filtres.")

else:
    if not st.session_state['scr_run_done']:
        st.info("Configurer les paramètres dans la sidebar et cliquer **RUN SCREENER**.")

st.markdown(f"<div style='border-top:1px solid {GRID_C};margin-top:2rem;padding-top:0.5rem;text-align:center;color:{TEXT_MUTED};font-size:0.7rem;font-family:Inter,sans-serif;'>© 2026 — Relative Value Screener</div>", unsafe_allow_html=True)
