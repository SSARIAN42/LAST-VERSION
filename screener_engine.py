"""
screener_engine.py
------------------
Partie 1 : Construction des historiques de structures + métriques pures
           (sans régression — régression dans Partie 2)

Métriques calculées par structure :
  - Z-score résidu 1M / 3M / 6M
  - Percentile niveau 1M / 3M / 6M
  - Vol 1M / 3M / 6M
  - Carry 3M / 12M (depuis CARRY ROLL.xlsm, logique identique PCA)
  - Carry/Vol  (carry_3m / vol_3m)
  - Half-life AR(1)
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CHEMINS
# ─────────────────────────────────────────────────────────────────────────────
FILE_PATH  = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\1. SWAP\SWAP_XCCY_and_SINGLE_Data_Only.xlsm'
CARRY_FILE = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\5. Carry Rolls\CARRY ROLL.xlsm'
MACRO_FILE = FILE_PATH   # feuille MACRO dans le même fichier

# ─────────────────────────────────────────────────────────────────────────────
# DÉFINITION DES STRUCTURES EUR6
# Même liste utilisée pour toutes les CCY — le moteur skppe si leg absent
# ─────────────────────────────────────────────────────────────────────────────

SPOT_CURVES = [
    ('2s5s',   ['2s',  '5s'],          'curve'),
    ('3s5s',   ['3s',  '5s'],          'curve'),
    ('5s7s',   ['5s',  '7s'],          'curve'),
    ('5s10s',  ['5s',  '10s'],         'curve'),
    ('7s10s',  ['7s',  '10s'],         'curve'),
    ('10s12s', ['10s', '12s'],         'curve'),
    ('7s12s',  ['7s',  '12s'],         'curve'),
    ('10s15s', ['10s', '15s'],         'curve'),
    ('10s20s', ['10s', '20s'],         'curve'),
    ('5s20s',  ['5s',  '20s'],         'curve'),
    ('5s30s',  ['5s',  '30s'],         'curve'),
    ('10s30s', ['10s', '30s'],         'curve'),
    ('20s25s', ['20s', '25s'],         'curve'),
    ('20s30s', ['20s', '30s'],         'curve'),
    ('10s40s', ['10s', '40s'],         'curve'),
    ('20s40s', ['20s', '40s'],         'curve'),
    ('30s40s', ['30s', '40s'],         'curve'),
    ('30s50s', ['30s', '50s'],         'curve'),
    ('40s50s', ['40s', '50s'],         'curve'),
    ('25s30s', ['25s', '30s'],         'curve'),
]

SPOT_FLIES = [
    ('2s3s5s',    ['2s',  '3s',  '5s'],  'fly'),
    ('2s5s10s',   ['2s',  '5s',  '10s'], 'fly'),
    ('5s7s10s',   ['5s',  '7s',  '10s'], 'fly'),
    ('5s10s20s',  ['5s',  '10s', '20s'], 'fly'),
    ('5s10s30s',  ['5s',  '10s', '30s'], 'fly'),
    ('10s15s20s', ['10s', '15s', '20s'], 'fly'),
    ('5s10s15s',  ['5s',  '10s', '15s'], 'fly'),
    ('7s10s15s',  ['7s',  '10s', '15s'], 'fly'),
    ('7s10s12s',  ['7s',  '10s', '12s'], 'fly'),
    ('3s5s7s',    ['3s',  '5s',  '7s'],  'fly'),
    ('10s20s30s', ['10s', '20s', '30s'], 'fly'),
    ('20s25s30s', ['20s', '25s', '30s'], 'fly'),
    ('20s30s40s', ['20s', '30s', '40s'], 'fly'),
    ('30s40s50s', ['30s', '40s', '50s'], 'fly'),
    ('2s10s30s',  ['2s',  '10s', '30s'], 'fly'),
]

FWD_CURVES = [
    # ── IRS forwards ──
    ('1y1y_5y5y',      ['1y1y',  '5y5y'],   'curve'),
    ('2y2y_5y5y',      ['2y2y',  '5y5y'],   'curve'),
    ('5y5y_10y10y',    ['5y5y',  '10y10y'], 'curve'),
    ('3y2y_5y5y',      ['3y2y',  '5y5y'],   'curve'),
    ('3y2y_10y10y',    ['3y2y',  '10y10y'], 'curve'),
    ('2y1y_3y2y',      ['2y1y',  '3y2y'],   'curve'),
    ('5y2y_7y3y',      ['5y2y',  '7y3y'],   'curve'),
    ('10y5y_20y5y',    ['10y5y', '20y5y'],  'curve'),
    ('25y5y_30y20y',   ['25y5y', '30y20y'], 'curve'),
    ('5y5y_15y5y',     ['5y5y',  '15y5y'],  'curve'),
    ('3y2y_5y2y',      ['3y2y',  '5y2y'],   'curve'),
    ('8y2y_10y2y',     ['8y2y',  '10y2y'],  'curve'),
    ('10y2y_12y3y',    ['10y2y', '12y3y'],  'curve'),
    ('12y3y_15y5y',    ['12y3y', '15y5y'],  'curve'),
    ('15y5y_20y5y',    ['15y5y', '20y5y'],  'curve'),
    ('1y1y_2y3y',      ['1y1y',  '2y3y'],   'curve'),
    ('1y1y_3y2y',      ['1y1y',  '3y2y'],   'curve'),
    ('2y3y_5y5y',      ['2y3y',  '5y5y'],   'curve'),
    ('2y3y_10y10y',    ['2y3y',  '10y10y'], 'curve'),
    ('10y10y_20y10y',  ['10y10y','20y10y'], 'curve'),
    ('15y5y_20y10y',   ['15y5y', '20y10y'], 'curve'),
    ('2y1y_3y1y',      ['2y1y',  '3y1y'],   'curve'),
    ('1y1y_2y1y',      ['1y1y',  '2y1y'],   'curve'),
    ('20y10y_30y20y',  ['20y10y','30y20y'], 'curve'),
    ('20y10y_30y10y',  ['20y10y','30y10y'], 'curve'),
    ('1y2y_3y1y',      ['1y2y',  '3y1y'],   'curve'),
    ('10y5y_15y5y',    ['10y5y', '15y5y'],  'curve'),
    ('20y5y_25y5y',    ['20y5y', '25y5y'],  'curve'),
    ('6m_2s5s',    ['6m2y',  '6m5y'],  'curve'),
    ('6m_3s5s',    ['6m3y',  '6m5y'],  'curve'),
    ('6m_5s7s',    ['6m5y',  '6m7y'],  'curve'),
    ('6m_5s10s',   ['6m5y',  '6m10y'], 'curve'),
    ('6m_7s10s',   ['6m7y',  '6m10y'], 'curve'),
    ('6m_10s15s',  ['6m10y', '6m15y'], 'curve'),
    ('6m_10s20s',  ['6m10y', '6m20y'], 'curve'),
    ('6m_5s20s',   ['6m5y',  '6m20y'], 'curve'),
    ('6m_5s30s',   ['6m5y',  '6m30y'], 'curve'),
    ('6m_10s30s',  ['6m10y', '6m30y'], 'curve'),
    ('6m_20s30s',  ['6m20y', '6m30y'], 'curve'),
    ('1y_2s5s',    ['1y2y',  '1y5y'],  'curve'),
    ('1y_3s5s',    ['1y3y',  '1y5y'],  'curve'),
    ('1y_5s7s',    ['1y5y',  '1y7y'],  'curve'),
    ('1y_5s10s',   ['1y5y',  '1y10y'], 'curve'),
    ('1y_7s10s',   ['1y7y',  '1y10y'], 'curve'),
    ('1y_10s15s',  ['1y10y', '1y15y'], 'curve'),
    ('1y_10s20s',  ['1y10y', '1y20y'], 'curve'),
    ('1y_5s20s',   ['1y5y',  '1y20y'], 'curve'),
    ('1y_5s30s',   ['1y5y',  '1y30y'], 'curve'),
    ('1y_10s30s',  ['1y10y', '1y30y'], 'curve'),
    ('1y_20s30s',  ['1y20y', '1y30y'], 'curve'),
    ('2y_2s5s',    ['2y2y',  '2y5y'],  'curve'),
    ('2y_3s5s',    ['2y3y',  '2y5y'],  'curve'),
    ('2y_5s7s',    ['2y5y',  '2y7y'],  'curve'),
    ('2y_5s10s',   ['2y5y',  '2y10y'], 'curve'),
    ('2y_7s10s',   ['2y7y',  '2y10y'], 'curve'),
    ('2y_10s15s',  ['2y10y', '2y15y'], 'curve'),
    ('2y_10s20s',  ['2y10y', '2y20y'], 'curve'),
    ('2y_5s20s',   ['2y5y',  '2y20y'], 'curve'),
    ('2y_5s30s',   ['2y5y',  '2y30y'], 'curve'),
    ('2y_10s30s',  ['2y10y', '2y30y'], 'curve'),
    ('2y_20s30s',  ['2y20y', '2y30y'], 'curve'),
]

FWD_FLIES = [
    # ── IRS forwards ──
    ('1y1y_2y1y_3y1y',       ['1y1y',  '2y1y',  '3y1y'],   'fly'),
    ('1y2y_3y2y_5y5y',       ['1y2y',  '3y2y',  '5y5y'],   'fly'),
    ('3y2y_5y5y_10y10y',     ['3y2y',  '5y5y',  '10y10y'], 'fly'),
    ('5y5y_10y10y_20y10y',   ['5y5y',  '10y10y','20y10y'], 'fly'),
    ('10y10y_20y10y_30y10y', ['10y10y','20y10y','30y10y'], 'fly'),
    ('10y5y_15y5y_20y5y',    ['10y5y', '15y5y', '20y5y'],  'fly'),
    ('5y5y_10y5y_15y5y',     ['5y5y',  '10y5y', '15y5y'],  'fly'),
    ('3y2y_5y7y_7y3y',       ['3y2y',  '5y7y',  '7y3y'],   'fly'),
    ('8y2y_10y2y_12y3y',     ['8y2y',  '10y2y', '12y3y'],  'fly'),
    ('10y2y_12y3y_15y5y',    ['10y2y', '12y3y', '15y5y'],  'fly'),
    ('12y3y_15y5y_20y10y',   ['12y3y', '15y5y', '20y10y'], 'fly'),
    ('12y3y_15y5y_20y5y',    ['12y3y', '15y5y', '20y5y'],  'fly'),
    ('2y1y_3y2y_5y5y',       ['2y1y',  '3y2y',  '5y5y'],   'fly'),
    ('2y1y_3y2y_5y2y',       ['2y1y',  '3y2y',  '5y2y'],   'fly'),
    ('1y2y_3y2y_5y2y',       ['1y2y',  '3y2y',  '5y2y'],   'fly'),
    ('1y1y_2y2y_5y5y',       ['1y1y',  '2y2y',  '5y5y'],   'fly'),
    ('2y2y_5y5y_10y10y',     ['2y2y',  '5y5y',  '10y10y'], 'fly'),
    ('3y2y_5y5y_10y5y',      ['3y2y',  '5y5y',  '10y5y'],  'fly'),
    ('5y2y_7y2y_10y2y',      ['5y2y',  '7y2y',  '10y2y'],  'fly'),
    ('5y2y_7y3y_10y5y',      ['5y2y',  '7y3y',  '10y5y'],  'fly'),
    ('15y5y_20y5y_25y5y',    ['15y5y', '20y5y', '25y5y'],  'fly'),
    ('6m_2s3s5s',    ['6m2y',  '6m3y',  '6m5y'],  'fly'),
    ('6m_2s5s10s',   ['6m2y',  '6m5y',  '6m10y'], 'fly'),
    ('6m_5s7s10s',   ['6m5y',  '6m7y',  '6m10y'], 'fly'),
    ('6m_5s10s20s',  ['6m5y',  '6m10y', '6m20y'], 'fly'),
    ('6m_5s10s30s',  ['6m5y',  '6m10y', '6m30y'], 'fly'),
    ('6m_10s15s20s', ['6m10y', '6m15y', '6m20y'], 'fly'),
    ('6m_5s10s15s',  ['6m5y',  '6m10y', '6m15y'], 'fly'),
    ('6m_3s5s7s',    ['6m3y',  '6m5y',  '6m7y'],  'fly'),
    ('6m_10s20s30s', ['6m10y', '6m20y', '6m30y'], 'fly'),
    ('6m_2s10s30s',  ['6m2y',  '6m10y', '6m30y'], 'fly'),
    ('1y_2s3s5s',    ['1y2y',  '1y3y',  '1y5y'],  'fly'),
    ('1y_2s5s10s',   ['1y2y',  '1y5y',  '1y10y'], 'fly'),
    ('1y_5s7s10s',   ['1y5y',  '1y7y',  '1y10y'], 'fly'),
    ('1y_5s10s20s',  ['1y5y',  '1y10y', '1y20y'], 'fly'),
    ('1y_5s10s30s',  ['1y5y',  '1y10y', '1y30y'], 'fly'),
    ('1y_10s15s20s', ['1y10y', '1y15y', '1y20y'], 'fly'),
    ('1y_5s10s15s',  ['1y5y',  '1y10y', '1y15y'], 'fly'),
    ('1y_3s5s7s',    ['1y3y',  '1y5y',  '1y7y'],  'fly'),
    ('1y_10s20s30s', ['1y10y', '1y20y', '1y30y'], 'fly'),
    ('1y_2s10s30s',  ['1y2y',  '1y10y', '1y30y'], 'fly'),
    ('2y_2s3s5s',    ['2y2y',  '2y3y',  '2y5y'],  'fly'),
    ('2y_2s5s10s',   ['2y2y',  '2y5y',  '2y10y'], 'fly'),
    ('2y_5s7s10s',   ['2y5y',  '2y7y',  '2y10y'], 'fly'),
    ('2y_5s10s20s',  ['2y5y',  '2y10y', '2y20y'], 'fly'),
    ('2y_5s10s30s',  ['2y5y',  '2y10y', '2y30y'], 'fly'),
    ('2y_10s15s20s', ['2y10y', '2y15y', '2y20y'], 'fly'),
    ('2y_5s10s15s',  ['2y5y',  '2y10y', '2y15y'], 'fly'),
    ('2y_3s5s7s',    ['2y3y',  '2y5y',  '2y7y'],  'fly'),
    ('2y_10s20s30s', ['2y10y', '2y20y', '2y30y'], 'fly'),
    ('2y_2s10s30s',  ['2y2y',  '2y10y', '2y30y'], 'fly'),
]

ALL_STRUCTURES = SPOT_CURVES + SPOT_FLIES + FWD_CURVES + FWD_FLIES


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

def load_ccy_sheet(ccy: str) -> pd.DataFrame:
    """
    Charge la feuille CCY avec :
    - ligne 1 Excel = à drop
    - ligne 2 Excel = bond tickers -> headers
    - ligne 3+ Excel = données
    """
    df_raw = pd.read_excel(
        FILE_PATH,
        sheet_name=ccy,
        engine='openpyxl',
        header=1   # ligne 2 Excel
    )

    date_col = df_raw.columns[0]
    df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, errors='coerce')
    df_raw = df_raw.dropna(subset=[date_col])
    df_raw = df_raw.set_index(date_col)
    df_raw.index.name = 'Date'

    for col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

    return df_raw

def load_macro_sheet() -> pd.DataFrame:
    df_raw = pd.read_excel(
        FILE_PATH,
        sheet_name='REGRESSOR',
        engine='openpyxl',
        header=2
    )

    df_raw = df_raw.iloc[1:].reset_index(drop=True)

    date_col = df_raw.columns[0]
    df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, errors='coerce')
    df_raw = df_raw.dropna(subset=[date_col]).set_index(date_col)
    df_raw.index.name = 'Date'

    for col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

    return df_raw

def load_carry(ccy: str) -> dict:
    """
    Charge le carry depuis CARRY ROLL.xlsm, feuille RESULTS.
    Logique identique au code PCA.
    Retourne dict: {instrument: {'3m': float, '12m': float}}
    """
    carry_data = {}
    try:
        df_carry = pd.read_excel(CARRY_FILE, sheet_name='RESULTS', engine='openpyxl')
        col_3m  = f"{ccy} 3m"
        col_12m = f"{ccy} 12m"
        if col_3m in df_carry.columns and col_12m in df_carry.columns:
            structure_col = df_carry.columns[1]
            for _, row in df_carry.iterrows():
                name = row[structure_col]
                if pd.notna(name):
                    c3m  = row[col_3m]  if pd.notna(row[col_3m])  else np.nan
                    c12m = row[col_12m] if pd.notna(row[col_12m]) else np.nan
                    carry_data[str(name).strip()] = {'3m': c3m, '12m': c12m}
    except Exception:
        pass
    return carry_data


# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCTION D'UNE STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

def build_structure_series(df: pd.DataFrame, legs: list, stype: str) -> pd.Series | None:
    """
    Construit la série historique d'une structure en bps.
    curve : (leg2 - leg1) * 100
    fly   : (2*belly - wing1 - wing2) * 100
    Retourne None si un leg est absent.
    """
    for leg in legs:
        if leg not in df.columns:
            return None

    cols = [df[leg] for leg in legs]

    if stype == 'curve':
        s = (cols[1] - cols[0]) * 100
    elif stype == 'fly':
        s = (2 * cols[1] - cols[0] - cols[2]) * 100
    else:
        return None

    s = s.dropna()
    if len(s) < 30:
        return None

    return s


# ─────────────────────────────────────────────────────────────────────────────
# CARRY D'UNE STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

def compute_structure_carry(carry_data: dict, legs: list, stype: str) -> dict:
    """
    Calcule carry 3M et 12M pour une structure.
    curve : carry_leg2 - carry_leg1
    fly   : 2*carry_belly - carry_wing1 - carry_wing2
    """
    def get(leg, horizon):
        return carry_data.get(leg, {}).get(horizon, np.nan)

    result = {'3m': np.nan, '12m': np.nan}

    if stype == 'curve' and len(legs) == 2:
        for h in ['3m', '12m']:
            c0, c1 = get(legs[0], h), get(legs[1], h)
            if not np.isnan(c0) and not np.isnan(c1):
                result[h] = c1 - c0

    elif stype == 'fly' and len(legs) == 3:
        for h in ['3m', '12m']:
            c0, c1, c2 = get(legs[0], h), get(legs[1], h), get(legs[2], h)
            if not (np.isnan(c0) or np.isnan(c1) or np.isnan(c2)):
                result[h] = 2 * c1 - c0 - c2

    return result


# ─────────────────────────────────────────────────────────────────────────────
# MÉTRIQUES PURES (sans régression)
# ─────────────────────────────────────────────────────────────────────────────

WINDOWS_BASE = {'1M': 21, '3M': 63, '6M': 126}

LOOKBACK_MAP = {
    '1M':  21,
    '3M':  63,
    '6M':  126,
    '1Y':  252,
    '2Y':  504,
    '3Y':  756,
    '5Y':  1260,
    '10Y': 2520,
}

def get_windows(lookback_label: str) -> dict:
    """
    Retourne toujours 1M/3M/6M + le lookback sélectionné s'il n'est pas déjà dedans.
    Ex: '5Y' → {'1M':21, '3M':63, '6M':126, '5Y':1260}
    Ex: '3M' → {'1M':21, '3M':63, '6M':126}  (3M déjà dans la base)
    """
    windows = dict(WINDOWS_BASE)
    if lookback_label not in WINDOWS_BASE:
        windows[lookback_label] = LOOKBACK_MAP[lookback_label]
    return windows


def calc_ar1_half_life(s: pd.Series, window: int) -> float:
    """Half-life via AR(1) sur la fenêtre demandée."""
    r = s.dropna().iloc[-window:].values
    if len(r) < 10:
        return np.nan

    phi = np.dot(r[:-1], r[1:]) / (np.dot(r[:-1], r[:-1]) + 1e-12)

    if phi <= 0 or phi >= 1:
        return np.nan

    return -np.log(2) / np.log(phi)


def compute_metrics(s: pd.Series, carry: dict, windows: dict = None, hl_window: int = 252) -> dict:
    """
    Calcule toutes les métriques pures pour une série.
    windows : dict {'1M':21, '3M':63, ...}
    hl_window : fenêtre utilisée pour le calcul du half-life
    """
    if windows is None:
        windows = WINDOWS_BASE

    last = s.iloc[-1]
    m = {'Last (bp)': round(last, 4)}

    for label, w in windows.items():
        sub = s.iloc[-w:] if len(s) >= w else s

        mu, sigma = sub.mean(), sub.std()
        z = (last - mu) / sigma if sigma > 0 else np.nan
        m[f'Zscore_{label}'] = round(z, 4) if not np.isnan(z) else np.nan

        pct = (sub < last).mean() * 100
        m[f'Pct_{label}'] = round(pct, 1)

        vol = sub.diff().std() * np.sqrt(252)
        m[f'Vol_{label}'] = round(vol, 4) if not np.isnan(vol) else np.nan

    m['Carry_3M'] = carry.get('3m', np.nan)
    m['Carry_12M'] = carry.get('12m', np.nan)

    vol_3m = m.get('Vol_3M', np.nan)
    c3m = m.get('Carry_3M', np.nan)
    if not np.isnan(c3m) and not np.isnan(vol_3m) and vol_3m > 0:
        m['Carry_Vol'] = round(c3m / vol_3m, 4)
    else:
        m['Carry_Vol'] = np.nan

    hl = calc_ar1_half_life(s, hl_window)
    m['Half_Life'] = round(hl, 1) if not np.isnan(hl) else np.nan

    return m


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE — RUN SCREENER (Partie 1)
# ─────────────────────────────────────────────────────────────────────────────

def run_screener_part1(ccy: str, lookback_label: str = '1Y', progress_callback=None) -> pd.DataFrame:
    """
    Pour une CCY donnée :
    1. Charge la feuille CCY
    2. Charge le carry
    3. Pour chaque structure de ALL_STRUCTURES :
       - Tente de construire la série historique
       - Si OK → calcule les métriques
       - Si KO (leg absent) → skip silencieusement
    4. Retourne un DataFrame avec une ligne par structure

    progress_callback : callable(current, total) pour Streamlit progress bar
    """
    # Chargement
    try:
        df = load_ccy_sheet(ccy)
    except Exception as e:
        raise RuntimeError(f"Impossible de charger la feuille {ccy} : {e}")

    carry_data = load_carry(ccy)

    windows = get_windows(lookback_label)
    rows = []
    total = len(ALL_STRUCTURES)

    for i, (name, legs, stype) in enumerate(ALL_STRUCTURES):
        if progress_callback:
            progress_callback(i, total)

        # Construction de la série
        s = build_structure_series(df, legs, stype)
        if s is None:
            continue  # skip silencieux

        # Carry
        carry = compute_structure_carry(carry_data, legs, stype)

        # Métriques
        hl_window = LOOKBACK_MAP.get(lookback_label, 252)
        metrics = compute_metrics(s, carry, windows, hl_window=hl_window)

        row = {
            'CCY':       ccy,
            'Structure': name,
            'Type':      stype,
            'Legs':      ' | '.join(legs),
        }
        row.update(metrics)

        # Stocker la série pour la Partie 2 (régression)
        row['_series'] = s

        rows.append(row)

    if progress_callback:
        progress_callback(total, total)

    if not rows:
        return pd.DataFrame()

    df_out = pd.DataFrame(rows)
    return df_out


# ─────────────────────────────────────────────────────────────────────────────
# PARTIE 2 — RÉGRESSION vs MACRO (appelée après sélection de l'asset macro)
# ─────────────────────────────────────────────────────────────────────────────

def run_regression_vs_macro(
    df_structures: pd.DataFrame,
    macro_series: pd.Series,
    lookback_label: str = '1Y',
) -> pd.DataFrame:
    """
    Pour chaque structure dans df_structures :
    - Régression OLS 1-for-1 (structure ~ macro) sur lookback_label
    - Calcule R², résidu last, percentile + zscore résidu (1M/3M/6M + lookback), corr 252j/126j
    Retourne df_structures enrichi des colonnes de régression.
    """
    from scipy import stats

    windows     = get_windows(lookback_label)
    lookback_days = LOOKBACK_MAP.get(lookback_label, 252)

    r2_list, resid_last_list = [], []
    resid_pct  = {lbl: [] for lbl in windows}
    resid_z    = {lbl: [] for lbl in windows}
    corr_252_list, corr_126_list = [], []

    macro_clean = macro_series.dropna()

    def _append_nan():
        r2_list.append(np.nan)
        resid_last_list.append(np.nan)
        for lbl in windows:
            resid_pct[lbl].append(np.nan)
            resid_z[lbl].append(np.nan)
        corr_252_list.append(np.nan)
        corr_126_list.append(np.nan)

    for _, row in df_structures.iterrows():
        s = row.get('_series')
        if s is None or not isinstance(s, pd.Series):
            _append_nan()
            continue

        # Aligner sur lookback
        merged = pd.concat([s.rename('Y'), macro_clean.rename('X')], axis=1).dropna()
        if lookback_days < len(merged):
            merged = merged.iloc[-lookback_days:]

        if len(merged) < 30:
            _append_nan()
            continue

        y = merged['Y'].values
        x = merged['X'].values

        slope, intercept, r_val, _, _ = stats.linregress(x, y)
        r2        = r_val ** 2
        resid     = pd.Series(y - (slope * x + intercept), index=merged.index)
        last_resid = resid.iloc[-1]

        r2_list.append(round(r2, 4))
        resid_last_list.append(round(last_resid, 4))

        # Percentile + Z-score résidu par fenêtre
        for lbl, w in windows.items():
            sub = resid.iloc[-w:] if len(resid) >= w else resid
            pct = (sub < last_resid).mean() * 100
            resid_pct[lbl].append(round(pct, 1))
            mu, sigma = sub.mean(), sub.std()
            z = (last_resid - mu) / sigma if sigma > 0 else np.nan
            resid_z[lbl].append(round(z, 4) if not np.isnan(z) else np.nan)

        # Corrélations sur série complète
        full_merged = pd.concat([s.rename('Y'), macro_clean.rename('X')], axis=1).dropna()
        corr_252 = full_merged.iloc[-252:].corr().iloc[0, 1] if len(full_merged) >= 252 else full_merged.corr().iloc[0, 1]
        corr_126 = full_merged.iloc[-126:].corr().iloc[0, 1] if len(full_merged) >= 126 else full_merged.corr().iloc[0, 1]
        corr_252_list.append(round(corr_252, 4))
        corr_126_list.append(round(corr_126, 4))

    df_out = df_structures.copy()
    df_out['R2']         = r2_list
    df_out['Resid_Last'] = resid_last_list
    for lbl in windows:
        df_out[f'Resid_Pct_{lbl}'] = resid_pct[lbl]
        df_out[f'Resid_Z_{lbl}']   = resid_z[lbl]
    df_out['Corr_252d'] = corr_252_list
    df_out['Corr_126d'] = corr_126_list

    return df_out


# ─────────────────────────────────────────────────────────────────────────────
# COLONNES À AFFICHER DANS LE TABLEAU (sans _series)
# ─────────────────────────────────────────────────────────────────────────────

DISPLAY_COLS_BASE = [
    'Structure', 'Type', 'Last (bp)',
    'Carry_3M', 'Carry_12M', 'Carry_Vol', 'Half_Life',
]

def get_display_cols(lookback_label: str, with_regression: bool = False) -> list:
    """Retourne la liste des colonnes à afficher selon le lookback et si régression active."""
    windows = get_windows(lookback_label)
    cols = list(DISPLAY_COLS_BASE)
    for lbl in windows:
        cols += [f'Zscore_{lbl}', f'Pct_{lbl}', f'Vol_{lbl}']
    if with_regression:
        cols += ['R2', 'Resid_Last']
        for lbl in windows:
            cols += [f'Resid_Pct_{lbl}', f'Resid_Z_{lbl}']
        cols += ['Corr_252d', 'Corr_126d']
    return cols
