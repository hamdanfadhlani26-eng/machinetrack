import streamlit as st

def inject():
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>

    /* ── ROOT VARIABLES ──────────────────────────────────── */
    :root {
        --bg-base:      #0a0e1a;
        --bg-surface:   #0f1629;
        --bg-card:      #131d35;
        --bg-hover:     #1a2540;
        --border:       #1e2d4a;
        --border-light: #253352;
        --amber:        #f59e0b;
        --amber-dim:    #d97706;
        --amber-glow:   rgba(245,158,11,0.12);
        --amber-glow2:  rgba(245,158,11,0.06);
        --text-primary: #e8edf5;
        --text-secondary:#8899bb;
        --text-muted:   #4a5d80;
        --green:        #10b981;
        --red:          #ef4444;
        --blue:         #3b82f6;
    }

    /* ── GLOBAL ──────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .stApp {
        background-color: var(--bg-base) !important;
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(245,158,11,0.04) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 100%, rgba(59,130,246,0.04) 0%, transparent 60%);
    }

    /* ── SIDEBAR ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* Radio buttons di sidebar */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background: var(--amber-glow2) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] .stRadio [data-checked="true"] + label,
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: var(--amber-glow) !important;
        border-color: var(--amber-dim) !important;
        color: var(--amber) !important;
    }

    /* Hide radio circles */
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
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid var(--border) !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: var(--amber) !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
        margin-top: 1.5rem !important;
    }

    h3 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    /* ── CAPTION & SMALL TEXT ────────────────────────────── */
    .stCaption, small, caption {
        color: var(--text-muted) !important;
        font-size: 0.78rem !important;
    }

    /* ── METRIC CARDS ────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        transition: border-color 0.2s !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--amber-dim) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: var(--amber) !important;
    }

    /* ── BUTTONS ─────────────────────────────────────────── */
    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.02em !important;
    }

    .stButton > button:hover {
        background: var(--amber-glow) !important;
        border-color: var(--amber) !important;
        color: var(--amber) !important;
        box-shadow: 0 0 20px var(--amber-glow) !important;
    }

    .stButton > button:active {
        background: var(--amber-glow2) !important;
        transform: scale(0.98) !important;
    }

    /* Primary button (full width) */
    .stButton > button[kind="primary"] {
        background: var(--amber-glow) !important;
        border-color: var(--amber) !important;
        color: var(--amber) !important;
    }

    /* ── SELECTBOX / DROPDOWN ────────────────────────────── */
    .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox > div > div:focus-within {
        border-color: var(--amber-dim) !important;
        box-shadow: 0 0 0 2px var(--amber-glow) !important;
    }

    /* ── TEXT INPUT ──────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.88rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--amber-dim) !important;
        box-shadow: 0 0 0 2px var(--amber-glow) !important;
    }

    /* ── DATAFRAME / TABLE ───────────────────────────────── */
    [data-testid="stDataFrame"],
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        background: var(--bg-card) !important;
    }

    /* ── TABS ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        color: var(--text-muted) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: var(--amber-glow2) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--amber) !important;
        border-bottom-color: var(--amber) !important !important;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding: 1.5rem 0 !important;
    }

    /* ── ALERTS / NOTIFICATIONS ──────────────────────────── */
    .stSuccess {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.3) !important;
        border-radius: 8px !important;
        color: #6ee7b7 !important;
    }

    .stError {
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
        border-radius: 8px !important;
        color: #fca5a5 !important;
    }

    .stWarning {
        background: rgba(245,158,11,0.08) !important;
        border: 1px solid rgba(245,158,11,0.3) !important;
        border-radius: 8px !important;
        color: #fcd34d !important;
    }

    .stInfo {
        background: rgba(59,130,246,0.08) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        border-radius: 8px !important;
        color: #93c5fd !important;
    }

    /* ── EXPANDER ────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--amber-dim) !important;
        color: var(--amber) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }

    /* ── RADIO BUTTONS (inline) ──────────────────────────── */
    .stRadio > div {
        gap: 8px !important;
    }

    .stRadio label {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 6px 14px !important;
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }

    .stRadio label:hover {
        border-color: var(--amber-dim) !important;
        color: var(--text-primary) !important;
    }

    /* ── CHECKBOX ────────────────────────────────────────── */
    .stCheckbox label {
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
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
        color: var(--amber) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
        padding: 2px 6px !important;
    }

    /* ── MULTISELECT ─────────────────────────────────────── */
    .stMultiSelect > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── DATE & TIME INPUT ───────────────────────────────── */
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* ── FORM ────────────────────────────────────────────── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
    }

    /* ── SCROLLBAR ───────────────────────────────────────── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-base);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-light);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* ── LABEL STYLING ───────────────────────────────────── */
    label[data-testid="stWidgetLabel"],
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stTextArea label {
        color: var(--text-muted) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    /* ── PLOTLY CHART BACKGROUND ─────────────────────────── */
    .js-plotly-plot {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ── SIDEBAR BRAND ───────────────────────────────────── */
    .sidebar-brand {
        padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }

    .sidebar-brand h2 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: var(--amber) !important;
        margin: 0 !important;
        text-transform: none !important;
        letter-spacing: -0.01em !important;
    }

    .sidebar-brand p {
        font-size: 0.72rem !important;
        color: var(--text-muted) !important;
        margin: 2px 0 0 0 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }

    /* ── PAGE HEADER COMPONENT ───────────────────────────── */
    .page-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }

    .page-header-icon {
        font-size: 1.4rem;
    }

    .page-header-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .page-header-subtitle {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin: 0;
        letter-spacing: 0.04em;
    }

    /* ── STEP BADGE ──────────────────────────────────────── */
    .step-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--amber-glow);
        border: 1px solid var(--amber-dim);
        border-radius: 6px;
        padding: 4px 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--amber);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 1rem 0 0.5rem 0;
        width: fit-content;
    }

    /* ── STATUS BADGE ────────────────────────────────────── */
    .badge-accept {
        display: inline-block;
        background: rgba(16,185,129,0.12);
        border: 1px solid rgba(16,185,129,0.4);
        color: #6ee7b7;
        border-radius: 20px;
        padding: 3px 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .badge-reject {
        display: inline-block;
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.4);
        color: #fca5a5;
        border-radius: 20px;
        padding: 3px 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ── VERDICT BOX ─────────────────────────────────────── */
    .verdict-accept {
        background: rgba(16,185,129,0.07);
        border: 1px solid rgba(16,185,129,0.35);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    .verdict-reject {
        background: rgba(239,68,68,0.07);
        border: 1px solid rgba(239,68,68,0.35);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    .verdict-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        margin: 0 0 4px 0;
    }

    .verdict-body {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.5;
    }

    /* ── SIDEBAR VERSION ─────────────────────────────────── */
    .sidebar-version {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
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