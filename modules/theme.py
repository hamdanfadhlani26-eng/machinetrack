import streamlit as st

def inject():
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Nunito:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>

    /* ── ROOT VARIABLES ──────────────────────────────────── */
    :root {
        --bg-base:       #f0ede8;
        --bg-surface:    #f7f5f2;
        --bg-card:       #ffffff;
        --bg-hover:      #ede9e3;
        --border:        #d6cfc6;
        --border-light:  #e2dbd3;
        --accent:        #b45309;
        --accent-dim:    #92400e;
        --accent-glow:   rgba(180,83,9,0.10);
        --accent-glow2:  rgba(180,83,9,0.05);
        --text-primary:  #1c1917;
        --text-secondary:#44403c;
        --text-muted:    #78716c;
        --green:         #15803d;
        --green-bg:      rgba(21,128,61,0.08);
        --red:           #b91c1c;
        --red-bg:        rgba(185,28,28,0.08);
        --blue:          #1d4ed8;
        --blue-bg:       rgba(29,78,216,0.08);
        --shadow-sm:     0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md:     0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
    }

    /* ── GLOBAL ──────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background-color: var(--bg-base) !important;
        background-image:
            radial-gradient(ellipse at 10% 0%, rgba(180,83,9,0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 100%, rgba(29,78,216,0.03) 0%, transparent 50%);
    }

    /* ── SIDEBAR ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #faf8f5 !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 2px 0 8px rgba(0,0,0,0.06) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 11px 14px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: var(--accent-glow2) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] .stRadio [data-checked="true"] + label,
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: var(--accent-glow) !important;
        border-color: var(--accent) !important;
        color: var(--accent-dim) !important;
    }

    [data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none !important;
    }

    /* ── MAIN CONTENT AREA ───────────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1400px !important;
    }

    /* ── HEADINGS ────────────────────────────────────────── */
    h1 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--border) !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: var(--accent-dim) !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
        margin-top: 1.5rem !important;
    }

    h3 {
        font-family: 'Nunito', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    /* ── CAPTION & SMALL TEXT ────────────────────────────── */
    .stCaption, small, caption {
        color: var(--text-muted) !important;
        font-size: 0.82rem !important;
    }

    /* ── METRIC CARDS ────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.1rem 1.3rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.2s, border-color 0.2s !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--accent) !important;
        box-shadow: var(--shadow-md) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--accent-dim) !important;
    }

    /* ── BUTTONS ─────────────────────────────────────────── */
    .stButton > button {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        background: var(--accent-glow) !important;
        border-color: var(--accent) !important;
        color: var(--accent-dim) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border-color: var(--accent-dim) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--accent-dim) !important;
        box-shadow: 0 4px 12px rgba(180,83,9,0.25) !important;
    }

    /* ── SELECTBOX / DROPDOWN ────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 0.92rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stSelectbox > div > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* ── TEXT INPUT ──────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.92rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }

    /* ── DATAFRAME / TABLE ───────────────────────────────── */
    [data-testid="stDataFrame"],
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── TABS ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-surface) !important;
        border-bottom: 2px solid var(--border) !important;
        border-radius: 8px 8px 0 0 !important;
        gap: 0 !important;
        padding: 0 8px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        color: var(--text-muted) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.3rem !important;
        transition: all 0.2s !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: var(--accent-glow2) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent-dim) !important;
        border-bottom-color: var(--accent) !important;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding: 1.5rem 0 !important;
        background: transparent !important;
    }

    /* ── ALERTS / NOTIFICATIONS ──────────────────────────── */
    .stSuccess {
        background: var(--green-bg) !important;
        border: 1px solid rgba(21,128,61,0.3) !important;
        border-left: 4px solid var(--green) !important;
        border-radius: 8px !important;
        color: var(--green) !important;
        font-weight: 600 !important;
    }

    .stError {
        background: var(--red-bg) !important;
        border: 1px solid rgba(185,28,28,0.3) !important;
        border-left: 4px solid var(--red) !important;
        border-radius: 8px !important;
        color: var(--red) !important;
        font-weight: 600 !important;
    }

    .stWarning {
        background: rgba(180,83,9,0.07) !important;
        border: 1px solid rgba(180,83,9,0.25) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 8px !important;
        color: var(--accent-dim) !important;
        font-weight: 600 !important;
    }

    .stInfo {
        background: var(--blue-bg) !important;
        border: 1px solid rgba(29,78,216,0.25) !important;
        border-left: 4px solid var(--blue) !important;
        border-radius: 8px !important;
        color: var(--blue) !important;
        font-weight: 600 !important;
    }

    /* ── EXPANDER ────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--accent) !important;
        color: var(--accent-dim) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }

    /* ── RADIO BUTTONS (inline) ──────────────────────────── */
    .stRadio > div { gap: 8px !important; }

    .stRadio label {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 7px 16px !important;
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stRadio label:hover {
        border-color: var(--accent) !important;
        color: var(--accent-dim) !important;
    }

    /* ── CHECKBOX ────────────────────────────────────────── */
    .stCheckbox label {
        color: var(--text-secondary) !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }

    /* ── DIVIDER ─────────────────────────────────────────── */
    hr {
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── CODE / INLINE CODE ──────────────────────────────── */
    code {
        background: var(--bg-hover) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        color: var(--accent-dim) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        padding: 2px 6px !important;
    }

    /* ── MULTISELECT ─────────────────────────────────────── */
    .stMultiSelect > div > div {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── DATE & TIME INPUT ───────────────────────────────── */
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.92rem !important;
    }

    /* ── FORM ────────────────────────────────────────────── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── SCROLLBAR ───────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* ── LABEL STYLING ───────────────────────────────────── */
    label[data-testid="stWidgetLabel"],
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stTextArea label {
        color: var(--text-secondary) !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.80rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    /* ── PLOTLY CHART ────────────────────────────────────── */
    .js-plotly-plot {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── SIDEBAR BRAND ───────────────────────────────────── */
    .sidebar-brand {
        padding: 0.5rem 0 1rem 0;
        border-bottom: 2px solid var(--border);
        margin-bottom: 1rem;
    }

    .sidebar-brand h2 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: var(--accent-dim) !important;
        margin: 0 !important;
        text-transform: none !important;
        letter-spacing: -0.01em !important;
    }

    .sidebar-brand p {
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        margin: 3px 0 0 0 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }

    /* ── PAGE HEADER COMPONENT ───────────────────────────── */
    .page-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border);
    }

    .page-header-icon { font-size: 1.5rem; }

    .page-header-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .page-header-subtitle {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin: 0;
        letter-spacing: 0.04em;
        font-weight: 500;
    }

    /* ── STEP BADGE ──────────────────────────────────────── */
    .step-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--accent-glow);
        border: 1.5px solid var(--accent);
        border-radius: 6px;
        padding: 5px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--accent-dim);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1rem 0 0.5rem 0;
        width: fit-content;
        box-shadow: var(--shadow-sm);
    }

    /* ── STATUS BADGE ────────────────────────────────────── */
    .badge-accept {
        display: inline-block;
        background: var(--green-bg);
        border: 1.5px solid rgba(21,128,61,0.4);
        color: var(--green);
        border-radius: 20px;
        padding: 3px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .badge-reject {
        display: inline-block;
        background: var(--red-bg);
        border: 1.5px solid rgba(185,28,28,0.4);
        color: var(--red);
        border-radius: 20px;
        padding: 3px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* ── VERDICT BOX ─────────────────────────────────────── */
    .verdict-accept {
        background: var(--green-bg);
        border: 1px solid rgba(21,128,61,0.3);
        border-left: 5px solid var(--green);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    .verdict-reject {
        background: var(--red-bg);
        border: 1px solid rgba(185,28,28,0.3);
        border-left: 5px solid var(--red);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    .verdict-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0 0 4px 0;
        color: var(--text-primary);
    }

    .verdict-body {
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.6;
        font-weight: 500;
    }

    /* ── SIDEBAR VERSION ─────────────────────────────────── */
    .sidebar-version {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.70rem;
        color: var(--text-muted);
        text-align: center;
        letter-spacing: 0.06em;
        padding-top: 0.5rem;
    }

    /* ── DATA EDITOR ─────────────────────────────────────── */
    [data-testid="stDataEditor"] {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    </style>
    """)


def page_header(icon: str, title: str, subtitle: str = ""):
    sub = f'<p class="page-header-subtitle">{subtitle}</p>' if subtitle else ''
    st.html(f"""
    <div class="page-header">
        <span class="page-header-icon">{icon}</span>
        <div>
            <p class="page-header-title">{title}</p>
            {sub}
        </div>
    </div>
    """)


def step_badge(number: str, label: str):
    st.html(f"""
    <div class="step-badge">
        <span>{number}</span>
        <span>{label}</span>
    </div>
    """)


def verdict(accept: bool, title: str, body: str):
    cls  = "verdict-accept" if accept else "verdict-reject"
    icon = "✅" if accept else "❌"
    st.html(f"""
    <div class="{cls}">
        <p class="verdict-title">{icon} {title}</p>
        <p class="verdict-body">{body}</p>
    </div>
    """)