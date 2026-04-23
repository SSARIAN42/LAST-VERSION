import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ========== PALETTE ==========
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
ORANGE    = "#e65100"
YELLOW    = "#f9a825"

# ========== CSS ==========
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
section[data-testid="stSidebar"] .stMultiSelect > div > div {{
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

h1, h2, h3 {{
    font-family: 'Inter', sans-serif;
    color: {TEXT_MAIN};
    font-weight: 600;
}}
.stSelectbox > div > div {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 3px;
}}
.stSlider > div {{ color: {TEXT_MAIN}; }}

div[data-testid="stExpander"] {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 3px;
    margin: 1px 0;
}}
div[data-testid="stExpander"] summary {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.80rem;
    color: {TEXT_MAIN};
    padding: 0.35rem 0.7rem;
}}

[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    color: {BLUE};
    font-weight: 600;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.7rem;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.5px;
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

.result-header {{
    display: grid;
    grid-template-columns: 2.5fr 1fr 1.2fr 1fr;
    gap: 4px;
    padding: 0.35rem 0.7rem;
    background-color: {BG_PANEL};
    border-top: 2px solid {BLUE};
    border-bottom: 1px solid {GRID_C};
    font-size: 0.68rem;
    font-weight: 700;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1px;
}}

.stAlert {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 3px;
}}
hr {{ border-color: {GRID_C}; margin: 0.4rem 0; }}
</style>
""", unsafe_allow_html=True)

# ========== CONSTANTES ==========
FILE_PATH = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\1. SWAP\SWAP_XCCY_and_SINGLE_Data_Only.xlsm'
CURRENCIES = ['EUR6', 'EUR-OIS', 'USD', 'GBP', 'AUD6', 'NZD', 'CHF', 'CAD', 'JPY', 'SEK', 'NOK']

LOOKBACK_MAP      = {'1M': 21, '3M': 63, '6M': 126, '1Y': 252, '2Y': 504, '5Y': 1260}
CHART_HORIZON_MAP = {'1M': 21, '3M': 63, '6M': 126, '1Y': 252, '2Y': 504, '5Y': 1260, '10Y': 2520}

# ========== CTA SIGNAL PARAMS (fixes) ==========
RSI_PARAMS    = [(14, 0.25), (30, 0.25), (60, 0.50)]
ZSCORE_PARAMS = [(20, 0.15), (60, 0.30), (120, 0.30), (250, 0.25)]
ZSCORE_CAP    = 2.5
WEIGHT_RSI    = 0.30
WEIGHT_Z      = 0.70
SMOOTH_SPAN   = 4
MA_WINDOW     = 10
EXTREME_PCT   = 99

# ========== CHARGEMENT CCY ==========
@st.cache_data
def load_ccy_data(ccy_name):
    try:
        df_raw = pd.read_excel(FILE_PATH, sheet_name=ccy_name, engine='openpyxl', header=1)
        date_col = df_raw.columns[0]
        df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, errors='coerce')
        df_raw = df_raw.dropna(subset=[date_col])
        data_cols = []
        for i in range(1, len(df_raw.columns)):
            col_name = df_raw.columns[i]
            if pd.notna(col_name) and str(col_name).strip() != '':
                data_cols.append(col_name)
            else:
                break
        if not data_cols:
            return None
        df = df_raw[[date_col] + data_cols].copy().rename(columns={date_col: 'Date'})
        for col in data_cols:
            df[col] = df[col] * 100
        return df
    except Exception as e:
        st.error(f"Error loading {ccy_name}: {e}")
        return None

# ========== CHARGEMENT REGRESSEURS ==========
@st.cache_data
def load_regressors():
    try:
        df_raw      = pd.read_excel(FILE_PATH, sheet_name='REGRESSOR', engine='openpyxl', header=None)
        groups_row  = df_raw.iloc[1]
        tickers_row = df_raw.iloc[2]
        df_data     = df_raw.iloc[4:].reset_index(drop=True)
        dates       = pd.to_datetime(df_data.iloc[:, 0], dayfirst=True, errors='coerce')
        groups_dict = {}
        for col_idx in range(1, len(groups_row)):
            group  = str(groups_row.iloc[col_idx]).strip()
            ticker = str(tickers_row.iloc[col_idx]).strip()
            if group == 'nan' or ticker == 'nan':
                continue
            if group not in groups_dict:
                groups_dict[group] = {}
            series    = pd.to_numeric(df_data.iloc[:, col_idx], errors='coerce')
            df_series = pd.DataFrame({'Date': dates, ticker: series}).dropna()
            groups_dict[group][ticker] = df_series
        return groups_dict
    except Exception as e:
        st.error(f"Error loading REGRESSOR: {e}")
        return None

# ========== STRUCTURE ==========
def compute_structure(df_ccy, stype, w1, belly, w2):
    if stype == 'Outright':
        vals = df_ccy[belly].values
    elif stype == 'Curve':
        vals = df_ccy[belly].values - df_ccy[w1].values
    else:
        vals = 2*df_ccy[belly].values - df_ccy[w1].values - df_ccy[w2].values
    return pd.DataFrame({'Date': df_ccy['Date'].values, 'Value': vals})

# ========== OLS ==========
def run_ols(y_series, x_series, lookback_days):
    merged = pd.merge(y_series, x_series, on='Date', suffixes=('_y', '_x'))
    merged = merged.dropna().sort_values('Date').reset_index(drop=True)
    if len(merged) < 10:
        return None
    merged = merged.tail(lookback_days).reset_index(drop=True)
    if len(merged) < 10:
        return None
    y     = merged.iloc[:, 1].values
    x     = merged.iloc[:, 2].values
    dates = merged['Date'].values
    slope, intercept, r_value, _, _ = stats.linregress(x, y)
    r2        = r_value ** 2
    residuals = y - (slope * x + intercept)
    corr_252  = np.corrcoef(
        merged.iloc[-252:, 1].values,
        merged.iloc[-252:, 2].values
    )[0, 1] if len(merged) >= 252 else np.corrcoef(y, x)[0, 1]
    return {
        'r2': r2, 'beta': slope, 'alpha': intercept,
        'residuals': residuals, 'y': y, 'x': x,
        'dates': dates, 'corr_252': corr_252, 'n': len(merged)
    }

# ========== CTA SIGNAL ==========
def compute_rsi(s, w):
    d  = s.diff()
    g  = d.clip(lower=0).rolling(w).mean()
    l  = -d.clip(upper=0).rolling(w).mean()
    rs = g / l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_composite_score(series):
    rsi_score  = sum(compute_rsi(series, w) * p for w, p in RSI_PARAMS)
    z_weighted = sum(
        ((series - series.rolling(w).mean()) /
         series.rolling(w).std().replace(0, np.nan)).clip(-ZSCORE_CAP, ZSCORE_CAP) * p
        for w, p in ZSCORE_PARAMS
    )
    rsi_c = ((rsi_score - 50) / 25).clip(-2, 2)
    z_c   = ((z_weighted / ZSCORE_CAP) * 2).clip(-2, 2)
    raw   = WEIGHT_RSI * rsi_c + WEIGHT_Z * z_c
    score = raw.ewm(span=SMOOTH_SPAN, adjust=False).mean().clip(-2, 2)
    ma    = score.rolling(MA_WINDOW).mean()
    clean = score.dropna()
    upper = np.percentile(clean, EXTREME_PCT)     if len(clean) > 0 else  2.0
    lower = np.percentile(clean, 100-EXTREME_PCT) if len(clean) > 0 else -2.0
    return score, ma, upper, lower

# ========== PLOTLY — NIVEAU + COMPOSITE SCORE (Bloomberg light style) ==========
def plot_structure_with_signal(dep_series, dep_title, horizon_days):
    dep_s = dep_series.sort_values('Date').reset_index(drop=True)

    series_ts = dep_s.set_index('Date')['Value']
    score, score_ma, up, lo = compute_composite_score(series_ts)

    plot_start = score.first_valid_index() or series_ts.index[0]

    s_plot  = series_ts.loc[plot_start:].tail(horizon_days)
    sc_plot = score.loc[plot_start:].tail(horizon_days)
    sc_ma   = score_ma.loc[plot_start:].tail(horizon_days)

    if len(s_plot) == 0 or len(sc_plot) == 0:
        return go.Figure()

    # Palette
    BG_PAPER     = "#ffffff"
    BG_PLOT      = "#f7f9fc"
    LINE_LVL     = "#1565c0"
    LINE_SC      = "#1e88e5"
    LINE_MA      = "#90a4ae"
    RED_PLT      = "#d32f2f"
    GREEN_PLT    = "#00875a"
    GRID_PLT     = "rgba(26,42,58,0.08)"
    ZERO_LINE    = "rgba(26,42,58,0.18)"
    TEXT_PLT     = "#1a2a3a"
    TEXT_MUTED_P = "#6b7c93"
    BORDER_AX    = "rgba(26,42,58,0.14)"

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.58, 0.42],
        vertical_spacing=0.10,
        subplot_titles=(
            f"{dep_title} — Level",
            "Composite Score"
        )
    )

    # =========================
    # Panel 1 : Level
    # =========================
    fig.add_trace(
        go.Scatter(
            x=s_plot.index,
            y=s_plot.values,
            mode="lines",
            line=dict(color=LINE_LVL, width=2),
            name="Level",
            showlegend=False,
            hovertemplate="%{x|%d %b %Y}<br>Level: %{y:.2f} bp<extra></extra>"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=[s_plot.index[-1]],
            y=[s_plot.values[-1]],
            mode="markers+text",
            marker=dict(
                color=LINE_LVL,
                size=8,
                symbol="circle",
                line=dict(color="white", width=1.5)
            ),
            text=[f"{s_plot.values[-1]:.2f}"],
            textposition="middle right",
            textfont=dict(size=10, color=LINE_LVL, family="Inter, Arial"),
            showlegend=False,
            hoverinfo="skip"
        ),
        row=1, col=1
    )

    # =========================
    # Panel 2 : Composite Score
    # =========================
    sc_arr = sc_plot.values
    dates_sc = sc_plot.index

    pos_fill = np.where(sc_arr >= 0, sc_arr, 0)
    neg_fill = np.where(sc_arr < 0, sc_arr, 0)

    fig.add_trace(
        go.Scatter(
            x=dates_sc,
            y=pos_fill,
            fill="tozeroy",
            fillcolor="rgba(30,136,229,0.12)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=dates_sc,
            y=neg_fill,
            fill="tozeroy",
            fillcolor="rgba(211,47,47,0.10)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=dates_sc,
            y=sc_arr,
            mode="lines",
            line=dict(color=LINE_SC, width=2),
            name="Composite Score",
            hovertemplate="%{x|%d %b %Y}<br>Score: %{y:.2f}<extra></extra>"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=sc_ma.index,
            y=sc_ma.values,
            mode="lines",
            line=dict(color=LINE_MA, width=1.3, dash="dot"),
            name=f"MA({MA_WINDOW})",
            hovertemplate="%{x|%d %b %Y}<br>MA: %{y:.2f}<extra></extra>"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=[dates_sc[0], dates_sc[-1]],
            y=[up, up],
            mode="lines",
            line=dict(color=RED_PLT, width=1.2, dash="dash"),
            name=f"Extreme High ({up:.2f})",
            hoverinfo="skip"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=[dates_sc[0], dates_sc[-1]],
            y=[lo, lo],
            mode="lines",
            line=dict(color=GREEN_PLT, width=1.2, dash="dash"),
            name=f"Extreme Low ({lo:.2f})",
            hoverinfo="skip"
        ),
        row=2, col=1
    )

    fig.add_hline(
        y=0,
        line=dict(color=ZERO_LINE, width=1, dash="dot"),
        row=2, col=1
    )

    # =========================
    # Layout
    # =========================
    fig.update_layout(
        height=840,
        paper_bgcolor=BG_PAPER,
        plot_bgcolor=BG_PLOT,
        font=dict(
            family="Inter, Arial, sans-serif",
            size=10,
            color=TEXT_PLT
        ),
        margin=dict(l=55, r=55, t=70, b=55),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(size=9, color=TEXT_MUTED_P),
            bgcolor="rgba(255,255,255,0.65)",
            bordercolor="rgba(0,0,0,0)",
            traceorder="normal"
        ),
        hovermode="x unified"
    )

    axis_style = dict(
        showgrid=True,
        gridcolor=GRID_PLT,
        gridwidth=0.6,
        zeroline=False,
        showline=True,
        linecolor=BORDER_AX,
        linewidth=1,
        tickfont=dict(size=9, color=TEXT_MUTED_P, family="Inter, Arial"),
        title_font=dict(size=10, color=TEXT_MUTED_P, family="Inter, Arial"),
        ticks="outside",
        ticklen=4
    )

    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    fig.update_yaxes(title_text="bps", row=1, col=1)
    fig.update_yaxes(title_text="Score", row=2, col=1, range=[-2.4, 2.4])

    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(tickformat="%b\n%Y", row=2, col=1)

    # Centrer les titres des sous-graphes
    for ann in fig.layout.annotations:
        ann.update(
            x=0.5,
            xanchor="center",
            font=dict(size=13, color=TEXT_PLT, family="Inter, Arial"),
            y=ann.y + 0.01
        )

    return fig

# ========== PLOTLY — SCATTER ==========
def plot_scatter(ols, ticker, dep_title, r2):
    n_total  = len(ols['x'])
    n_recent = min(21, n_total)
    n_old    = n_total - n_recent

    fig = go.Figure()

    if n_old > 0:
        fig.add_trace(go.Scatter(
            x=ols['x'][:n_old], y=ols['y'][:n_old],
            mode='markers',
            marker=dict(color='#2a2a2a', size=4, opacity=0.55),
            name='History',
            showlegend=True
        ))

    if n_recent > 1:
        fig.add_trace(go.Scatter(
            x=ols['x'][n_old:n_total-1], y=ols['y'][n_old:n_total-1],
            mode='markers',
            marker=dict(color=YELLOW, size=5, opacity=0.85),
            name='Last 21d',
            showlegend=True
        ))

    fig.add_trace(go.Scatter(
        x=[ols['x'][-1]], y=[ols['y'][-1]],
        mode='markers+text',
        marker=dict(color='#b71c1c', size=10, symbol='circle',
                    line=dict(color='white', width=1.5)),
        text=[f"  ({ols['x'][-1]:.1f}, {ols['y'][-1]:.1f})"],
        textposition='middle right',
        textfont=dict(size=8, color='#b71c1c'),
        name='Last',
        showlegend=True
    ))

    x_line = np.linspace(ols['x'].min(), ols['x'].max(), 200)
    y_line = ols['beta'] * x_line + ols['alpha']
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        line=dict(color=BLUE, width=1.4, dash='dash'),
        name=f"β={ols['beta']:.3f}  R²={r2:.3f}",
        showlegend=True
    ))

    fig.update_layout(
        height=340,
        paper_bgcolor=BG_MAIN,
        plot_bgcolor=BG_PANEL,
        font=dict(family='Inter', size=9, color=TEXT_MAIN),
        margin=dict(l=50, r=20, t=28, b=40),
        title=dict(text='Scatter', font=dict(size=10, color=TEXT_MUTED), x=0),
        legend=dict(font=dict(size=8), bgcolor='rgba(0,0,0,0)',
                    bordercolor=GRID_C, orientation='h', x=0, y=-0.18),
        xaxis_title=ticker,
        yaxis_title=dep_title,
        hovermode=False
    )
    axis_s = dict(showgrid=True, gridcolor=GRID_C, gridwidth=0.5,
                  zeroline=False, linecolor=GRID_C,
                  tickfont=dict(size=8, color=TEXT_MUTED),
                  title_font=dict(size=8.5, color=TEXT_MUTED))
    fig.update_xaxes(**axis_s)
    fig.update_yaxes(**axis_s)
    return fig

# ========== PLOTLY — RESIDUS ==========
def plot_residuals(ols):
    dates_r   = pd.to_datetime(ols['dates'])
    residuals = ols['residuals']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates_r, y=np.where(residuals >= 0, residuals, 0),
        fill='tozeroy', fillcolor='rgba(211,47,47,0.10)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=dates_r, y=np.where(residuals < 0, residuals, 0),
        fill='tozeroy', fillcolor='rgba(0,135,90,0.10)',
        line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=dates_r, y=residuals,
        mode='lines',
        line=dict(color=BLUE2, width=1.3),
        name='Residuals',
        showlegend=False
    ))

    fig.add_hline(y=0, line=dict(color=GRID_C, width=0.8, dash='dot'))

    fig.add_trace(go.Scatter(
        x=[dates_r[-1]], y=[residuals[-1]],
        mode='markers+text',
        marker=dict(color='#b71c1c', size=8,
                    line=dict(color='white', width=1.2)),
        text=[f"  {residuals[-1]:+.2f}"],
        textposition='middle right',
        textfont=dict(size=8.5, color='#b71c1c', family='JetBrains Mono'),
        showlegend=False
    ))

    fig.update_layout(
        height=340,
        paper_bgcolor=BG_MAIN,
        plot_bgcolor=BG_PANEL,
        font=dict(family='Inter', size=9, color=TEXT_MAIN),
        margin=dict(l=50, r=60, t=28, b=40),
        title=dict(text='Residuals', font=dict(size=10, color=TEXT_MUTED), x=0),
        hovermode=False
    )
    axis_s = dict(showgrid=True, gridcolor=GRID_C, gridwidth=0.5,
                  zeroline=False, linecolor=GRID_C,
                  tickfont=dict(size=8, color=TEXT_MUTED),
                  title_font=dict(size=8.5, color=TEXT_MUTED))
    fig.update_xaxes(**axis_s, tickangle=-35)
    fig.update_yaxes(**axis_s, title_text='Residuals (bp)')
    return fig

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown(f"<div style='color:{ACCENT};font-size:0.68rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>REGRESSION CONFIGURATION</div>", unsafe_allow_html=True)

    dep_type = st.selectbox("Dependent Type", ['Single CCY', 'XMkt'], index=['Single CCY', 'XMkt'].index(st.session_state.get('reg_dep_type', 'Single CCY')), key='reg_dep_type')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>STRUCTURE 1</div>", unsafe_allow_html=True)
    ccy1         = st.selectbox("CCY", CURRENCIES, key='reg_ccy1')
    struct_type1 = st.selectbox("Type", ['Outright', 'Curve', 'Fly'], key='reg_struct_type1')
    df_ccy1      = load_ccy_data(ccy1)
    instruments1 = list(df_ccy1.columns[1:]) if df_ccy1 is not None else []
    wing1_1      = st.selectbox("Wing 1", instruments1, key='reg_wing1_1')
    belly_1      = st.selectbox("Belly",  instruments1, index=min(5,  len(instruments1)-1), key='reg_belly_1')
    wing2_1      = st.selectbox("Wing 2", instruments1, index=min(10, len(instruments1)-1), key='reg_wing2_1')

    if dep_type == 'XMkt':
        st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>STRUCTURE 2</div>", unsafe_allow_html=True)
        ccy2         = st.selectbox("CCY 2", CURRENCIES, index=1, key='reg_ccy2')
        struct_type2 = st.selectbox("Type 2", ['Outright', 'Curve', 'Fly'], key='reg_struct_type2')
        df_ccy2      = load_ccy_data(ccy2)
        instruments2 = list(df_ccy2.columns[1:]) if df_ccy2 is not None else []
        wing1_2      = st.selectbox("Wing 1 (2)", instruments2, key='reg_wing1_2')
        belly_2      = st.selectbox("Belly (2)",  instruments2, index=min(5,  len(instruments2)-1), key='reg_belly_2')
        wing2_2      = st.selectbox("Wing 2 (2)", instruments2, index=min(10, len(instruments2)-1), key='reg_wing2_2')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>PARAMETERS</div>", unsafe_allow_html=True)
    col_lb, col_hz = st.columns(2)
    with col_lb:
        _lb_keys = list(LOOKBACK_MAP.keys()); lookback_reg = st.selectbox("Lookback", _lb_keys, index=_lb_keys.index(st.session_state.get('reg_lookback_reg', '6M')) if st.session_state.get('reg_lookback_reg') in _lb_keys else 2, key='reg_lookback_reg')
    with col_hz:
        _ch_keys = list(CHART_HORIZON_MAP.keys()); chart_horizon = st.selectbox("Horizon", _ch_keys, index=_ch_keys.index(st.session_state.get('reg_chart_horizon', '1Y')) if st.session_state.get('reg_chart_horizon') in _ch_keys else 3, key='reg_chart_horizon')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>REGRESSORS</div>", unsafe_allow_html=True)
    groups_dict = load_regressors()
    if groups_dict:
        available_groups = list(groups_dict.keys())
        selected_groups  = st.multiselect("Groups", available_groups,
                                          default=available_groups[:1],
                                          key='reg_selected_groups')
    else:
        selected_groups = []
        st.error("Cannot load REGRESSOR sheet")

    st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)
    run_button = st.button("▶  RUN REGRESSIONS", use_container_width=True)

# ========== TITRE ==========
if dep_type == 'Single CCY':
    dep_title = (belly_1 if struct_type1 == 'Outright'
                 else f"{wing1_1}/{belly_1}" if struct_type1 == 'Curve'
                 else f"{wing1_1}/{belly_1}/{wing2_1}")
    dep_title = f"{ccy1}  {dep_title}"
else:
    t1 = (belly_1 if struct_type1 == 'Outright'
          else f"{wing1_1}/{belly_1}" if struct_type1 == 'Curve'
          else f"{wing1_1}/{belly_1}/{wing2_1}")
    t2 = (belly_2 if struct_type2 == 'Outright'
          else f"{wing1_2}/{belly_2}" if struct_type2 == 'Curve'
          else f"{wing1_2}/{belly_2}/{wing2_2}")
    dep_title = f"{ccy1} {t1}  —  {ccy2} {t2}"

st.markdown(f"<div class='header-bar'><h2>{dep_title}</h2></div>", unsafe_allow_html=True)

# ========== GRAPHIQUE NIVEAU + SIGNAL ==========
if df_ccy1 is not None:
    struct1 = compute_structure(df_ccy1, struct_type1, wing1_1, belly_1, wing2_1)

    if dep_type == 'XMkt' and df_ccy2 is not None:
        struct2    = compute_structure(df_ccy2, struct_type2, wing1_2, belly_2, wing2_2)
        merged_dep = pd.merge(struct1, struct2, on='Date', suffixes=('_1','_2')).dropna()
        merged_dep['Value'] = merged_dep['Value_1'] - merged_dep['Value_2']
        dep_series = merged_dep[['Date','Value']].copy()
    else:
        dep_series = struct1.copy()

    dep_series   = dep_series.sort_values('Date').reset_index(drop=True)
    horizon_days = CHART_HORIZON_MAP[chart_horizon]

    fig_main = plot_structure_with_signal(dep_series, dep_title, horizon_days)
    st.plotly_chart(fig_main, use_container_width=True, config={'displayModeBar': False})

# ========== REGRESSIONS ==========
if run_button:
    if not selected_groups:
        st.warning("Select at least one regressor group.")
    elif df_ccy1 is None:
        st.error("Cannot load currency data.")
    else:
        lookback_days = LOOKBACK_MAP[lookback_reg]

        struct1 = compute_structure(df_ccy1, struct_type1, wing1_1, belly_1, wing2_1)
        if dep_type == 'XMkt' and df_ccy2 is not None:
            struct2    = compute_structure(df_ccy2, struct_type2, wing1_2, belly_2, wing2_2)
            merged_dep = pd.merge(struct1, struct2, on='Date', suffixes=('_1','_2')).dropna()
            merged_dep['Value'] = merged_dep['Value_1'] - merged_dep['Value_2']
            dep_series_reg = merged_dep[['Date','Value']].rename(columns={'Value':'Y'})
        else:
            dep_series_reg = struct1.rename(columns={'Value':'Y'})

        all_regressors = [
            {'ticker': ticker, 'data': df_t.rename(columns={ticker: 'X'})}
            for grp in selected_groups if grp in groups_dict
            for ticker, df_t in groups_dict[grp].items()
        ]

        if not all_regressors:
            st.warning("No regressors in selected groups.")
        else:
            results  = []
            total    = len(all_regressors)
            prog_bar = st.progress(0, text=f"Running {total} regressions...")

            for i, reg in enumerate(all_regressors):
                ols = run_ols(dep_series_reg, reg['data'], lookback_days)
                if ols is not None:
                    results.append({
                        'ticker':        reg['ticker'],
                        'r2':            ols['r2'],
                        'corr_252':      ols['corr_252'],
                        'last_residual': ols['residuals'][-1],
                        'ols_result':    ols
                    })
                prog_bar.progress((i+1)/total, text=f"{i+1}/{total} regressions")

            prog_bar.empty()
            results = sorted(results, key=lambda x: x['r2'], reverse=True)
            st.session_state['reg_reg_results'] = results
            st.session_state['reg_dep_title']   = dep_title

# ========== RÉSULTATS ==========
if 'reg_reg_results' in st.session_state:
    results   = st.session_state['reg_reg_results']
    dep_title = st.session_state.get('reg_dep_title', dep_title)

    st.markdown(f"<div class='header-bar' style='margin-top:1.5rem'><h2>RESULTS — {len(results)} models · {lookback_reg} lookback</h2></div>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        min_r2 = st.slider("Min R²", 0.0, 1.0, 0.0, 0.01, key='reg_r2_filter')

    filtered = [r for r in results if r['r2'] >= min_r2]
    st.markdown(f"<div style='color:{TEXT_MUTED};font-size:0.72rem;margin-bottom:6px;font-family:JetBrains Mono,monospace;'>{len(filtered)} regressors · R² ≥ {min_r2:.2f}</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='result-header'>
        <span>TICKER</span><span>R²</span><span>LAST RESID (bp)</span><span>CORR 252d</span>
    </div>
    """, unsafe_allow_html=True)

    for res in filtered:
        with st.expander(
            f"{res['ticker']:<26}  "
            f"R² {res['r2']:.3f}   |   "
            f"Resid {res['last_residual']:+.2f} bp   |   "
            f"Corr {res['corr_252']:+.3f}"
        ):
            ols = res['ols_result']

            c_scatter, c_resid = st.columns(2)
            with c_scatter:
                fig_s = plot_scatter(ols, res['ticker'], dep_title, res['r2'])
                st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
            with c_resid:
                fig_r = plot_residuals(ols)
                st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("R²",            f"{res['r2']:.4f}")
            m2.metric("Beta",          f"{ols['beta']:.4f}")
            m3.metric("Last Residual", f"{ols['residuals'][-1]:+.2f} bp")
            m4.metric("Corr 252d",     f"{res['corr_252']:+.3f}")

st.markdown(f"<div style='border-top:1px solid {GRID_C};margin-top:2rem;padding-top:0.5rem;text-align:center;color:{TEXT_MUTED};font-size:0.7rem;font-family:Inter,sans-serif;'>© 2026 — Regression Analysis</div>", unsafe_allow_html=True)
