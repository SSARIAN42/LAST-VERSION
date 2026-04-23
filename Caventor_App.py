import streamlit as st

st.set_page_config(
    page_title="CAVENTOR Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #03112b;
    color: #e8f4fd;
}
.stApp { background-color: #03112b; }

section[data-testid="stSidebar"] {
    background-color: #0a1628 !important;
    border-right: 1px solid #1a3a5c !important;
}
section[data-testid="stSidebar"] * { color: #e8f4fd !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #0f2040 !important;
    border: 1px solid #1a3a5c !important;
    border-radius: 3px !important;
}
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #0f2040 !important;
    border: 1px solid #1a3a5c !important;
    border-radius: 3px !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #00aaff !important;
    color: #03112b !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 0.5rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #33bbff !important;
    box-shadow: 0 0 10px rgba(0,170,255,0.4) !important;
}
div[data-baseweb="select"] > div {
    background-color: #0f2040;
    border: 1px solid #1a3a5c;
    border-radius: 3px;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: #00aaff !important;
    color: #03112b !important;
    border-radius: 3px !important;
    border: none !important;
}
.stMultiSelect [data-baseweb="tag"] span { color: #03112b !important; font-weight: 600 !important; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #03112b 0%, #0a2a5e 50%, #03112b 100%);
    border: 1px solid #1a3a5c;
    border-radius: 12px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,170,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-tag {
    display: inline-block;
    background: rgba(0,170,255,0.12);
    border: 1px solid rgba(0,170,255,0.3);
    color: #00aaff;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 2px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    line-height: 1.15;
    margin: 0 0 0.5rem 0;
}
.hero-title span {
    color: #00aaff;
}
.hero-subtitle {
    font-size: 1rem;
    font-weight: 300;
    color: rgba(232,244,253,0.55);
    letter-spacing: 0.3px;
    margin: 0;
}
.hero-divider {
    width: 48px;
    height: 3px;
    background: linear-gradient(90deg, #00aaff, transparent);
    margin: 1.2rem 0;
    border-radius: 2px;
}

/* Section title */
.section-title {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(0,170,255,0.7);
    margin-bottom: 1rem;
}

/* Tool cards */
.tool-card {
    background: linear-gradient(145deg, #071830 0%, #0a2040 100%);
    border: 1px solid #1a3a5c;
    border-radius: 8px;
    padding: 1.6rem 1.8rem;
    height: 100%;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.tool-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 8px 0 0 8px;
}
.tool-card.pca::after    { background: #00aaff; }
.tool-card.reg::after    { background: #4fc3f7; }
.tool-card.seas::after   { background: #29b6f6; }

.tool-icon {
    font-size: 1.6rem;
    margin-bottom: 0.8rem;
    display: block;
}
.tool-name {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #00aaff;
    margin-bottom: 0.4rem;
}
.tool-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.8rem;
    line-height: 1.3;
}
.tool-desc {
    font-size: 0.82rem;
    color: rgba(232,244,253,0.5);
    line-height: 1.65;
    margin-bottom: 1.1rem;
}
.feature-list {
    list-style: none;
    padding: 0; margin: 0;
}
.feature-list li {
    font-size: 0.78rem;
    color: rgba(232,244,253,0.45);
    padding: 0.22rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
}
.feature-list li::before {
    content: '—';
    color: #00aaff;
    opacity: 0.5;
    flex-shrink: 0;
    margin-top: 1px;
}

/* Stats strip */
.stats-strip {
    background: linear-gradient(90deg, #071830, #0a2040, #071830);
    border: 1px solid #1a3a5c;
    border-radius: 8px;
    padding: 1.2rem 2rem;
    display: flex;
    justify-content: space-around;
    margin: 2.5rem 0;
}
.stat-item { text-align: center; }
.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #00aaff;
    display: block;
    letter-spacing: -0.5px;
}
.stat-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(232,244,253,0.35);
    margin-top: 0.2rem;
    display: block;
}
.stat-sep {
    width: 1px;
    background: #1a3a5c;
    margin: 0.2rem 0;
}

/* Footer */
.footer {
    border-top: 1px solid #1a3a5c;
    padding-top: 1.2rem;
    margin-top: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-left {
    font-size: 0.72rem;
    color: rgba(232,244,253,0.25);
    letter-spacing: 0.3px;
}
.footer-right {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(0,170,255,0.4);
}

/* Nav hint */
.nav-hint {
    background: rgba(0,170,255,0.06);
    border: 1px solid rgba(0,170,255,0.15);
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    font-size: 0.78rem;
    color: rgba(232,244,253,0.45);
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">Caventor Capital · Analytics Suite</div>
    <div class="hero-title">CAVENTOR <span>ANALYTICS</span></div>
    <div class="hero-divider"></div>
    <div class="hero-subtitle">
        Inventing Cross-Asset Liquidity and Alpha &nbsp;·&nbsp;
        Fixed Income &amp; Interest Rate Derivatives
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAV HINT ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-hint">
    ← Navigate to each tool using the sidebar on the left
</div>
""", unsafe_allow_html=True)

# ── STATS STRIP ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-strip">
    <div class="stat-item">
        <span class="stat-value">10</span>
        <span class="stat-label">G10 Currencies</span>
    </div>
    <div class="stat-sep"></div>
    <div class="stat-item">
        <span class="stat-value">5</span>
        <span class="stat-label">Analytics Tools</span>
    </div>
    <div class="stat-sep"></div>
    <div class="stat-item">
        <span class="stat-value">15Y</span>
        <span class="stat-label">Max Lookback</span>
    </div>
    <div class="stat-sep"></div>
    <div class="stat-item">
        <span class="stat-value">OIS</span>
        <span class="stat-label">Rate Universe</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TOOL CARDS ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Available Tools</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5, gap="medium")

with col1:
    st.markdown("""
    <div class="tool-card pca">
        <span class="tool-icon">📐</span>
        <div class="tool-name">Tool 01</div>
        <div class="tool-title">PCA Fair Value Analysis</div>
        <div class="tool-desc">
            Multi-currency Principal Component Analysis across 10 independent G10 models.
            Identifies mispricings in real basis points against a PCA-reconstructed fair value.
        </div>
        <ul class="feature-list">
            <li>G10 rates</li>
            <li>Outright · Curve · Fly structure builder</li>
            <li>3 PCA factors — level, slope, curvature</li>
            <li>Fair value in real bp — dé-standardised output</li>
            <li>Mispricing bar chart per instrument</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tool-card reg">
        <span class="tool-icon">📈</span>
        <div class="tool-name">Tool 02</div>
        <div class="tool-title">Regression Driver Analysis</div>
        <div class="tool-desc">
            OLS regression engine mapping any G10 rate structure or cross-market spread
            against a library of 400+ regressors across multiple asset groups.
        </div>
        <ul class="feature-list">
            <li>Single CCY or XMkt dependent variable</li>
            <li>400+ regressors — grouped by asset class</li>
            <li>OLS · R² ranking · Corr 252d</li>
            <li>Scatter plot with 21d recency highlight</li>
            <li>Residuals timeseries · last residual in bp</li>
            <li>Composite RSI + Z-score signal overlay</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="tool-card seas">
        <span class="tool-icon">📅</span>
        <div class="tool-name">Tool 03</div>
        <div class="tool-title">Seasonality Analysis</div>
        <div class="tool-desc">
            Statistical seasonality engine covering monthly, quarterly, semester and annual
            patterns across a broad universe of rates products.
        </div>
        <ul class="feature-list">
            <li>Month · Quarter · Semester · Year · Custom</li>
            <li>First / Last N days or weeks windows</li>
            <li>Spaghetti chart — all historical instances</li>
            <li>Heatmap — progressive windows by year</li>
            <li>Bull & Bear top-15 ranking tables</li>
            <li>Success rate · G/L ratio · Avg gain in bp</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="tool-card pca">
        <span class="tool-icon">⚡</span>
        <div class="tool-name">Tool 04</div>
        <div class="tool-title">Metrics & Backtest</div>
        <div class="tool-desc">
            Real-time market metrics and multi-horizon backtesting engine for any
            G10 rate structure or cross-market spread.
        </div>
        <ul class="feature-list">
            <li>Z-score · Yield Ratio · RSI · BB Position</li>
            <li>Mean-Reversion score — multi-window AR(1)</li>
            <li>Vol 3w/3m · MR Score</li>
            <li>Backtest 1M / 3M / 6M horizons</li>
            <li>Vol-adjusted RR ratio with proba weighting</li>
            <li>Expected win & stop loss in bp</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="tool-card seas">
        <span class="tool-icon">🔍</span>
        <div class="tool-name">Tool 05</div>
        <div class="tool-title">Relative Value Screener</div>
        <div class="tool-desc">
            Screener de relative value : trouve les structures les plus cheap ou riches
            pour exprimer une vue macro, sans beta-weighting.
        </div>
        <ul class="feature-list">
            <li>147 structures par CCY — spot, fly, fwd, spot fwdé</li>
            <li>Régression OLS 1-for-1 vs asset macro</li>
            <li>Z-score · Percentile · Vol 1M/3M/6M + lookback</li>
            <li>Carry 3M/12M · Carry/Vol · Half-life</li>
            <li>Résidu last · Corr 252j/126j</li>
            <li>Scatter + résidus sur sélection</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-left">© 2026 Caventor Capital · Internal Analytics Platform · Confidential</div>
    <div class="footer-right">Fixed Income · IR Derivatives</div>
</div>
""", unsafe_allow_html=True)
