import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
 

 
# ========== CUSTOM CSS FOR BEAUTIFUL UI ==========
st.markdown("""
<style>
/* Import beautiful fonts */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap');
 /* Global styling */
.main {
   background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
 /* Headers with elegant typography */
h1 {
   font-family: 'Playfair Display', serif;
   color: #1a1a2e;
   font-weight: 700;
   text-align: center;
   padding: 1.5rem 0;
   background: linear-gradient(120deg, #2c3e50, #3498db);
   -webkit-background-clip: text;
   -webkit-text-fill-color: transparent;
   font-size: 3rem;
   letter-spacing: -0.5px;
}
 h2 {
   font-family: 'Playfair Display', serif;
   color: #2c3e50;
   font-weight: 600;
   margin-top: 2rem;
   margin-bottom: 1rem;
   border-bottom: 3px solid #3498db;
   padding-bottom: 0.5rem;
}
 h3 {
   font-family: 'Source Sans Pro', sans-serif;
   color: #34495e;
   font-weight: 600;
   margin-top: 1.5rem;
}
 /* Beautiful cards */
.stApp [data-testid="stHorizontalBlock"] {
   background: rgba(255, 255, 255, 0.95);
   border-radius: 15px;
   padding: 1.5rem;
   box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
   backdrop-filter: blur(10px);
   margin: 1rem 0;
}
 /* Input boxes styling */
.stSelectbox, .stNumberInput {
   font-family: 'Source Sans Pro', sans-serif;
}
 .stSelectbox > div > div {
   background: white;
   border: 2px solid #e0e6ed;
   border-radius: 10px;
   transition: all 0.3s ease;
}
 .stSelectbox > div > div:hover {
   border-color: #3498db;
   box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2);
}
 /* Metric cards */
[data-testid="stMetricValue"] {
   font-family: 'Source Sans Pro', sans-serif;
   font-size: 1.8rem;
   font-weight: 600;
   color: #2c3e50;
}
 [data-testid="stMetricLabel"] {
   font-family: 'Source Sans Pro', sans-serif;
   font-weight: 600;
   color: #7f8c8d;
   font-size: 0.95rem;
   letter-spacing: 0.5px;
}
 /* Buttons */
.stButton > button {
   font-family: 'Source Sans Pro', sans-serif;
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   color: white;
   border: none;
   border-radius: 25px;
   padding: 0.75rem 2.5rem;
   font-size: 1.1rem;
   font-weight: 600;
   letter-spacing: 0.5px;
   transition: all 0.3s ease;
   box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
   width: 100%;
}
 .stButton > button:hover {
   transform: translateY(-2px);
   box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}
 /* Results table */
.results-grid {
   display: grid;
   grid-template-columns: 120px repeat(3, 1fr);
   gap: 0.5rem;
   margin: 1.5rem 0;
   font-family: 'Source Sans Pro', sans-serif;
}
 .results-header {
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   color: white;
   padding: 1rem;
   border-radius: 10px;
   font-weight: 600;
   text-align: center;
   font-size: 0.95rem;
}
 .results-cell {
   background: white;
   border: 2px solid #e0e6ed;
   padding: 1rem;
   border-radius: 10px;
   text-align: center;
   font-weight: 500;
   color: #2c3e50;
   transition: all 0.2s ease;
}
 .results-cell:hover {
   border-color: #3498db;
   transform: scale(1.02);
}
 .results-label {
   background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
   color: white;
   padding: 1rem;
   border-radius: 10px;
   font-weight: 600;
   display: flex;
   align-items: center;
   justify-content: center;
   font-size: 0.95rem;
}
/* ===== SIDEBAR DARK CAVENTOR ===== */
section[data-testid="stSidebar"] {
   background-color: #0a1628 !important;
   border-right: 1px solid #1a3a5c !important;
}
section[data-testid="stSidebar"] * { color: #e8f4fd !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
   color: #7a9cc0 !important;
   font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
   background-color: #0f2040 !important;
   border: 1px solid #1a3a5c !important;
   border-radius: 3px !important;
}
section[data-testid="stSidebar"] .stButton > button {
   background-color: #00aaff !important;
   color: #0a1628 !important;
   border: none !important;
   border-radius: 3px !important;
   font-size: 0.82rem !important;
   font-weight: 700 !important;
   letter-spacing: 1px !important;
   text-transform: uppercase !important;
   width: 100% !important;
   padding: 0.5rem !important;
   box-shadow: none !important;
   transform: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
   background-color: #33bbff !important;
   box-shadow: 0 0 10px rgba(0,170,255,0.4) !important;
   transform: none !important;
}
.stAlert {
   border-radius: 4px;
   border-left: 3px solid #00aaff;
   background: rgba(0, 170, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)
 
# ========== TITRE PRINCIPAL ==========
st.markdown("<h1> Multi-Currency PCA Fair Value Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: Source Sans Pro; color: #7f8c8d; font-size: 1.2rem; margin-bottom: 2rem;'>Advanced Principal Component Analysis for Interest Rate Trading - 10 Independent Models</p>", unsafe_allow_html=True)
 
# ========== SIDEBAR - CONFIGURATION ==========
CURRENCIES = ['EUR6', 'EUR-OIS', 'USD', 'GBP', 'AUD6', 'NZD', 'CHF', 'CAD', 'JPY', 'SEK', 'NOK']

with st.sidebar:
    st.markdown("### Configuration")
    st.markdown("**Common to all currencies**")

    st.markdown("#### Lookback Period")
    lookback_options = ['6M', '1Y', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '11Y', '12Y', '13Y', '14Y', '15Y']
    if 'pca_lookback' not in st.session_state:
        st.session_state['pca_lookback'] = '1Y'
    lookback = st.selectbox("Select period", lookback_options, key='pca_lookback')

    st.markdown("#### PCA Settings")
    if 'pca_n_factors' not in st.session_state:
        st.session_state['pca_n_factors'] = 3
    n_factors = st.slider("Number of Factors", min_value=1, max_value=3, key='pca_n_factors')

    st.markdown("---")
    calculate_button = st.button(" Calculate All PCAs", use_container_width=True)

    st.markdown("---")
    st.markdown("#### Currency")
    if 'pca_selected_ccy' not in st.session_state:
        st.session_state['pca_selected_ccy'] = 'EUR6'
    selected_ccy = st.selectbox("Select Currency", CURRENCIES, key='pca_selected_ccy')
    
# ========== CHARGEMENT DES DONNÉES PAR CCY ==========
@st.cache_data
def load_and_process_data_for_ccy(ccy_name, lookback_period, n_factors):
    """
    Charge et traite les données PCA pour UNE devise spécifique
    """
    try:
        file_path = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\1. SWAP\SWAP_XCCY_and_SINGLE_Data_Only.xlsm'
 
        # Calculer la date de début selon le lookback
        end_date = datetime.now()
        lookback_map = {
            '6M': 6, '1Y': 12, '2Y': 24, '3Y': 36, '4Y': 48, '5Y': 60,
            '6Y': 72, '7Y': 84, '8Y': 96, '9Y': 108, '10Y': 120,
            '11Y': 132, '12Y': 144, '13Y': 156, '14Y': 168, '15Y': 180
        }
        months_back = lookback_map.get(lookback_period, 12)
        start_date = end_date - timedelta(days=months_back * 30)
 
        # === CHARGER LA FEUILLE SPÉCIFIQUE ===
        df_raw = pd.read_excel(file_path, sheet_name=ccy_name, engine='openpyxl', header=1)
 
        date_col = df_raw.columns[0]
        df_raw[date_col] = pd.to_datetime(df_raw[date_col], dayfirst=True, errors='coerce')
        df_raw = df_raw.dropna(subset=[date_col])
 
        mask = (df_raw[date_col] >= start_date) & (df_raw[date_col] <= end_date)
        df_raw = df_raw.loc[mask].reset_index(drop=True)
 
        # === AUTO-DÉTECTION COLONNES ===
        data_cols = []
        for i in range(1, len(df_raw.columns)):
            col_name = df_raw.columns[i]
            if pd.notna(col_name) and str(col_name).strip() != '':
                data_cols.append(col_name)
            else:
                break
 
        num_columns = len(data_cols)
        if num_columns == 0:
            return None
 
        df_all_raw = df_raw[[date_col] + data_cols].copy()
        df_all_raw = df_all_raw.rename(columns={date_col: 'Date'})

        # === SAUVEGARDER LES NIVEAUX RÉELS AVANT STANDARDISATION ===
        df_levels_real = df_all_raw.drop(columns=['Date'])
        means_real = df_levels_real.mean()
        stds_real = df_levels_real.std()

        # === STANDARDISATION ===
        df_zscores = (df_levels_real - means_real) / stds_real
        df_all = pd.concat([df_all_raw[['Date']], df_zscores], axis=1)

        # === CHARGER DV01 ===
        dv01_vars = {}
        try:
            df_dv01 = pd.read_excel(file_path, sheet_name='DV01', engine='openpyxl', header=3)
            dv01_row = df_dv01.iloc[0]
            for col in data_cols:
                if col in dv01_row.index:
                    dv01_vars[col] = float(dv01_row[col])
        except:
            pass
 
        # === CHARGER CARRY ===
        carry_data = {}
        carry_debug = {}
 
        try:
            carry_file = r'\\cad.local\dfsroot\GroupShares\PARIS\CAVENTOR\Analytics\5. Carry Rolls\CARRY ROLL.xlsm'
            df_carry = pd.read_excel(carry_file, sheet_name='RESULTS', engine='openpyxl')
 
            col_3m = f"{ccy_name} 3m"
            col_12m = f"{ccy_name} 12m"
 
            carry_debug['ccy'] = ccy_name
            carry_debug['col_3m'] = col_3m
            carry_debug['col_12m'] = col_12m
            carry_debug['columns_found'] = [col for col in df_carry.columns if ccy_name in str(col).upper()]
            carry_debug['col_3m_exists'] = col_3m in df_carry.columns
            carry_debug['col_12m_exists'] = col_12m in df_carry.columns
 
            if col_3m in df_carry.columns and col_12m in df_carry.columns:
                structure_col = df_carry.columns[1]
                for idx, row in df_carry.iterrows():
                    structure_name = row[structure_col]
                    if pd.notna(structure_name):
                        c3m = row[col_3m] if pd.notna(row[col_3m]) else np.nan
                        c12m = row[col_12m] if pd.notna(row[col_12m]) else np.nan
                        carry_data[str(structure_name)] = {'3m': c3m, '12m': c12m}
 
                carry_debug['structures_loaded'] = len(carry_data)
                carry_debug['sample_structures'] = list(carry_data.keys())[:5]
            else:
                carry_debug['error'] = 'Columns not found'
        except Exception as e:
            carry_debug['exception'] = str(e)
 
        # === PCA ===
        dates = df_all['Date']
        data = df_all.drop(columns=['Date'])
        column_means = data.mean()
        data_centered = data - column_means
 
        cov_matrix = data_centered.cov()
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
 
        loadings = eigenvectors[:, :n_factors]
        scores = data_centered.values @ loadings
 
        df_factors = pd.DataFrame(scores, columns=[f"Factor{i+1}" for i in range(n_factors)])
        df_factors.insert(0, "Date", dates.values)
 
        # === RECONSTRUCTION EN Z-SCORES ===
        centered_sum_mat = scores @ loadings.T
        fair_value_zscores = centered_sum_mat + column_means.values

        # === DÉ-STANDARDISATION → NIVEAUX RÉELS ===
        fair_value_real = fair_value_zscores * stds_real.values + means_real.values

        df_fair_value = pd.DataFrame(fair_value_real, columns=data.columns)
        df_fair_value.insert(0, "Date", dates.values)

        # === MISPRICING EN NIVEAUX RÉELS ===
        mispricing_real = df_levels_real.values - fair_value_real
        df_mispricing = pd.DataFrame(mispricing_real, columns=data.columns)
        df_mispricing.insert(0, "Date", dates.values)

        # === RÉSIDUS (en z-scores pour usage interne PCA) ===
        residuals_mat = data_centered.values - centered_sum_mat
        df_residuals = pd.DataFrame(residuals_mat, columns=data.columns)
        df_residuals.insert(0, "Date", dates.values)
 
        pc_labels = [f"PC{i+1}" for i in range(len(eigenvalues))]
        df_vectors = pd.DataFrame(eigenvectors, index=data.columns, columns=pc_labels)

        # df_all_real : données marché en niveaux réels (ce que tu vois sur BBG)
        df_all_real = df_all_raw.copy()

        return {
            'df_all': df_all_real,          # Niveaux réels (BBG)
            'df_all_zscore': df_all,        # Z-scores (usage interne PCA)
            'df_fair_value': df_fair_value, # Fair value en niveaux réels
            'df_mispricing': df_mispricing, # Mispricing en niveaux réels
            'df_residuals': df_residuals,
            'df_factors': df_factors,
            'df_vectors': df_vectors,
            'dv01_vars': dv01_vars,
            'dates': dates,
            'column_means': column_means,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'carry_data': carry_data,
            'ccy': ccy_name,
            'num_columns': num_columns,
            'carry_debug': carry_debug,
            'means_real': means_real,
            'stds_real': stds_real
        }
 
    except Exception as e:
        st.error(f"Error loading {ccy_name}: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None
 
# ========== FONCTION POUR CRÉER L'INTERFACE COMPLÈTE D'UN ONGLET ==========
def create_currency_tab(ccy_name, data):
    """Crée l'interface COMPLÈTE pour une devise - RIEN enlevé"""
 
    if data is None:
        st.error(f" No data available for {ccy_name}")
        return
 
    # Extraire les données
    df_all = data['df_all']           # Niveaux réels
    df_fair_value = data['df_fair_value']   # Fair value en niveaux réels
    df_mispricing = data['df_mispricing']   # Mispricing en niveaux réels
    df_residuals = data['df_residuals']
    df_vectors = data['df_vectors']
    dv01_vars = data['dv01_vars']
    dates = data['dates']
    carry_data = data.get('carry_data', {})
 
    instruments = list(df_all.columns[1:])
 
    # ========== INTERFACE DE TRADING ==========
    st.markdown(f"<h2> {ccy_name} Trading Structure Builder</h2>", unsafe_allow_html=True)
 
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
 
    with col1:
        structure_type = st.selectbox("**Type**", ['Outright', 'Curve', 'Fly'], key=f'{ccy_name}_type')
 
    with col2:
        wing1 = st.selectbox("**Wing1**", instruments, key=f'{ccy_name}_wing1')
 
    with col3:
        belly = st.selectbox("**Belly**", instruments, index=min(5, len(instruments)-1), key=f'{ccy_name}_belly')
 
    with col4:
        wing2 = st.selectbox("**Wing2**", instruments, index=min(10, len(instruments)-1), key=f'{ccy_name}_wing2')
 
    direction = 'pay belly'
 
    if structure_type == 'Outright':
        structure_title = f"{belly}"
    elif structure_type == 'Curve':
        structure_title = f"{wing1}/{belly}"
    else:
        structure_title = f"{wing1}/{belly}/{wing2}"
 
    st.markdown(f"<h2 style='text-align: center; color: #2c3e50; font-family: Source Sans Pro;'> Fair Value Analysis: {structure_title}</h2>", unsafe_allow_html=True)
    st.markdown("---")
 
    def create_fair_value_plots(type_, box1, box2, box3, direction):
        """Crée les graphiques Market vs Fair Value + Mispricing — tout en niveaux réels"""

        # Marché en niveaux réels (identique à BBG)
        market_1 = df_all[box1].values
        market_2 = df_all[box2].values
        market_3 = df_all[box3].values

        # Fair value en niveaux réels
        fv_1 = df_fair_value[box1].values
        fv_2 = df_fair_value[box2].values
        fv_3 = df_fair_value[box3].values
 
        if type_ == 'Outright':
            market_structure = market_2 * 100
            fv_structure = fv_2 * 100
            title_suffix = f"{box2}"
        elif type_ == 'Curve':
            market_structure = (market_2 - market_1) * 100
            fv_structure = (fv_2 - fv_1) * 100
            title_suffix = f"{box2} - {box1}"
        else:  # Fly
            if direction == 'pay belly':
                market_structure = (2 * market_2 - market_1 - market_3) * 100
                fv_structure = (2 * fv_2 - fv_1 - fv_3) * 100
            else:
                market_structure = (market_1 + market_3 - 2 * market_2) * 100
                fv_structure = (fv_1 + fv_3 - 2 * fv_2) * 100
            title_suffix = f"2×{box2} - {box1} - {box3}"
 
        mispricing = market_structure - fv_structure
 
        last_market = market_structure[-1]
        last_fv = fv_structure[-1]
        last_mispricing = mispricing[-1]
 
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5), dpi=120)
        fig.patch.set_facecolor('white')
 
        # ========== GRAPHIQUE 1 : MARKET VS FAIR VALUE ==========
        ax1.plot(dates, market_structure, label=f'Market: {last_market:.1f} bp', color='#e74c3c', linewidth=2.5)
        ax1.plot(dates, fv_structure, label=f'Fair Value: {last_fv:.1f} bp', color='#3498db', linewidth=2.5, linestyle='--')
        ax1.scatter(dates.iloc[-1], last_market, color='#e74c3c', s=100, zorder=5, edgecolors='white', linewidth=2)
        ax1.scatter(dates.iloc[-1], last_fv, color='#3498db', s=100, zorder=5, edgecolors='white', linewidth=2)
        ax1.set_ylabel('Basis Points (bp)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=11)
        ax1.legend(loc='best', fontsize=11, frameon=True, shadow=False)
        ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax1.tick_params(axis='x', rotation=45, labelsize=10)
        ax1.tick_params(axis='y', labelsize=10)
 
        # ========== GRAPHIQUE 2 : MISPRICING ==========
        misp_mean = mispricing.mean()
        misp_std = mispricing.std()
 
        ax2.fill_between(dates, misp_mean + misp_std, misp_mean + 2*misp_std, alpha=0.15, color='#e74c3c')
        ax2.fill_between(dates, misp_mean - misp_std, misp_mean - 2*misp_std, alpha=0.15, color='#27ae60')
        ax2.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        ax2.axhline(misp_mean, color='black', linestyle='--', linewidth=1, alpha=0.7, label=f'Mean: {misp_mean:.1f}')
        ax2.axhline(misp_mean + misp_std, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.7, label=f'+1σ: {misp_mean + misp_std:.1f}')
        ax2.axhline(misp_mean - misp_std, color='#27ae60', linestyle='--', linewidth=1, alpha=0.7, label=f'-1σ: {misp_mean - misp_std:.1f}')
        ax2.plot(dates, mispricing, label=f'Mispricing: {last_mispricing:.2f} bp', color='#9b59b6', linewidth=2.5)
        ax2.scatter(dates.iloc[-1], last_mispricing, color='#9b59b6', s=100, zorder=5, edgecolors='white', linewidth=2)
        ax2.set_ylabel('Mispricing (bp)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.legend(loc='best', fontsize=10, frameon=True, shadow=False)
        ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax2.tick_params(axis='x', rotation=45, labelsize=10)
        ax2.tick_params(axis='y', labelsize=10)
 
        plt.tight_layout()
        return fig
 
    fig = create_fair_value_plots(structure_type, wing1, belly, wing2, direction)
    st.pyplot(fig)
    plt.close()
 
    # ========== SECTION MÉTRIQUES + GRAPHIQUE YIELDS ==========
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'> Detailed Metrics & Yield Levels</h2>", unsafe_allow_html=True)
    st.markdown("---")
 
    col_table, col_graph = st.columns([1, 1.5])
 
    with col_table:
        # Marché en niveaux réels
        market_1 = df_all[wing1].values
        market_2 = df_all[belly].values
        market_3 = df_all[wing2].values
 
        if structure_type == 'Outright':
            structure_series = market_2 * 100
        elif structure_type == 'Curve':
            structure_series = (market_2 - market_1) * 100
        else:
            structure_series = (2 * market_2 - market_1 - market_3) * 100
 
        structure_df = pd.DataFrame({'Date': dates, 'Value': structure_series})
 
        # === CORRELATIONS ===
        correlations = {}
 
        def calc_correlation_252d(series1, series2):
            if len(series1) >= 252 and len(series2) >= 252:
                return np.corrcoef(series1[-252:], series2[-252:])[0, 1]
            else:
                return np.corrcoef(series1, series2)[0, 1]
 
        if '10s' in df_all.columns:
            correlations['10s'] = calc_correlation_252d(structure_series, df_all['10s'].values * 100)
        else:
            correlations['10s'] = np.nan
 
        if '2y1y' in df_all.columns:
            correlations['2y1y'] = calc_correlation_252d(structure_series, df_all['2y1y'].values * 100)
        else:
            correlations['2y1y'] = np.nan
 
        if '2s' in df_all.columns and '10s' in df_all.columns:
            curve_2s10s = (df_all['10s'].values - df_all['2s'].values) * 100
            correlations['2s10s'] = calc_correlation_252d(structure_series, curve_2s10s)
        else:
            correlations['2s10s'] = np.nan
 
        if '10s' in df_all.columns and '30s' in df_all.columns:
            curve_10s30s = (df_all['30s'].values - df_all['10s'].values) * 100
            correlations['10s30s'] = calc_correlation_252d(structure_series, curve_10s30s)
        else:
            correlations['10s30s'] = np.nan
 
        if '5s' in df_all.columns and '10s' in df_all.columns and '30s' in df_all.columns:
            fly_5s10s30s = (2 * df_all['10s'].values - df_all['5s'].values - df_all['30s'].values) * 100
            correlations['5s10s30s'] = calc_correlation_252d(structure_series, fly_5s10s30s)
        else:
            correlations['5s10s30s'] = np.nan
 
        # === Z-SCORES ===
        periods_days = {'1M': 21, '3M': 63, '6M': 126, '1Y': 252, '3Y': 756}
        zscores = {}
        percentiles = {}
 
        for period_name, days in periods_days.items():
            if len(structure_series) >= days:
                window = structure_series[-days:]
                mean = window.mean()
                std = window.std()
                last_val = window[-1]
                zscores[period_name] = (last_val - mean) / std if std != 0 else 0
                percentiles[period_name] = (window < last_val).sum() / len(window) * 100
            else:
                zscores[period_name] = np.nan
                percentiles[period_name] = np.nan
 
        # === FAIR VALUE & MISPRICING (niveaux réels) ===
        fv_1 = df_fair_value[wing1].values
        fv_2 = df_fair_value[belly].values
        fv_3 = df_fair_value[wing2].values
 
        if structure_type == 'Outright':
            fv_structure = fv_2 * 100
        elif structure_type == 'Curve':
            fv_structure = (fv_2 - fv_1) * 100
        else:
            fv_structure = (2 * fv_2 - fv_1 - fv_3) * 100
 
        fair_value_last = fv_structure[-1]
        mispricing_last = structure_series[-1] - fv_structure[-1]
 
        # === CARRY ===
        carry_3m = np.nan
        carry_12m = np.nan
 
        if carry_data:
            if structure_type == 'Outright':
                if belly in carry_data:
                    carry_3m = carry_data[belly].get('3m', np.nan)
                    carry_12m = carry_data[belly].get('12m', np.nan)
 
            elif structure_type == 'Curve':
                carry_3m_belly = carry_data.get(belly, {}).get('3m', np.nan)
                carry_3m_wing1 = carry_data.get(wing1, {}).get('3m', np.nan)
                carry_12m_belly = carry_data.get(belly, {}).get('12m', np.nan)
                carry_12m_wing1 = carry_data.get(wing1, {}).get('12m', np.nan)
                if not np.isnan(carry_3m_belly) and not np.isnan(carry_3m_wing1):
                    carry_3m = carry_3m_belly - carry_3m_wing1
                if not np.isnan(carry_12m_belly) and not np.isnan(carry_12m_wing1):
                    carry_12m = carry_12m_belly - carry_12m_wing1
 
            else:
                carry_3m_belly = carry_data.get(belly, {}).get('3m', np.nan)
                carry_3m_wing1 = carry_data.get(wing1, {}).get('3m', np.nan)
                carry_3m_wing2 = carry_data.get(wing2, {}).get('3m', np.nan)
                carry_12m_belly = carry_data.get(belly, {}).get('12m', np.nan)
                carry_12m_wing1 = carry_data.get(wing1, {}).get('12m', np.nan)
                carry_12m_wing2 = carry_data.get(wing2, {}).get('12m', np.nan)
                if not np.isnan(carry_3m_belly) and not np.isnan(carry_3m_wing1) and not np.isnan(carry_3m_wing2):
                    carry_3m = 2 * carry_3m_belly - carry_3m_wing1 - carry_3m_wing2
                if not np.isnan(carry_12m_belly) and not np.isnan(carry_12m_wing1) and not np.isnan(carry_12m_wing2):
                    carry_12m = 2 * carry_12m_belly - carry_12m_wing1 - carry_12m_wing2
 
        # ========== TABLEAU ==========
        st.markdown("### Metrics Table")
 
        table_html = """
        <style>
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Source Sans Pro', sans-serif;
            font-size: 14px;
            margin-top: 1rem;
        }
        .metrics-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #ddd;
        }
        .metrics-table td {
            padding: 10px 12px;
            border: 1px solid #ddd;
            background: white;
        }
        .metrics-table tr:hover {
            background: #e3f2fd;
        }
        .section-header {
            background: white !important;
            color: #2c3e50 !important;
            font-weight: bold !important;
            font-size: 15px !important;
            text-align: left !important;
            padding: 14px 12px !important;
            border-top: 3px solid #3498db !important;
        }
        </style>
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
        """
 
        if not np.isnan(carry_3m) or not np.isnan(carry_12m):
            table_html += '<tr class="section-header"><td colspan="2">Carry</td></tr>'
        if not np.isnan(carry_3m):
            table_html += f"<tr><td>3M</td><td>{carry_3m:.2f}</td></tr>"
        if not np.isnan(carry_12m):
            table_html += f"<tr><td>12M</td><td>{carry_12m:.2f}</td></tr>"
 
        table_html += '<tr class="section-header"><td colspan="2">Correlation 252 days</td></tr>'
        for key, val in correlations.items():
            val_str = f"{val:.3f}" if not np.isnan(val) else "N/A"
            table_html += f"<tr><td>{key}</td><td>{val_str}</td></tr>"
 
        table_html += '<tr class="section-header"><td colspan="2">Entry Level - Z-score</td></tr>'
        for period, val in zscores.items():
            val_str = f"{val:.2f}" if not np.isnan(val) else "N/A"
            table_html += f"<tr><td>{period}</td><td>{val_str}</td></tr>"
 
        table_html += '<tr class="section-header"><td colspan="2">Percentile %</td></tr>'
        for period, val in percentiles.items():
            val_str = f"{val:.1f}%" if not np.isnan(val) else "N/A"
            table_html += f"<tr><td>{period}</td><td>{val_str}</td></tr>"
 
        table_html += f'''
        <tr class="section-header">
            <td colspan="2">PCA</td>
        </tr>
        <tr><td>Fair Value (bp)</td><td>{fair_value_last:.2f}</td></tr>
        <tr><td>Mispricing (bp)</td><td>{mispricing_last:.2f}</td></tr>
        </tbody>
        </table>
        '''
 
        st.markdown(table_html, unsafe_allow_html=True)
 
    with col_graph:
        st.markdown("### Yield Levels")
 
        fig_yields, ax1 = plt.subplots(figsize=(10, 6), dpi=120)
        fig_yields.patch.set_facecolor('white')
 
        if structure_type == 'Outright':
            structure_plot = market_2 * 100
            ax1.plot(dates, market_2 * 100, label=f'{belly}', color='#3498db', linewidth=2, alpha=0.8)
            ax1.plot(dates, structure_plot, label=f'{structure_title} (Structure)', color='#e74c3c', linewidth=4, alpha=1.0, zorder=5)
            last_structure_value = structure_plot[-1]
            ax1.scatter(dates.iloc[-1], last_structure_value, color='#c0392b', s=150, zorder=10, edgecolors='white', linewidth=2)
            ax1.annotate(f'{last_structure_value:.2f}', xy=(dates.iloc[-1], last_structure_value),
                xytext=(10, 0), textcoords='offset points', fontsize=11, fontweight='bold', color='#c0392b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e74c3c', linewidth=2),
                verticalalignment='center')
            ax1.set_ylabel('Yield (%)', fontsize=12, fontweight='bold')
            ax1.legend(loc='best', fontsize=10, frameon=True)
 
        elif structure_type == 'Curve':
            structure_plot = (market_2 - market_1) * 100
            ax1.plot(dates, structure_plot, label=f'{structure_title} (Structure)', color='#e74c3c', linewidth=4, alpha=1.0, zorder=5)
            last_structure_value = structure_plot[-1]
            ax1.scatter(dates.iloc[-1], last_structure_value, color='#c0392b', s=150, zorder=10, edgecolors='white', linewidth=2)
            ax1.annotate(f'{last_structure_value:.2f}', xy=(dates.iloc[-1], last_structure_value),
                xytext=(10, 0), textcoords='offset points', fontsize=11, fontweight='bold', color='#c0392b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e74c3c', linewidth=2),
                verticalalignment='center')
            ax1.set_ylabel('Structure (bp)', fontsize=12, fontweight='bold', color='#e74c3c')
            ax1.tick_params(axis='y', labelcolor='#e74c3c')
            ax2 = ax1.twinx()
            ax2.plot(dates, market_1 * 100, label=f'{wing1}', color='#3498db', linewidth=2, alpha=0.8)
            ax2.plot(dates, market_2 * 100, label=f'{belly}', color='#e67e22', linewidth=2, alpha=0.8)
            ax2.set_ylabel('Yield Levels (%)', fontsize=12, fontweight='bold', color='#34495e')
            ax2.tick_params(axis='y', labelcolor='#34495e')
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10, frameon=True)
 
        else:  # Fly
            structure_plot = (2 * market_2 - market_1 - market_3) * 100
            ax1.plot(dates, structure_plot, label=f'{structure_title} (Structure)', color='#e74c3c', linewidth=4, alpha=1.0, zorder=5)
            last_structure_value = structure_plot[-1]
            ax1.scatter(dates.iloc[-1], last_structure_value, color='#c0392b', s=150, zorder=10, edgecolors='white', linewidth=2)
            ax1.annotate(f'{last_structure_value:.2f}', xy=(dates.iloc[-1], last_structure_value),
                xytext=(10, 0), textcoords='offset points', fontsize=11, fontweight='bold', color='#c0392b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e74c3c', linewidth=2),
                verticalalignment='center')
            ax1.set_ylabel('Structure (bp)', fontsize=12, fontweight='bold', color='#e74c3c')
            ax1.tick_params(axis='y', labelcolor='#e74c3c')
            ax2 = ax1.twinx()
            ax2.plot(dates, market_1 * 100, label=f'{wing1}', color='#3498db', linewidth=2, alpha=0.8)
            ax2.plot(dates, market_2 * 100, label=f'{belly}', color='#e67e22', linewidth=2, alpha=0.8)
            ax2.plot(dates, market_3 * 100, label=f'{wing2}', color='#9b59b6', linewidth=2, alpha=0.8)
            ax2.set_ylabel('Yield Levels (%)', fontsize=12, fontweight='bold', color='#34495e')
            ax2.tick_params(axis='y', labelcolor='#34495e')
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10, frameon=True)
 
        ax1.set_xlabel('Date', fontsize=11)
        ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax1.tick_params(axis='x', rotation=45, labelsize=10)
        ax1.tick_params(axis='y', labelsize=10)
        plt.tight_layout()
        st.pyplot(fig_yields)
        plt.close()
 
    # ========== MÉTRIQUES CLÉS ==========
    st.markdown("<h3> Key Metrics</h3>", unsafe_allow_html=True)
 
    col1, col2, col3, col4 = st.columns(4)
 
    with col1:
        variance_pc1 = (data['eigenvalues'][0] / data['eigenvalues'].sum() * 100)
        st.metric("PC1 Variance", f"{variance_pc1:.1f}%", delta="Primary factor", delta_color="off")
 
    with col2:
        variance_pc2 = (data['eigenvalues'][1] / data['eigenvalues'].sum() * 100)
        st.metric("PC2 Variance", f"{variance_pc2:.1f}%", delta="Secondary factor", delta_color="off")
 
    with col3:
        variance_pc3 = (data['eigenvalues'][2] / data['eigenvalues'].sum() * 100)
        st.metric("PC3 Variance", f"{variance_pc3:.1f}%", delta="Tertiary factor", delta_color="off")
 
    with col4:
        total_variance = variance_pc1 + variance_pc2 + variance_pc3
        st.metric("Total Explained", f"{total_variance:.1f}%", delta="Model quality", delta_color="normal")

    # ========== BAR CHART MISPRICING PAR INSTRUMENT ==========
    st.markdown("<h3> Mispricing par instrument (last) — bp</h3>", unsafe_allow_html=True)
    st.markdown("---")

    last_mispricing_row = df_mispricing.drop(columns=['Date']).iloc[-1] * 100
    instruments_list = list(last_mispricing_row.index)
    mispricing_values = last_mispricing_row.values

    colors = ['#e74c3c' if v > 0 else '#27ae60' for v in mispricing_values]

    fig_bar, ax_bar = plt.subplots(figsize=(16, 5), dpi=120)
    fig_bar.patch.set_facecolor('white')

    bars = ax_bar.bar(instruments_list, mispricing_values, color=colors, edgecolor='white', linewidth=0.8, zorder=3)

    ax_bar.axhline(0, color='black', linewidth=1.2, zorder=4)
    ax_bar.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, zorder=0)

    for bar, val in zip(bars, mispricing_values):
        ax_bar.text(
            bar.get_x() + bar.get_width() / 2,
            val + (0.3 if val >= 0 else -0.3),
            f'{val:.1f}',
            ha='center', va='bottom' if val >= 0 else 'top',
            fontsize=9, fontweight='bold',
            color='#2c3e50'
        )

    ax_bar.set_ylabel('Mispricing (bp)', fontsize=12, fontweight='bold')
    ax_bar.set_xlabel('Instrument', fontsize=11)
    ax_bar.tick_params(axis='x', rotation=45, labelsize=10)
    ax_bar.tick_params(axis='y', labelsize=10)
    ax_bar.set_facecolor('#fafafa')

    plt.tight_layout()
    st.pyplot(fig_bar)
    plt.close()
 
 
