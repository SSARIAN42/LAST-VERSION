import streamlit as st
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import numpy as np
from datetime import datetime, timedelta
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
GREEN     = "#00875a"
RED       = "#d32f2f"

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

div[data-testid="stExpander"] {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 3px;
    margin: 1px 0;
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

.metric-card {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 4px;
    padding: 0.6rem 0.9rem;
    margin: 2px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}}
.metric-label {{
    color: {TEXT_MUTED};
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.metric-value {{
    color: {TEXT_MAIN};
    font-weight: 600;
}}
.metric-value.positive {{ color: {GREEN}; }}
.metric-value.negative {{ color: {RED}; }}

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

.backtest-card {{
    background-color: {BG_PANEL};
    border: 1px solid {GRID_C};
    border-radius: 4px;
    padding: 1rem;
    margin: 0.4rem 0;
}}
.backtest-header {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid {GRID_C};
    padding-bottom: 0.4rem;
    margin-bottom: 0.6rem;
}}
.best-badge {{
    background-color: {BLUE};
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
.direction-long {{
    background-color: rgba(0,135,90,0.15);
    color: {GREEN};
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    border: 1px solid {GREEN};
}}
.direction-short {{
    background-color: rgba(211,47,47,0.1);
    color: {RED};
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    border: 1px solid {RED};
}}

hr {{ border-color: {GRID_C}; margin: 0.4rem 0; }}
</style>
""", unsafe_allow_html=True)

# ========== CONSTANTES ==========
FILE_PATH  = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\1. SWAP\SWAP_XCCY_and_SINGLE_Data_Only.xlsm'
CURRENCIES = ['EUR6', 'EUR-OIS', 'USD', 'GBP', 'AUD6', 'NZD', 'CHF', 'CAD', 'JPY', 'SEK', 'NOK']

LOOKBACK_BT_MAP = {
    '6M':  180,
    '1Y':  365,
    '2Y':  730,
    '5Y':  1825,
    'Max': 99999,
}

HORIZONS_CONFIG = {
    "6M": {"window_ma": 20, "multiplier": 2, "lookback": 126, "rsi_period": 14,
           "horizon": 110, "sl_multiplier": 2.5, "ew_multiplier": 3.75},
    "3M": {"window_ma": 20, "multiplier": 2, "lookback": 63,  "rsi_period": 14,
           "horizon": 55,  "sl_multiplier": 2.2, "ew_multiplier": 3.3},
    "1M": {"window_ma": 10, "multiplier": 2, "lookback": 21,  "rsi_period": 14,
           "horizon": 21,  "sl_multiplier": 2.0, "ew_multiplier": 3.0},
}

MR_WEIGHTS_FULL = {
    "1m": 0.08,
    "2m": 0.10,
    "3m": 0.12,
    "6m": 0.15,
    "8m": 0.15,
    "10m": 0.15,
    "1y": 0.15,
    "2y": 0.10
}

ROLL_WINDOWS_FULL = {
    "1m": 21,
    "2m": 42,
    "3m": 63,
    "6m": 126,
    "8m": 168,
    "10m": 210,
    "1y": 252,
    "2y": 504
}

WINDOW_5Y = 5 * 252
WINDOW_6M = 126

DFA_SCALES = np.unique(
    np.logspace(np.log10(10), np.log10(63), 15).astype(int)
)

ZSCORE_WINDOWS = {
    "1m": 21,
    "3m": 63,
    "6m": 126
}
# ========== CHARGEMENT DATA ==========
@st.cache_data
def load_ccy_data(ccy_name):
    try:
        df_raw   = pd.read_excel(FILE_PATH, sheet_name=ccy_name, engine='openpyxl', header=1)
        date_col = df_raw.columns[0]
        df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, errors='coerce')
        df_raw   = df_raw.dropna(subset=[date_col])
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

# ========== STRUCTURE ==========
def compute_structure(df_ccy, stype, w1, belly, w2):
    if stype == 'Outright':
        vals = df_ccy[belly].values
    elif stype == 'Curve':
        vals = df_ccy[belly].values - df_ccy[w1].values
    else:
        vals = 2*df_ccy[belly].values - df_ccy[w1].values - df_ccy[w2].values
    return pd.DataFrame({'Date': df_ccy['Date'].values, 'Value': vals})

# ========== UTILS MÉTRIQUES ==========
def calc_rsi(series, period=14):
    delta     = series.diff()
    up        = delta.clip(lower=0)
    down      = -delta.clip(upper=0)
    roll_up   = up.ewm(alpha=1/period, adjust=False).mean()
    roll_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs        = roll_up / roll_down
    return 100 - (100 / (1 + rs))

def ar1_phi(s, w):
    s2 = s.dropna().iloc[-w:]
    if len(s2) < max(10, w//4): return np.nan
    d   = s2 - s2.mean()
    x   = d.shift(1).dropna()
    y   = d.loc[x.index]
    den = (x**2).sum()
    return (x*y).sum() / den if den != 0 else np.nan

def half_life(phi):
    if pd.isna(phi) or phi <= 0 or phi >= 1: return np.nan
    return -np.log(2) / np.log(phi)

def mr_component(z, hl):
    if pd.isna(z) or pd.isna(hl) or hl <= 0: return np.nan
    return abs(z) / (abs(z) + hl)

def weighted_avg(vals, wts):
    valid = [(v, w) for v, w in zip(vals, wts) if pd.notna(v)]
    if not valid: return np.nan
    tw = sum(w for _, w in valid)
    return sum(v*w for v, w in valid) / tw

def compute_ar1_phi_lookback(s, w):
    s2 = s.dropna().iloc[-w:]
    if len(s2) < max(10, w // 4):
        return np.nan

    x = s2.shift(1).dropna()
    y = s2.loc[x.index]

    x_c = x - x.mean()
    y_c = y - y.mean()

    den = (x_c ** 2).sum()
    return (x_c * y_c).sum() / den if den != 0 else np.nan

def rolling_zscore(series, window):
    mean_ = series.rolling(window).mean()
    std_ = series.rolling(window).std()
    return (series - mean_) / std_

def count_zero_crossings(zscore_series):
    z = zscore_series.dropna()
    if z.empty:
        return np.nan

    signs = np.sign(z)
    signs = signs[signs != 0]

    if len(signs) < 2:
        return 0

    return int((signs.diff().abs() == 2).sum())

def compute_adf_pvalue(series, window):
    sub = series.dropna().iloc[-window:]

    if len(sub) < 20:
        return np.nan

    try:
        return round(adfuller(sub, autolag="AIC", regression="c")[1], 4)
    except Exception:
        return np.nan

def dfa_numpy(x, scales):
    x = np.array(x, dtype=float)

    if len(x) < 10:
        return np.nan

    x = np.cumsum(x - np.mean(x))

    flucts = []
    valid_scales = []

    for n in scales:
        n = int(n)

        if n < 4 or n > len(x) // 2:
            continue

        n_segs = len(x) // n
        if n_segs < 2:
            continue

        rms_list = []

        for i in range(n_segs):
            seg = x[i * n:(i + 1) * n]
            t = np.arange(n)
            coeffs = np.polyfit(t, seg, 1)
            trend = np.polyval(coeffs, t)
            resid = seg - trend
            rms = np.sqrt(np.mean(resid ** 2))
            rms_list.append(rms)

        mean_rms = np.mean(rms_list)
        if np.isfinite(mean_rms) and mean_rms > 0:
            flucts.append(mean_rms)
            valid_scales.append(n)

    if len(valid_scales) < 3:
        return np.nan

    H, _ = np.polyfit(np.log(valid_scales), np.log(flucts), 1)
    return round(H, 4)

def compute_hurst(series, window, scales):
    sub = series.dropna().iloc[-window:].values.astype(float)

    if len(sub) < max(scales) + 1:
        return np.nan

    diff = np.diff(sub)

    if len(diff) < max(scales):
        return np.nan

    try:
        return dfa_numpy(diff, scales)
    except Exception:
        return np.nan

    
# ========== CALCUL MÉTRIQUES ==========
def compute_display_metrics(s):
    last = s.iloc[-1]
    m = {}

    m["Last (bp)"] = round(last, 4)
    m["MA5"] = round(s.rolling(5).mean().iloc[-1], 4)
    m["MA10"] = round(s.rolling(10).mean().iloc[-1], 4)

    # Z-scores affichés
    for lbl, w in [("1m", 21), ("6m", 126)]:
        rm = s.rolling(w).mean().iloc[-1]
        rs = s.rolling(w).std().iloc[-1]
        m[f"Zscore_{lbl}"] = round((last - rm) / rs, 4) if pd.notna(rs) and rs != 0 else np.nan

    # Yield ratios affichés
    for lbl, w in [("1m", 21), ("6m", 126)]:
        mn = s.rolling(w).min().iloc[-1]
        mx = s.rolling(w).max().iloc[-1]
        m[f"YieldRatio_{lbl}"] = round((last - mn) / (mx - mn), 4) if pd.notna(mx) and pd.notna(mn) and mx != mn else np.nan

    # Vol ratio
    sd_3m = s.rolling(63).std().iloc[-1]
    sd_3w = s.rolling(15).std().iloc[-1]
    vol_3m_ann = sd_3m * np.sqrt(252) if pd.notna(sd_3m) else np.nan
    vol_3w_ann = sd_3w * np.sqrt(252) if pd.notna(sd_3w) else np.nan
    m["Vol3w/Vol3m"] = round(vol_3w_ann / vol_3m_ann, 4) if pd.notna(vol_3m_ann) and vol_3m_ann != 0 else np.nan

    # RSI
    m["RSI_14d"] = round(calc_rsi(s, 14).iloc[-1], 4)

    # Bollinger
    ma20 = s.rolling(20).mean()
    std20 = s.rolling(20).std()
    bb_up = ma20 + 2 * std20
    bb_lo = ma20 - 2 * std20
    cur_up = bb_up.iloc[-1]
    cur_lo = bb_lo.iloc[-1]
    m["BB20_Position_%"] = round((last - cur_lo) / (cur_up - cur_lo) * 100, 2) if pd.notna(cur_up) and pd.notna(cur_lo) and cur_up != cur_lo else np.nan

    # ===== MR SCORE VERSION IDENTIQUE AU 2e CODE =====
    mr_components = []
    mr_weights = []

    for lbl, w in ROLL_WINDOWS_FULL.items():
        rolling_mean = s.rolling(w).mean().iloc[-1]
        rolling_std = s.rolling(w).std().iloc[-1]
        zscore = (last - rolling_mean) / rolling_std if pd.notna(rolling_std) and rolling_std != 0 else np.nan

        phi = compute_ar1_phi_lookback(s, w)
        hl = half_life(phi)
        mr_comp = mr_component(zscore, hl)

        m[f"AR1_phi_{lbl}"] = round(phi, 4) if pd.notna(phi) else np.nan
        m[f"HalfLife_{lbl}"] = round(hl, 4) if pd.notna(hl) else np.nan
        m[f"MR_Score_{lbl}"] = round(mr_comp, 4) if pd.notna(mr_comp) else np.nan

        mr_components.append(mr_comp)
        mr_weights.append(MR_WEIGHTS_FULL[lbl])

    m["MR_Score"] = round(weighted_avg(mr_components, mr_weights), 4)

    # ===== ADF =====
    m["ADF_pval_5y"] = compute_adf_pvalue(s, WINDOW_5Y)

    # ===== HURST =====
    m["Hurst_6m"] = compute_hurst(s, WINDOW_6M, DFA_SCALES)

    # ===== CROSSINGS =====
    if len(s.dropna()) >= WINDOW_5Y:
        for lbl, w in ZSCORE_WINDOWS.items():
            z_full = rolling_zscore(s, w)
            z_win = z_full.iloc[-WINDOW_5Y:]
            m[f"crossings_{lbl}"] = count_zero_crossings(z_win)
    else:
        m["crossings_1m"] = np.nan
        m["crossings_3m"] = np.nan
        m["crossings_6m"] = np.nan

    return m

# ========== BACKTEST UTILS ==========
def compute_metrics_horizon(s, config):
    wma = config["window_ma"]; mul = config["multiplier"]
    lb  = config["lookback"];  h   = config["horizon"]

    rsi    = calc_rsi(s, config["rsi_period"])
    ma     = s.rolling(wma, min_periods=wma).mean()
    std    = s.rolling(wma, min_periods=wma).std()
    bb_up  = ma + mul*std; bb_lo = ma - mul*std
    ma_pos = (s - bb_lo) / (bb_up - bb_lo) * 100

    mean_lb = s.rolling(lb).mean()
    std_lb  = s.rolling(lb).std()
    zscore  = (s - mean_lb) / std_lb

    rolling_min = s.rolling(lb).min()
    rolling_max = s.rolling(lb).max()
    yr          = (s - rolling_min) / (rolling_max - rolling_min)

    daily_std  = s.diff().rolling(30).std()
    vol_annual = daily_std * np.sqrt(252)
    vol_horiz  = vol_annual * np.sqrt(h / 252)

    yr_6m  = (s - s.rolling(126).min()) / (s.rolling(126).max() - s.rolling(126).min())
    z6m_lb = s.rolling(126).mean()
    z6m_sd = s.rolling(126).std()
    z6m    = (s - z6m_lb) / z6m_sd

    return pd.DataFrame({
        "Value":         s,
        "RSI":           rsi,
        "MA_Position_%": ma_pos,
        "ZScore":        zscore,
        "YieldRatio":    yr,
        "YieldRatio_6m": yr_6m,
        "ZScore_6m":     z6m,
        "Vol_Horizon":   vol_horiz,
    }, index=s.index)

def group_blocks(indices, values, extreme="max"):
    if len(indices) == 0: return []
    blocks, block = [], [indices[0]]
    for idx in indices[1:]:
        if idx == block[-1]+1: block.append(idx)
        else: blocks.append(block); block = [idx]
    blocks.append(block)
    return [max(b, key=lambda i: values[i]) if extreme=="max"
            else min(b, key=lambda i: values[i]) for b in blocks]

def backtest_single_horizon(s, today_metrics, config, horizon_name, dir_signal='YieldRatio 6M', rr_ratio_target=2):
    horizon = config["horizon"]
    ew_mult = config["ew_multiplier"]

    metrics = compute_metrics_horizon(s, config)
    rewards, risks                 = [], []
    rewards_vol_adj, risks_vol_adj = [], []
    vol_horizons                   = []
    wins, losses                   = 0, 0

    today_position = today_metrics["MA_Position_%"]
    is_short_setup = today_position > 91
    is_long_setup  = today_position < 9

    if dir_signal == 'YieldRatio 6M':
        is_short_dir = today_metrics["YieldRatio_6m"] > 0.5
    elif dir_signal == 'BB MA20':
        is_short_dir = today_metrics["MA_Position_%"] > 50
    else:
        z6m = today_metrics.get("ZScore_6m", np.nan)
        is_short_dir = z6m > 0 if not np.isnan(z6m) else today_metrics["MA_Position_%"] > 50

    if is_short_setup:
        cond = ((metrics["RSI"] > 60) & (metrics["YieldRatio"] > 0.95) &
                (metrics["ZScore"] > 2) & (metrics["MA_Position_%"] > 95))
        indices = group_blocks(np.where(cond)[0], metrics["MA_Position_%"].values, "max")
    elif is_long_setup:
        cond = ((metrics["RSI"] < 40) & (metrics["YieldRatio"] < 0.05) &
                (metrics["ZScore"] < -2) & (metrics["MA_Position_%"] < 5))
        indices = group_blocks(np.where(cond)[0], metrics["MA_Position_%"].values, "min")
    else:
        cond = ((metrics["RSI"]           >= today_metrics["RSI"]) &
                (metrics["YieldRatio"]    >= today_metrics["YieldRatio"]) &
                (metrics["ZScore"]        >= today_metrics["ZScore"]) &
                (metrics["MA_Position_%"] >= today_metrics["MA_Position_%"]))
        indices = group_blocks(np.where(cond)[0], metrics["MA_Position_%"].values, "max")

    for i in indices:
        if i + horizon >= len(metrics): continue
        entry  = metrics["Value"].iloc[i]
        vol_h  = metrics["Vol_Horizon"].iloc[i]
        future = metrics["Value"].iloc[i+1:i+1+horizon]
        if np.isnan(vol_h) or vol_h <= 0: continue

        vol_horizons.append(vol_h)
        sl_dist = vol_h * config["sl_multiplier"]
        exp_win = vol_h * ew_mult
        reward = risk = 0; best_tp = 0; trade_closed = False

        if is_short_dir:
            sl  = entry + sl_dist
            tp1 = entry - 0.7*exp_win;  tp2 = entry - 1.2*exp_win
            tp3 = entry - 1.6*exp_win;  tp4 = entry - 2.0*exp_win
            tr1 = entry - 0.55*exp_win; tr2 = entry - 1.05*exp_win
            tr3 = entry - 1.4*exp_win;  tr4 = entry - 1.8*exp_win

            for price in future:
                if price >= sl and best_tp == 0:
                    reward,risk=0,sl_dist; losses+=1; trade_closed=True; break
                if   price<=tp4 and best_tp<4: best_tp=4
                elif price<=tp3 and best_tp<3: best_tp=3
                elif price<=tp2 and best_tp<2: best_tp=2
                elif price<=tp1 and best_tp<1: best_tp=1
                if   best_tp>=4 and price>=tr4: reward,risk=1.8*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=3 and price>=tr3: reward,risk=1.4*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=2 and price>=tr2: reward,risk=1.05*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=1 and price>=tr1: reward,risk=0.55*exp_win,0;wins+=1;trade_closed=True;break

            if not trade_closed:
                pnl = entry - future.iloc[-1]
                if   best_tp>=4: reward,risk=2.0*exp_win,0;wins+=1
                elif best_tp>=3: reward,risk=1.6*exp_win,0;wins+=1
                elif best_tp>=2: reward,risk=1.2*exp_win,0;wins+=1
                elif best_tp>=1: reward,risk=0.7*exp_win,0;wins+=1
                else:
                    if pnl>0: reward,risk=pnl,0;wins+=1
                    else:     reward,risk=0,abs(pnl);losses+=1
        else:
            sl  = entry - sl_dist
            tp1 = entry + 0.7*exp_win;  tp2 = entry + 1.2*exp_win
            tp3 = entry + 1.6*exp_win;  tp4 = entry + 2.0*exp_win
            tr1 = entry + 0.55*exp_win; tr2 = entry + 1.05*exp_win
            tr3 = entry + 1.4*exp_win;  tr4 = entry + 1.8*exp_win

            for price in future:
                if price <= sl and best_tp == 0:
                    reward,risk=0,sl_dist; losses+=1; trade_closed=True; break
                if   price>=tp4 and best_tp<4: best_tp=4
                elif price>=tp3 and best_tp<3: best_tp=3
                elif price>=tp2 and best_tp<2: best_tp=2
                elif price>=tp1 and best_tp<1: best_tp=1
                if   best_tp>=4 and price<=tr4: reward,risk=1.8*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=3 and price<=tr3: reward,risk=1.4*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=2 and price<=tr2: reward,risk=1.05*exp_win,0;wins+=1;trade_closed=True;break
                elif best_tp>=1 and price<=tr1: reward,risk=0.55*exp_win,0;wins+=1;trade_closed=True;break

            if not trade_closed:
                pnl = future.iloc[-1] - entry
                if   best_tp>=4: reward,risk=2.0*exp_win,0;wins+=1
                elif best_tp>=3: reward,risk=1.6*exp_win,0;wins+=1
                elif best_tp>=2: reward,risk=1.2*exp_win,0;wins+=1
                elif best_tp>=1: reward,risk=0.7*exp_win,0;wins+=1
                else:
                    if pnl>0: reward,risk=pnl,0;wins+=1
                    else:     reward,risk=0,abs(pnl);losses+=1

        rewards.append(reward); risks.append(risk)
        rewards_vol_adj.append(reward/vol_h if vol_h>0 else 0)
        risks_vol_adj.append(risk/vol_h if vol_h>0 else 0)

    if not rewards:
        return None

    win_rew  = [r for r in rewards if r>0]
    los_risk = [r for r in risks   if r>0]
    avg_win  = np.mean(win_rew)  if win_rew  else 0
    avg_loss = np.mean(los_risk) if los_risk else 0

    win_va   = [rewards_vol_adj[i] for i in range(len(rewards)) if rewards[i]>0]
    los_va   = [risks_vol_adj[i]   for i in range(len(risks))   if risks[i]>0]
    avg_w_va = np.mean(win_va)  if win_va  else 0
    avg_l_va = np.mean(los_va)  if los_va  else 0

    total    = wins+losses
    win_rate = wins/total*100 if total>0 else np.nan
    p_win    = wins/total  if total>0 else 0
    p_loss   = losses/total if total>0 else 0

    rr_ratio = avg_win/avg_loss if avg_loss>0 else np.nan
    rr_vpa   = (p_win*avg_w_va)/(p_loss*avg_l_va) if p_loss>0 and avg_l_va>0 else np.nan

    vol_today = today_metrics.get("Vol_Horizon", np.nan)
    exp_win_c = avg_w_va*vol_today if avg_w_va>0 and not np.isnan(vol_today) else vol_today*ew_mult
    stop_loss = exp_win_c/rr_vpa if not np.isnan(rr_vpa) and rr_vpa>0 else exp_win_c/rr_ratio_target

    direction = "SHORT" if is_short_dir else "LONG"

    if isinstance(rr_vpa, float) and not np.isnan(rr_vpa):
        rr_display = "≥ 5:1" if rr_vpa > 5 else round(rr_vpa, 2)
    else:
        rr_display = np.nan

    return {
        "horizon":      horizon_name,
        "direction":    direction,
        "wins":         wins,
        "losses":       losses,
        "win_rate":     round(win_rate, 1) if not np.isnan(win_rate) else np.nan,
        "avg_win":      round(avg_win, 2),
        "avg_loss":     round(avg_loss, 2),
        "expected_win": round(exp_win_c, 2) if not np.isnan(exp_win_c) else np.nan,
        "stop_loss":    round(stop_loss, 2) if not np.isnan(stop_loss) else np.nan,
        "rr_vpa":       rr_display,
        "rr_vpa_num":   rr_vpa,
    }

def run_backtest(s_full, s_today_metrics, bt_lookback_days, dir_signal='YieldRatio 6M'):
    if bt_lookback_days < 99999:
        cutoff = s_full.index[-1] - pd.Timedelta(days=bt_lookback_days)
        s_bt   = s_full[s_full.index >= cutoff]
    else:
        s_bt = s_full.copy()

    best_result = None
    best_rr     = -np.inf
    all_results = {}

    for hn, cfg in HORIZONS_CONFIG.items():
        metrics       = compute_metrics_horizon(s_bt, cfg)
        today_metrics = compute_metrics_horizon(s_full, cfg).iloc[-1].to_dict()
        result        = backtest_single_horizon(s_bt, today_metrics, cfg, hn, dir_signal)
        all_results[hn] = result

        if result is not None:
            rr = result["rr_vpa_num"]
            if isinstance(rr, float) and not np.isnan(rr) and rr > best_rr:
                best_rr     = rr
                best_result = result

    return best_result, all_results

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown(f"<div style='color:{ACCENT};font-size:0.68rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>METRICS & BACKTEST</div>", unsafe_allow_html=True)

    dep_type = st.selectbox("Type", ['Single CCY', 'XMkt'],
                            index=['Single CCY','XMkt'].index(st.session_state.get('mb_dep_type','Single CCY')),
                            key='mb_dep_type')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>STRUCTURE 1</div>", unsafe_allow_html=True)
    ccy1         = st.selectbox("CCY", CURRENCIES, key='mb_ccy1')
    struct_type1 = st.selectbox("Type", ['Outright','Curve','Fly'], key='mb_struct_type1')
    df_ccy1      = load_ccy_data(ccy1)
    instruments1 = list(df_ccy1.columns[1:]) if df_ccy1 is not None else []
    wing1_1      = st.selectbox("Wing 1", instruments1, key='mb_wing1_1')
    belly_1      = st.selectbox("Belly",  instruments1, index=min(5,  len(instruments1)-1), key='mb_belly_1')
    wing2_1      = st.selectbox("Wing 2", instruments1, index=min(10, len(instruments1)-1), key='mb_wing2_1')

    if dep_type == 'XMkt':
        st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>STRUCTURE 2</div>", unsafe_allow_html=True)
        ccy2         = st.selectbox("CCY 2", CURRENCIES, index=1, key='mb_ccy2')
        struct_type2 = st.selectbox("Type 2", ['Outright','Curve','Fly'], key='mb_struct_type2')
        df_ccy2      = load_ccy_data(ccy2)
        instruments2 = list(df_ccy2.columns[1:]) if df_ccy2 is not None else []
        wing1_2      = st.selectbox("Wing 1 (2)", instruments2, key='mb_wing1_2')
        belly_2      = st.selectbox("Belly (2)",  instruments2, index=min(5,  len(instruments2)-1), key='mb_belly_2')
        wing2_2      = st.selectbox("Wing 2 (2)", instruments2, index=min(10, len(instruments2)-1), key='mb_wing2_2')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>BACKTEST LOOKBACK</div>", unsafe_allow_html=True)
    bt_lookback = st.selectbox("Lookback", list(LOOKBACK_BT_MAP.keys()),
                               index=list(LOOKBACK_BT_MAP.keys()).index(st.session_state.get('mb_bt_lookback','Max')),
                               key='mb_bt_lookback')

    st.markdown(f"<div style='color:{TEXT_MUTED_S};font-size:0.65rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin:10px 0 4px;'>DIRECTION SIGNAL</div>", unsafe_allow_html=True)
    DIR_OPTIONS = ['YieldRatio 6M', 'BB MA20', 'Zscore 6M']
    dir_signal = st.selectbox("Signal", DIR_OPTIONS,
                              index=DIR_OPTIONS.index(st.session_state.get('mb_dir_signal','YieldRatio 6M')),
                              key='mb_dir_signal')

    st.markdown("<div style='margin:14px 0'></div>", unsafe_allow_html=True)
    run_button = st.button("▶  RUN", use_container_width=True)

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

# ========== RUN ==========
if run_button:
    if df_ccy1 is None:
        st.error("Cannot load currency data.")
    else:
        with st.spinner("Computing..."):
            struct1 = compute_structure(df_ccy1, struct_type1, wing1_1, belly_1, wing2_1)

            if dep_type == 'XMkt' and df_ccy2 is not None:
                struct2    = compute_structure(df_ccy2, struct_type2, wing1_2, belly_2, wing2_2)
                merged_dep = pd.merge(struct1, struct2, on='Date', suffixes=('_1','_2')).dropna()
                merged_dep['Value'] = merged_dep['Value_1'] - merged_dep['Value_2']
                dep_series = merged_dep[['Date','Value']].copy()
            else:
                dep_series = struct1.copy()

            dep_series = dep_series.sort_values('Date').dropna().reset_index(drop=True)
            s_full     = dep_series.set_index('Date')['Value']

            metrics             = compute_display_metrics(s_full)
            bt_days             = LOOKBACK_BT_MAP[bt_lookback]
            best_result, all_bt = run_backtest(s_full, metrics, bt_days, dir_signal)

        st.session_state['mb_metrics']           = metrics
        st.session_state['mb_best_result']       = best_result
        st.session_state['mb_all_bt']            = all_bt
        st.session_state['mb_dep_title']         = dep_title
        st.session_state['mb_bt_lookback_label'] = bt_lookback

def build_export_text(dep_title, metrics, best_result):
    def fmt(v, decimals=2, suffix=""):
        if v is None or pd.isna(v):
            return "N/A"
        return f"{v:.{decimals}f}{suffix}"

    best_horizon = best_result["horizon"] if best_result is not None else "N/A"

    if best_result is not None:
        expected_win = fmt(best_result.get("expected_win"), 2, " bp")
        stop_loss = fmt(best_result.get("stop_loss"), 2, " bp")

        rr_val = best_result.get("rr_vpa", np.nan)
        if isinstance(rr_val, str):
            rr_text = rr_val
        elif pd.notna(rr_val):
            rr_text = f"{rr_val:.2f}"
        else:
            rr_text = "N/A"
    else:
        expected_win = "N/A"
        stop_loss = "N/A"
        rr_text = "N/A"

    text = f"""Structure : {dep_title}

Metrics
CTA :
Last week in CTA :
5d projection :

Zscore 1M : {fmt(metrics.get("Zscore_1m"), 2)}
Zscore 6M : {fmt(metrics.get("Zscore_6m"), 2)}
YieldRatio 1M : {fmt(metrics.get("YieldRatio_1m"), 3)}
YieldRatio 6M : {fmt(metrics.get("YieldRatio_6m"), 3)}
RSI 14d : {fmt(metrics.get("RSI_14d"), 1)}
BB20 Position % : {fmt(metrics.get("BB20_Position_%"), 1)}
Vol 3w/3m : {fmt(metrics.get("Vol3w/Vol3m"), 3)}
MR Score : {fmt(metrics.get("MR_Score"), 3)}
ADF pval 5Y : {fmt(metrics.get("ADF_pval_5y"), 3)}
Hurst 6M : {fmt(metrics.get("Hurst_6m"), 4)}
Crossings 1M : {fmt(metrics.get("crossings_1m"), 0)}
Crossings 3M : {fmt(metrics.get("crossings_3m"), 0)}
Crossings 6M : {fmt(metrics.get("crossings_6m"), 0)}
HalfLife 1Y : {fmt(metrics.get("HalfLife_1y"), 2)}
AR1 Phi 1Y : {fmt(metrics.get("AR1_phi_1y"), 3)}

Backtest
Best horizon : {best_horizon}
Expected Win : {expected_win}
Stop Loss : {stop_loss}
RR Vol+Proba Adj : {rr_text}

Regression :
Roll :
Narrative :
"""
    return text

# ========== AFFICHAGE ==========
if 'mb_metrics' in st.session_state:
    metrics     = st.session_state['mb_metrics']
    best_result = st.session_state['mb_best_result']
    all_bt      = st.session_state['mb_all_bt']

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("<div class='section-title'>Market Metrics</div>", unsafe_allow_html=True)

        def metric_row(label, value, fmt=".4f", color_logic=None):
            if pd.isna(value) if isinstance(value, float) else value is None:
                val_str   = "N/A"
                val_class = "metric-value"
            else:
                val_str = f"{value:{fmt}}"
                if color_logic == "zscore":
                    val_class = "metric-value negative" if value < 0 else "metric-value positive"
                elif color_logic == "yr":
                    val_class = "metric-value negative" if value < 0.5 else "metric-value positive"
                elif color_logic == "rsi":
                    val_class = "metric-value negative" if value < 40 else ("metric-value positive" if value > 60 else "metric-value")
                elif color_logic == "vol":
                    val_class = "metric-value positive" if value < 1 else "metric-value negative"
                else:
                    val_class = "metric-value"

            st.markdown(f"""
            <div class='metric-card'>
                <span class='metric-label'>{label}</span>
                <span class='{val_class}'>{val_str}</span>
            </div>""", unsafe_allow_html=True)

        metric_row("Last (bp)",       metrics["Last (bp)"],       ".2f")
        metric_row("MA5",             metrics["MA5"],             ".2f")
        metric_row("MA10",            metrics["MA10"],            ".2f")

        st.markdown("<div class='section-title'>Z-Score</div>", unsafe_allow_html=True)
        metric_row("Zscore 1M",       metrics["Zscore_1m"],       ".2f", "zscore")
        metric_row("Zscore 6M",       metrics["Zscore_6m"],       ".2f", "zscore")

        st.markdown("<div class='section-title'>Yield Ratio</div>", unsafe_allow_html=True)
        metric_row("YieldRatio 1M",   metrics["YieldRatio_1m"],   ".3f", "yr")
        metric_row("YieldRatio 6M",   metrics["YieldRatio_6m"],   ".3f", "yr")

        st.markdown("<div class='section-title'>Technicals</div>", unsafe_allow_html=True)
        metric_row("RSI 14d",         metrics["RSI_14d"],         ".1f", "rsi")
        metric_row("BB20 Position %", metrics["BB20_Position_%"], ".1f")
        metric_row("Vol 3w/3m",       metrics["Vol3w/Vol3m"],     ".3f", "vol")
        metric_row("MR Score",        metrics["MR_Score"],        ".3f")
        metric_row("ADF pval 5Y",     metrics["ADF_pval_5y"],     ".3f")
        metric_row("Hurst 6M",        metrics["Hurst_6m"],        ".4f")
        metric_row("Crossings 1M",    metrics["crossings_1m"],    ".0f")
        metric_row("Crossings 3M",    metrics["crossings_3m"],    ".0f")
        metric_row("Crossings 6M",    metrics["crossings_6m"],    ".0f")
        metric_row("HalfLife 1Y",     metrics["HalfLife_1y"],     ".2f")
        metric_row("AR1 Phi 1Y",      metrics["AR1_phi_1y"],      ".3f")

    with col_right:
        st.markdown(
            f"<div class='section-title'>Backtest — {st.session_state.get('mb_bt_lookback_label','Max')} Lookback</div>",
            unsafe_allow_html=True
        )

        for hn in ["1M", "3M", "6M"]:
            r = all_bt.get(hn)
            is_best = (
                best_result is not None and
                r is not None and
                r["horizon"] == best_result["horizon"]
            )

            if r is None:
                st.markdown(f"""
                <div class='backtest-card'>
                    <div class='backtest-header'>{hn} — No trades found</div>
                </div>""", unsafe_allow_html=True)
                continue

            dir_badge  = (
                f"<span class='direction-long'>LONG</span>"
                if r["direction"] == "LONG"
                else f"<span class='direction-short'>SHORT</span>"
            )
            best_badge = "<span class='best-badge'>BEST</span>&nbsp;" if is_best else ""

            rr_val = r["rr_vpa"]
            rr_str = (
                str(rr_val)
                if isinstance(rr_val, str)
                else (f"{rr_val:.2f}" if isinstance(rr_val, float) and not np.isnan(rr_val) else "N/A")
            )
            exp_str = f"{r['expected_win']:.2f} bp" if not np.isnan(r["expected_win"]) else "N/A"
            sl_str  = f"{r['stop_loss']:.2f} bp"   if not np.isnan(r["stop_loss"])   else "N/A"

            st.markdown(f"""
            <div class='backtest-card' style='{"border-left: 3px solid " + BLUE + ";" if is_best else ""}'>
                <div class='backtest-header'>
                    {best_badge}{hn} &nbsp;{dir_badge}
                    &nbsp;&nbsp;
                    <span style='font-size:0.7rem;color:{TEXT_MUTED};font-weight:400;'>
                        {r['wins']}W / {r['losses']}L &nbsp;·&nbsp; Win Rate {r['win_rate']:.1f}%
                    </span>
                </div>
                <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;font-family:JetBrains Mono,monospace;font-size:0.80rem;'>
                    <div>
                        <div style='color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;'>Avg Win</div>
                        <div style='color:{GREEN};font-weight:600;'>{r['avg_win']:.2f} bp</div>
                    </div>
                    <div>
                        <div style='color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;'>Avg Loss</div>
                        <div style='color:{RED};font-weight:600;'>{r['avg_loss']:.2f} bp</div>
                    </div>
                    <div>
                        <div style='color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;'>Expected Win</div>
                        <div style='color:{BLUE};font-weight:600;'>{exp_str}</div>
                    </div>
                    <div>
                        <div style='color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;'>Stop Loss</div>
                        <div style='color:{RED};font-weight:600;'>{sl_str}</div>
                    </div>
                    <div style='grid-column:1/-1;'>
                        <div style='color:{TEXT_MUTED};font-size:0.68rem;text-transform:uppercase;'>RR Vol+Proba Adj</div>
                        <div style='color:{TEXT_MAIN};font-weight:700;font-size:0.9rem;'>{rr_str}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Export Summary</div>", unsafe_allow_html=True)

        export_text = build_export_text(
            st.session_state.get("mb_dep_title", "N/A"),
            metrics,
            best_result
        )

        st.text_area(
            "Copy-ready summary",
            value=export_text,
            height=420,
            key="mb_export_text"
        )

        st.download_button(
            label="Download .txt",
            data=export_text,
            file_name="metrics_summary.txt",
            mime="text/plain"
        )

else:
    st.info("Configure your structure in the sidebar and click **RUN**.")

st.markdown(
    f"<div style='border-top:1px solid {GRID_C};margin-top:2rem;padding-top:0.5rem;text-align:center;color:{TEXT_MUTED};font-size:0.7rem;font-family:Inter,sans-serif;'>© 2026 — Metrics & Backtest</div>",
    unsafe_allow_html=True
)