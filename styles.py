import streamlit as st

def inject_styles(is_dark=True):
    """
    Unified Single CSS Block for MAH-CET Analytics Dashboard.
    Uses CSS custom properties (:root) so theme switching dynamically updates
    all cards, tables, backgrounds, metrics, and navigation tabs at once!
    """
    bg_color = "#09090b" if is_dark else "#f8fafc"
    bg_subtle = "#0c0c0f" if is_dark else "#f1f5f9"
    card_bg = "#111115" if is_dark else "#ffffff"
    card_hover = "#16161c" if is_dark else "#f8fafc"
    border_color = "#27272a" if is_dark else "#cbd5e1"
    border_subtle = "#1e1e24" if is_dark else "#e2e8f0"
    text_color = "#fafafa" if is_dark else "#0f172a"
    text_muted = "#a1a1aa" if is_dark else "#475569"
    text_dim = "#71717a" if is_dark else "#64748b"
    accent_light = "#1e3a8a" if is_dark else "#dbeafe"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');

    :root {{
        --bg: {bg_color};
        --bg-subtle: {bg_subtle};
        --card: {card_bg};
        --card-hover: {card_hover};
        --border: {border_color};
        --border-subtle: {border_subtle};
        --text: {text_color};
        --text-muted: {text_muted};
        --text-dim: {text_dim};
        --accent: #2563eb;
        --accent-light: {accent_light};
        --radius: 12px;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, section[data-testid="stMain"] {{
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}

    /* Sidebar Background & Text - High-Contrast Synchronization */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    div[data-testid="stSidebarContent"],
    div[data-testid="stSidebarHeader"],
    div[data-testid="stSidebarUserContent"],
    [data-testid="stSidebarNav"] {{
        background-color: {"#0d0e12" if is_dark else "#f1f5f9"} !important;
        color: {"#f8fafc" if is_dark else "#0f172a"} !important;
    }}

    section[data-testid="stSidebar"] {{
        border-right: 1px solid {"#27272a" if is_dark else "#cbd5e1"} !important;
    }}

    /* Sidebar Headings, Labels, Markdown & Radio Option Text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: {"#f8fafc" if is_dark else "#0f172a"} !important;
    }}


    /* Hide top header bar, Fork button, GitHub icon, and Main Menu 3-dots button */
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stHeaderForkButton"],
    .stAppHeader,
    #MainMenu,
    .stDeployButton,
    button[aria-label*="Fork"],
    button[title*="Fork"],
    a[title*="Fork"],
    a[href*="github.com"],
    button[aria-label*="View app source"],
    button[aria-label*="Main menu"],
    div[class*="actionElements"],
    div[class*="headerAction"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }}

    /* Ensure sidebar collapse / expand toggle button is ALWAYS visible & clickable */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }}




    /* Global Container Spacing */
    .block-container {{
        padding: 1.5rem 1.5rem 2.5rem !important;
        max-width: 1440px !important;
    }}

    /* Clean Buttons */
    button[data-baseweb="button"], .stButton > button {{
        background-color: var(--bg-subtle) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        font-size: 0.78rem !important;
    }}
    button[data-baseweb="button"]:hover, .stButton > button:hover {{
        border-color: #2563eb !important;
        color: #2563eb !important;
        background-color: var(--accent-light) !important;
    }}

    /* Insight Banner */
    .insight-banner {{
        background: {"#1e293b" if is_dark else "#eff6ff"};
        border: 1px solid {"#334155" if is_dark else "#bfdbfe"};
        border-radius: var(--radius);
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        color: var(--text);
    }}
    .insight-banner h4 {{ margin: 0 0 0.5rem 0; color: #2563eb; font-weight: 800; font-size: 1.05rem; }}
    .insight-banner ul {{ margin: 0; padding-left: 1.2rem; font-size: 0.88rem; line-height: 1.6; }}

    /* Metric Cards */
    .metric-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{ border-color: var(--accent); transform: translateY(-1px); }}
    .metric-label {{ font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
    .metric-value {{ font-size: 1.7rem; font-weight: 700; color: var(--text); letter-spacing: -0.03em; margin-top: 0.2rem; font-family: 'JetBrains Mono', monospace; }}
    .metric-subtitle {{ font-size: 0.72rem; color: var(--text-dim); margin-top: 0.25rem; }}

    /* Full-Width Responsive Matrix Tables */
    .table-responsive {{
        width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
        border-radius: 8px;
        border: 1px solid var(--border);
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        background: var(--card);
    }}
    .seat-matrix-table {{
        width: 100%; min-width: 650px; border-collapse: collapse;
        font-size: 0.8rem; background: var(--card);
    }}
    .seat-matrix-table th {{
        background: var(--bg-subtle); color: var(--text-muted); font-weight: 700;
        padding: 0.45rem 0.35rem; text-align: center; border: 1px solid var(--border);
        font-size: 0.72rem; text-transform: uppercase; white-space: nowrap;
    }}
    .seat-matrix-table td {{
        padding: 0.4rem 0.35rem; text-align: center; border: 1px solid var(--border-subtle);
        color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; white-space: nowrap;
    }}
    .seat-matrix-table tr.header-row th {{ background: #2563eb; color: #ffffff; font-weight: 700; }}
    .seat-matrix-table tr.sub-header th {{ background: var(--bg-subtle); color: var(--text); }}
    .seat-matrix-table tr.quota-row td {{ font-weight: 600; }}

    /* Badges */
    .badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }}
    .badge-blue {{ color: #2563eb; background: var(--accent-light); }}

    /* Navigation Tabs */
    button[data-baseweb="tab"] {{
        background: transparent !important; color: var(--text-muted) !important;
        font-size: 0.88rem !important; font-weight: 600 !important;
        padding: 0.6rem 1.25rem !important; border-radius: 8px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color: #ffffff !important; background: #2563eb !important; }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{ display: none !important; }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important; background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important; border-radius: 12px !important;
        padding: 4px; margin-bottom: 1.5rem !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