# ========== CALCUL ET AFFICHAGE DES 10 ONGLETS ==========

# Détecter si les paramètres ont changé → forcer recalcul
current_params = f"{lookback}_{n_factors}"
params_changed = st.session_state.get('pca_last_params') != current_params

if calculate_button:
    # Recalcul forcé si bouton cliqué
    with st.spinner(' Calculating PCAs for all 10 currencies...'):
        all_data = {}
        success_count = 0
        for ccy in CURRENCIES:
            data = load_and_process_data_for_ccy(ccy, lookback, n_factors)
            all_data[ccy] = data
            if data is not None:
                success_count += 1

    st.session_state['pca_all_data'] = all_data
    st.session_state['pca_last_params'] = current_params
    st.success(f' {success_count}/{len(CURRENCIES)} PCAs calculated successfully!')

if 'pca_all_data' in st.session_state:
    all_data = st.session_state['pca_all_data']
    data = all_data.get(selected_ccy)
    create_currency_tab(selected_ccy, data)

else:
    # ========== ÉCRAN D'ACCUEIL ==========
    st.info(" Please configure your parameters in the sidebar and click **Calculate All PCAs** to start the analysis.")
 
    st.markdown("""
    ### Features
    
    - **10 Independent PCA Models**: EUR6, EUR-OIS, USD, GBP, AUD, NZD, CHF, CAD, JPY, SEK, NOK
    - **Flexible Lookback Periods**: From 6 months to 15 years
    - **Advanced PCA Analysis**: Up to 3 principal components
    - **Real-time Fair Value**: Market vs PCA-based fair value (in real bp)
    - **Mispricing Detection**: Statistical bands (±1σ, ±2σ)
    - **Trading Structure Builder**: Outrights, Curves, Flies
    - **Detailed Metrics**: Correlations, Z-scores, Percentiles, Carry (3M/12M)
    - **Yield Levels Graphs**: Dual-axis visualization
    
    ### How to Use
    
    1. Select your **lookback period** (6M to 15Y) - applies to all currencies
    2. Choose the **number of PCA factors** (1-3) - applies to all currencies
    3. Click **Calculate All PCAs**
    4. Navigate between currency tabs **without recalculating**
    5. Build your trading structures in each tab
    6. Analyze fair value and mispricing independently for each currency
    
    ---
    *Powered by Advanced Principal Component Analysis*
    """)
 
st.markdown("---")
st.markdown("<p style='text-align: center; color: #95a5a6; font-size: 0.9rem;'>© 2026 Multi-Currency PCA Fair Value Analysis | Built with Streamlit</p>", unsafe_allow_html=True)
