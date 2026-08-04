import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# Add custom CSS to hide the GitHub icon
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Clear any stale Streamlit data cache on load
st.cache_data.clear()

# Import PDF parsing module
from pdf_parser import parse_seat_matrix_pdf, generate_sample_seat_matrix, extract_city_from_name


# 1. Page Configuration
st.set_page_config(
    page_title="MAH-CET Seat Matrix & Full State Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# 2. Theme State Setup

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

IS_DARK = st.session_state.theme == "dark"

# Combined Streamlit Footer & Branding Masker (Legacy Sven-Bo Gist + Modern Streamlit 1.40+)
hide_streamlit_style = """
    <style>
    footer, 
    footer:after,
    #MainMenu, 
    #stDecoration,
    .stDeployButton, 
    [data-testid="stDecoration"], 
    [data-testid="stViewerBadge"],
    [data-testid="stHeader"] button[aria-label="View app source"],
    # [data-testid="stToolbar"],
    [data-testid="stFooter"],
    [data-testid="stReportViewFooter"],
    [data-testid="stStatusWidget"],
    .viewerBadge_container__1BShK,
    .viewerBadge_link__1S137,
    div[class*="viewerBadge"],
    div[class*="stDeployButton"],
    div[class*="profile"],
    div[class*="Profile"],
    div[class*="footer"],
    div[class*="Footer"],
    div[class*="HostedWith"],
    div[class*="styles_viewerBadge"],
    div[class*="embeddedAppMetaInfoBar"],
    a[href*="github.com"],

    a[href*="streamlit.io"],
    a[href*="share.streamlit.io"],
    footer *, 
    footer a {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
        max-height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -9999px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# 3. CSS Design System (Transparent Header, Hides Footer/Github Badges, Full-Width Responsive Tables)
theme_vars = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');

:root {{
    --bg: {"#09090b" if IS_DARK else "#f8fafc"};
    --bg-subtle: {"#0c0c0f" if IS_DARK else "#f1f5f9"};
    --card: {"#111115" if IS_DARK else "#ffffff"};
    --card-hover: {"#16161c" if IS_DARK else "#f8fafc"};
    --border: {"#27272a" if IS_DARK else "#cbd5e1"};
    --border-subtle: {"#1e1e24" if IS_DARK else "#e2e8f0"};
    --text: {"#fafafa" if IS_DARK else "#0f172a"};
    --text-muted: {"#a1a1aa" if IS_DARK else "#475569"};
    --text-dim: {"#71717a" if IS_DARK else "#64748b"};
    --accent: #2563eb;
    --accent-light: {"#1e3a8a" if IS_DARK else "#dbeafe"};
    --green: {"#22c55e" if IS_DARK else "#16a34a"};
    --green-muted: {"rgba(34,197,94,0.15)" if IS_DARK else "rgba(22,163,74,0.1)"};
    --amber: {"#f59e0b" if IS_DARK else "#d97706"};
    --amber-muted: {"rgba(245,158,11,0.15)" if IS_DARK else "rgba(217,119,6,0.1)"};
    --purple: {"#a855f7" if IS_DARK else "#7c3aed"};
    --purple-muted: {"rgba(168,85,247,0.15)" if IS_DARK else "rgba(124,58,237,0.1)"};
    --radius: 12px;
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}

/* Make top header background completely transparent */
header[data-testid="stHeader"] {{
    background: transparent !important;
    z-index: 100000 !important;
}}

/* Ultra-aggressive hiding of all footers, viewer badges, Streamlit branding, and profile avatars */
footer, 
#MainMenu, 
.stDeployButton, 
[data-testid="stDecoration"], 
[data-testid="stViewerBadge"],
[data-testid="stHeader"] button[aria-label="View app source"],
[data-testid="stToolbar"],
[data-testid="stFooter"],
[data-testid="stReportViewFooter"],
[data-testid="stStatusWidget"],
.viewerBadge_container__1BShK,
.viewerBadge_link__1S137,
div[class*="viewerBadge"],
div[class*="stDeployButton"],
div[class*="profile"],
div[class*="Profile"],
div[class*="footer"],
div[class*="Footer"],
div[class*="HostedWith"],
div[class*="styles_viewerBadge"],
a[href*="github.com"],
a[href*="streamlit.io"],
a[href*="share.streamlit.io"],
footer *, 
footer a {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    height: 0px !important;
    width: 0px !important;
    max-height: 0px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
    position: absolute !important;
    left: -9999px !important;
}}


/* Button styling fixes for Light & Dark mode contrast */
button[data-baseweb="button"], .stButton > button {{
    background-color: var(--bg-subtle) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    font-size: 0.78rem !important;
    padding: 0.35rem 0.5rem !important;
}}
button[data-baseweb="button"]:hover, .stButton > button:hover {{
    border-color: #2563eb !important;
    color: #2563eb !important;
    background-color: var(--accent-light) !important;
}}

# /* Ensure sidebar collapse/expand toggle button is ALWAYS bright & accessible */
# [data-testid="collapsedControl"], 
# [data-testid="stSidebarCollapseButton"],
# button[aria-label="Expand sidebar"], 
# button[aria-label="Collapse sidebar"],
# {{
#     display: flex !important;
#     visibility: visible !important;
#     opacity: 1 !important;
#     pointer-events: auto !important;
# }}

# [data-testid="collapsedControl"] {{
#     position: fixed !important;
#     top: 14px !important;
#     left: 14px !important;
#     z-index: 9999999 !important;
#     background: #2563eb !important;
#     color: #ffffff !important;
#     border-radius: 8px !important;
#     padding: 6px 10px !important;
#     box-shadow: 0 4px 12px rgba(37,99,235,0.4) !important;
#     border: 1px solid #1d4ed8 !important;
#     cursor: pointer !important;
# }}

# [data-testid="collapsedControl"] svg,
# [data-testid="stSidebarCollapseButton"] svg,
# button[aria-label="Expand sidebar"] svg,
# button[aria-label="Collapse sidebar"] svg {{
#     fill: #ffffff !important;
#     color: #ffffff !important;
#     stroke: #ffffff !important;
#     width: 20px !important;
#     height: 20px !important;
# }}

.block-container {{
    padding: 1.5rem 1.5rem 2.5rem !important;
    max-width: 1440px !important;
}}

.insight-banner {{
    background: {"#1e293b" if IS_DARK else "#eff6ff"};
    border: 1px solid {"#334155" if IS_DARK else "#bfdbfe"};
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    color: var(--text);
}}
.insight-banner h4 {{
    margin: 0 0 0.5rem 0;
    color: #2563eb;
    font-weight: 800;
    font-size: 1.05rem;
}}
.insight-banner ul {{
    margin: 0;
    padding-left: 1.2rem;
    font-size: 0.88rem;
    line-height: 1.6;
}}

.metric-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}}
.metric-card:hover {{
    border-color: var(--accent);
    transform: translateY(-1px);
}}
.metric-label {{
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.metric-value {{
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.03em;
    margin-top: 0.2rem;
    font-family: 'JetBrains Mono', monospace;
}}
.metric-subtitle {{
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 0.25rem;
}}

/* Table Responsive Wrapper to Prevent Any Overlap & Allow Smooth Mobile Scrolling */
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
    width: 100%;
    min-width: 650px;
    border-collapse: collapse;
    font-size: 0.8rem;
    background: var(--card);
}}
.seat-matrix-table th {{
    background: var(--bg-subtle);
    color: var(--text-muted);
    font-weight: 700;
    padding: 0.45rem 0.35rem;
    text-align: center;
    border: 1px solid var(--border);
    font-size: 0.72rem;
    text-transform: uppercase;
    white-space: nowrap;
}}
.seat-matrix-table td {{
    padding: 0.4rem 0.35rem;
    text-align: center;
    border: 1px solid var(--border-subtle);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    white-space: nowrap;
}}
.seat-matrix-table tr.header-row th {{
    background: #2563eb;
    color: #ffffff;
    font-weight: 700;
}}
.seat-matrix-table tr.sub-header th {{
    background: var(--bg-subtle);
    color: var(--text);
}}
.seat-matrix-table tr.quota-row td {{
    font-weight: 600;
}}

.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}}
.badge-blue {{ color: #2563eb; background: var(--accent-light); }}
.badge-green {{ color: var(--green); background: var(--green-muted); }}
.badge-amber {{ color: var(--amber); background: var(--amber-muted); }}
.badge-purple {{ color: var(--purple); background: var(--purple-muted); }}

button[data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.25rem !important;
    border-radius: 8px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #ffffff !important;
    background: #2563eb !important;
}}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
    display: none !important;
}}
[data-baseweb="tab-list"] {{
    gap: 6px !important;
    background: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 4px;
    margin-bottom: 1.5rem !important;
}}
</style>
"""
st.markdown(theme_vars, unsafe_allow_html=True)

# 3.5. Parent Window JS DOM Eraser (Removes Streamlit Cloud "Created With" Badge & Creator Avatar)
import streamlit.components.v1 as components
components.html("""
<script>
function eraseStreamlitBranding() {
    const targets = [
        'footer',
        '#MainMenu',
        '.stDeployButton',
        '[data-testid="stDecoration"]',
        '[data-testid="stViewerBadge"]',
        '[data-testid="stToolbar"]',
        '[data-testid="stFooter"]',
        '[data-testid="stReportViewFooter"]',
        '.viewerBadge_container__1BShK',
        '.viewerBadge_link__1S137',
        'div[class*="viewerBadge"]',
        'div[class*="profile"]',
        'div[class*="Profile"]',
        'div[class*="HostedWith"]',
        'a[href*="github.com"]',
        'a[href*="streamlit.io"]',
        'a[href*="share.streamlit.io"]'
    ];
    targets.forEach(t => {
        try {
            if (window.parent && window.parent.document) {
                window.parent.document.querySelectorAll(t).forEach(el => {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.remove();
                });
            }
        } catch(e){}
        try {
            document.querySelectorAll(t).forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.remove();
            });
        } catch(e){}
    });
}
eraseStreamlitBranding();
setInterval(eraseStreamlitBranding, 300);
</script>
""", height=0, width=0)


# 4. Plotly Helper
def apply_plot_style(fig, height=330, reverse_y=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#71717a" if IS_DARK else "#475569", size=11),
        margin=dict(l=10, r=10, t=25, b=10),
        height=height
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10)
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10),
        autorange="reversed" if reverse_y else None
    )
    return fig

# 5. Header Bar
h_col1, h_col2 = st.columns([9, 1.5])
with h_col1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.5rem; margin-left: 45px;">
        <span style="font-size: 2.2rem;">🎓</span>
        <div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em;">MAH-CET Seat Matrix & Full State Analytics</h2>
            <p style="margin: 0; color: var(--text-muted); font-size: 0.85rem;">
                State Common Entrance Test Cell (Maharashtra) • Unified Region & Quota Master Analytics
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with h_col2:
    theme_btn_text = "☀️ Light Mode" if IS_DARK else "🌙 Dark Mode"
    if st.button(theme_btn_text, use_container_width=True):
        toggle_theme()
        st.rerun()

st.markdown("<hr style='border: none; border-top: 1px solid var(--border); margin: 0.5rem 0 1.25rem 0;' />", unsafe_allow_html=True)

# 6. Data Loading & Master Data Setup
def get_default_data():
    return generate_sample_seat_matrix()

df_inst_raw, df_cat_raw = get_default_data()
all_regions = sorted(list(set(df_inst_raw["Region / City"].dropna().unique())))
region_counts = df_inst_raw["Region / City"].value_counts().to_dict()

# Handle Preset Triggers BEFORE widget instantiation to prevent StreamlitAPIException!
if "region_preset_trigger" in st.session_state:
    st.session_state["sidebar_selected_regions_key"] = st.session_state["region_preset_trigger"]
    del st.session_state["region_preset_trigger"]

if "sidebar_selected_regions_key" not in st.session_state:
    st.session_state["sidebar_selected_regions_key"] = all_regions

# 7. MASTER SIDEBAR (DATA SOURCE AT TOP & COMPACT 2-BUTTON QUICK FILTERS)
st.sidebar.markdown("### ⚙️ Master Filter Center")

# Data Source Selection at the VERY TOP of Sidebar!
data_source = st.sidebar.radio(
    "📊 Data Source:",
    ["📄 Full Maharashtra Dataset (440+ Colleges / 438 Pages)", "📤 Upload Custom CET Seat Matrix PDF"]
)

if data_source == "📤 Upload Custom CET Seat Matrix PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF file:", type=["pdf"])
    if uploaded_pdf is not None:
        try:
            pdf_bytes = io.BytesIO(uploaded_pdf.read())
            df_parsed_inst, df_parsed_cat = parse_seat_matrix_pdf(pdf_bytes)
            if not df_parsed_inst.empty:
                df_inst_raw = df_parsed_inst
                if not df_parsed_cat.empty:
                    df_cat_raw = df_parsed_cat
                st.sidebar.success(f"Successfully extracted {len(df_parsed_inst)} institutes from PDF!")
            else:
                st.sidebar.warning("Could not extract structured table automatically. Displaying full state dataset.")
        except Exception as e:
            st.sidebar.error(f"Error parsing PDF: {e}")

st.sidebar.markdown("---")

st.sidebar.markdown("#### 📍 Region / Location Filter")
selected_regions = st.sidebar.multiselect(
    "Choose Region(s):",
    options=all_regions,
    key="sidebar_selected_regions_key"
)

c_pune = region_counts.get("Pune", 64)
c_mumbai = region_counts.get("Mumbai", 64)
c_nashik = region_counts.get("Nashik", 12)
c_total = len(df_inst_raw)

# Compact 2-button per line quick filters
sb_p1, sb_p2 = st.sidebar.columns(2)
with sb_p1:
    if sb_p1.button(f"📍 Nashik ({c_nashik})", use_container_width=True, key="sb_btn_nashik"):
        st.session_state["region_preset_trigger"] = ["Nashik"]
        st.rerun()
with sb_p2:
    if sb_p2.button(f"📍 Pune ({c_pune})", use_container_width=True, key="sb_btn_pune"):
        st.session_state["region_preset_trigger"] = ["Pune"]
        st.rerun()

sb_p3, sb_p4 = st.sidebar.columns(2)
with sb_p3:
    if sb_p3.button(f"📍 Mumbai ({c_mumbai})", use_container_width=True, key="sb_btn_mumbai"):
        st.session_state["region_preset_trigger"] = ["Mumbai"]
        st.rerun()
with sb_p4:
    if sb_p4.button(f"🌐 All ({c_total})", use_container_width=True, key="sb_btn_all"):
        st.session_state["region_preset_trigger"] = all_regions
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📚 Course & Status Filters")

all_courses = sorted(list(set(df_inst_raw["Course Name"].dropna().unique())))
if "selected_courses_key" not in st.session_state:
    st.session_state["selected_courses_key"] = all_courses

selected_courses = st.sidebar.multiselect(
    "Select Course(s):",
    options=all_courses,
    key="selected_courses_key"
)

all_statuses = sorted(list(set(df_inst_raw["Status"].dropna().unique())))
if "selected_statuses_key" not in st.session_state:
    st.session_state["selected_statuses_key"] = all_statuses

selected_statuses = st.sidebar.multiselect(
    "College Status / Autonomy:",
    options=all_statuses,
    key="selected_statuses_key"
)

# Apply Master Filters strictly to raw DataFrames
cond_region = df_inst_raw["Region / City"].isin(selected_regions) if selected_regions else pd.Series(True, index=df_inst_raw.index)
cond_course = df_inst_raw["Course Name"].isin(selected_courses) if selected_courses else pd.Series(True, index=df_inst_raw.index)
cond_status = df_inst_raw["Status"].isin(selected_statuses) if selected_statuses else pd.Series(True, index=df_inst_raw.index)

df_inst_filtered = df_inst_raw[cond_region & cond_course & cond_status]

filtered_choice_codes = df_inst_filtered["Choice Code"].tolist() if "Choice Code" in df_inst_filtered else []
df_cat_filtered = df_cat_raw[df_cat_raw["Choice Code"].isin(filtered_choice_codes)] if not df_cat_raw.empty else pd.DataFrame()

available_colleges = sorted(list(set(df_inst_filtered["Institute Name"].unique())))

# Active Region Display Text (Clear multi-region formatting e.g. "Pune + Nashik")
if not selected_regions or len(selected_regions) == len(all_regions):
    active_reg_text = "All Maharashtra Regions"
elif len(selected_regions) <= 3:
    active_reg_text = " + ".join(selected_regions)
else:
    active_reg_text = f"{len(selected_regions)} Regions ({', '.join(selected_regions[:3])}...)"

# Validate and sync single_college_select to guarantee it ALWAYS belongs to active selected_regions!
if "single_college_select" in st.session_state:
    curr_sel = st.session_state["single_college_select"]
    if curr_sel not in available_colleges:
        if available_colleges:
            st.session_state["single_college_select"] = available_colleges[0]
    else:
        curr_rows = df_inst_raw[df_inst_raw["Institute Name"] == curr_sel]
        if not curr_rows.empty:
            curr_region = curr_rows["Region / City"].values[0]
            if selected_regions and curr_region not in selected_regions:
                if available_colleges:
                    st.session_state["single_college_select"] = available_colleges[0]

# 8. Executive Summary Brief Card on First Page
tot_colleges = len(df_inst_filtered["Institute Code"].unique()) if not df_inst_filtered.empty else 0
tot_si = int(df_inst_filtered["Sanctioned Intake (SI)"].sum()) if not df_inst_filtered.empty else 0
tot_cap = int(df_inst_filtered["CAP Total Seats"].sum()) if not df_inst_filtered.empty else 0
tot_hu = int(df_inst_filtered["Home University (HU) Seats"].sum()) if not df_inst_filtered.empty else 0
tot_ohu = int(df_inst_filtered["Other than Home University (OHU) Seats"].sum()) if not df_inst_filtered.empty else 0
tot_inst_seats = int(df_inst_filtered["Institute Seats"].sum()) if not df_inst_filtered.empty else 0

st.markdown(f"""
<div class="insight-banner">
    <h4>📍 Active Brief Summary: {active_reg_text} ({tot_colleges} Institutes)</h4>
    <ul>
        <li><b>Selection Overview:</b> Viewing <b>{tot_colleges} colleges</b> in <b>{active_reg_text}</b> matching active sidebar filters.</li>
        <li><b>Total Intake Capacity:</b> <b>{tot_si:,} Sanctioned Intake Seats</b> (<b>{tot_cap:,} CAP Round Seats</b> + <b>{tot_inst_seats:,} Management Quota Seats</b>).</li>
        <li><b>Quota Share:</b> <b>{tot_hu:,} Home University (HU) Seats</b> (70%) vs <b>{tot_ohu:,} Other Home University (OHU) Seats</b> (30%).</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 9. KPI Cards Row (Reflecting Exact Active Selection)
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Institutes Found</div>
        <div class="metric-value">{tot_colleges}</div>
        <div class="metric-subtitle">{active_reg_text}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Intake (SI)</div>
        <div class="metric-value">{tot_si:,}</div>
        <div class="metric-subtitle">Sanctioned Intake</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">CAP Total Seats</div>
        <div class="metric-value" style="color: #2563eb;">{tot_cap:,}</div>
        <div class="metric-subtitle">Centralized Admissions</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">HU Seats</div>
        <div class="metric-value" style="color: #16a34a;">{tot_hu:,}</div>
        <div class="metric-subtitle">Home Univ (70% State)</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">OHU Seats</div>
        <div class="metric-value" style="color: #a855f7;">{tot_ohu:,}</div>
        <div class="metric-subtitle">Other Home Univ (30%)</div>
    </div>
    """, unsafe_allow_html=True)

with k6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Institute Seats</div>
        <div class="metric-value" style="color: #d97706;">{tot_inst_seats:,}</div>
        <div class="metric-subtitle">Management Quota (20%)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# 10. Main Tabs Navigation
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Candidate Quota & Seat Finder",
    "📊 State Executive Dashboard & Charts",
    "🏫 College Matrix Inspector & Comparator",
    "📋 Complete Master Data Table",
    "📤 PDF Parsing Inspector"
])

# ---------------------------------------------------------
# TAB 0: CANDIDATE QUOTA & SEAT AVAILABILITY FINDER
# ---------------------------------------------------------
with tab0:
    st.markdown("### 🎯 Candidate Quota & Seat Availability Finder")
    st.caption("Driven 100% dynamically by your Master Sidebar Filters.")

    sc_col1, sc_col2, sc_col3, sc_col4 = st.columns([3.5, 3, 3, 2.5])

    with sc_col1:
        tab0_search = st.text_input(
            "🔍 Search College Name, DTE Code, or City:",
            value="",
            placeholder="e.g. K. K. Wagh, MET, BYK, COEP, Sydenham, VJTI...",
            key="tab0_instant_search"
        )

    with sc_col2:
        quota_scope = st.selectbox(
            "🏛️ Quota Scope:",
            options=["Combined (HU + OHU / SL)", "Home University (HU) Seats", "Other Home University (OHU) Seats"],
            index=0,
            key="tab0_quota_scope_select"
        )

    with sc_col3:
        category_options = ["OPEN", "OBC", "SC", "ST", "SEBC", "EWS", "NTB", "NTC", "NTD", "VJDT", "PWD", "DEF", "TOTAL"]
        selected_cat = st.selectbox(
            "🏷️ Reservation Category:",
            options=category_options,
            index=0,
            key="tab0_cat_select_master"
        )

    with sc_col4:
        gender_filter = st.selectbox(
            "👫 Candidate Gender:",
            options=["All Seats (General + Ladies)", "♂️ Male (General G Seats)", "♀️ Female (Ladies L + General G)"],
            index=0,
            key="tab0_gender_filter_select"
        )


    st.markdown("<br/>", unsafe_allow_html=True)

    df_cat_search = df_cat_filtered.copy()

    if tab0_search.strip():
        df_cat_search = df_cat_search[
            df_cat_search["Institute Name"].str.contains(tab0_search, case=False, na=False) |
            df_cat_search["Institute Code"].str.contains(tab0_search, case=False, na=False) |
            df_cat_search["Region / City"].str.contains(tab0_search, case=False, na=False) |
            df_cat_search["Choice Code"].str.contains(tab0_search, case=False, na=False)
        ]

    prefix = ""
    if quota_scope == "Home University (HU) Seats":
        prefix = "HU_"
    elif quota_scope == "Other Home University (OHU) Seats":
        prefix = "OHU_"

    g_col = f"{prefix}{selected_cat}_G" if f"{prefix}{selected_cat}_G" in df_cat_search else f"{selected_cat}_G"
    l_col = f"{prefix}{selected_cat}_L" if f"{prefix}{selected_cat}_L" in df_cat_search else f"{selected_cat}_L"

    total_g_seats = int(df_cat_search[g_col].sum()) if g_col and g_col in df_cat_search and not df_cat_search.empty else 0
    total_l_seats = int(df_cat_search[l_col].sum()) if l_col and l_col in df_cat_search and not df_cat_search.empty else 0
    
    if selected_cat in ["EWS", "PWD", "DEF"]:
        total_comb_seats = int(df_cat_search[selected_cat].sum()) if selected_cat in df_cat_search and not df_cat_search.empty else 0
    else:
        total_comb_seats = total_g_seats + total_l_seats

    total_colleges_found = len(df_cat_search["Institute Code"].unique()) if not df_cat_search.empty else 0

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Institutes Found</div>
            <div class="metric-value">{total_colleges_found}</div>
            <div class="metric-subtitle">{active_reg_text}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{selected_cat} General (G) Seats</div>
            <div class="metric-value" style="color: #2563eb;">{total_g_seats:,}</div>
            <div class="metric-subtitle">{quota_scope}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{selected_cat} Ladies (L) Seats</div>
            <div class="metric-value" style="color: #ec4899;">{total_l_seats:,}</div>
            <div class="metric-subtitle">30% Reserved Female Quota</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total {selected_cat} Seats</div>
            <div class="metric-value" style="color: #16a34a;">{total_comb_seats:,}</div>
            <div class="metric-subtitle">Combined {selected_cat} Quota</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    v_col1, v_col2 = st.columns([7, 5])

    with v_col1:
        st.markdown(f"#### 📋 {selected_cat} Category Seats Table ({quota_scope})")
        
        if not df_cat_search.empty:
            if selected_cat in ["EWS", "PWD", "DEF"]:
                df_view = df_cat_search[["Institute Code", "Institute Name", "Region / City", "Course Name", "CAP Total Seats", "Institute Seats", selected_cat]].copy()
                df_view = df_view.rename(columns={selected_cat: f"{selected_cat} Seats"})
            else:
                df_view = df_cat_search[["Institute Code", "Institute Name", "Region / City", "Course Name", "CAP Total Seats", "Institute Seats", g_col, l_col]].copy()
                df_view[f"Total {selected_cat}"] = df_view[g_col] + df_view[l_col]
                df_view = df_view.rename(columns={
                    g_col: f"General (G)",
                    l_col: f"Ladies (L)"
                })

            st.dataframe(
                df_view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Institute Code": st.column_config.TextColumn("Code"),
                    "Institute Name": st.column_config.TextColumn("College Name", width="large"),
                    "Region / City": st.column_config.TextColumn("Location"),
                    "CAP Total Seats": st.column_config.NumberColumn("CAP Seats"),
                    "Institute Seats": st.column_config.NumberColumn("Mgmt Seats")
                }
            )

            cat_csv = df_view.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {selected_cat} Seats Data as CSV",
                data=cat_csv,
                file_name=f"MAH_CET_{selected_cat}_Seats.csv",
                mime="text/csv"
            )
        else:
            st.info("No colleges match the active region filter or search term.")

    with v_col2:
        st.markdown(f"#### 📊 {selected_cat} Seats Distribution Chart")
        
        if not df_cat_search.empty:
            df_chart = df_cat_search.head(15).copy()
            df_chart["Short Name"] = df_chart["Institute Name"].apply(lambda x: x[:28] + "..." if len(x) > 28 else x)
            
            if selected_cat in ["EWS", "PWD", "DEF"]:
                fig_cat_bar = px.bar(
                    df_chart,
                    y="Short Name",
                    x=selected_cat,
                    orientation="h",
                    color="Region / City",
                    labels={"Short Name": "College", selected_cat: "Total Seats"}
                )
            else:
                fig_cat_bar = px.bar(
                    df_chart,
                    y="Short Name",
                    x=[g_col, l_col],
                    orientation="h",
                    barmode="stack",
                    labels={"value": "Seats", "variable": "Quota", "Short Name": "College"},
                    color_discrete_sequence=["#2563eb", "#ec4899"]
                )

            apply_plot_style(fig_cat_bar, height=380, reverse_y=True)
            st.plotly_chart(fig_cat_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data to plot.")

# ---------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD & CHARTS
# ---------------------------------------------------------
with tab1:
    if not df_inst_filtered.empty:
        top_city = df_inst_filtered["Region / City"].value_counts().idxmax()
        top_city_count = df_inst_filtered["Region / City"].value_counts().max()
        hu_pct = int((tot_hu / tot_cap * 100)) if tot_cap > 0 else 70
        ohu_pct = 100 - hu_pct
        
        st.markdown(f"""
        <div class="insight-banner">
            <h4>💡 Detailed Analytics for Active Selection: {active_reg_text}</h4>
            <ul>
                <li><b>Total Capacity:</b> In your active selection, <b>{tot_colleges} colleges</b> offer <b>{tot_si:,} Sanctioned Seats</b> (CAP Seats: <b>{tot_cap:,}</b>).</li>
                <li><b>Home vs Other University Quota:</b> <b>{hu_pct}% ({tot_hu:,} seats)</b> are Home University (HU) quota, while <b>{ohu_pct}% ({tot_ohu:,} seats)</b> are Other Home University (OHU) quota.</li>
                <li><b>Management Quota:</b> <b>{tot_inst_seats:,} seats</b> (20% of intake) are designated for Institute Level / Management admissions.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">📍 Seat Share Breakdown by Region & Quota Type</div>
            <div class="chart-subtitle">Compare Home University (HU), Other Home Univ (OHU), and All India seats</div>
        """, unsafe_allow_html=True)
        
        if not df_inst_filtered.empty:
            df_grp = df_inst_filtered.groupby("Region / City")[["Home University (HU) Seats", "Other than Home University (OHU) Seats", "All India Seats"]].sum().reset_index()
            fig_grp = px.bar(
                df_grp,
                x="Region / City",
                y=["Home University (HU) Seats", "Other than Home University (OHU) Seats", "All India Seats"],
                barmode="stack",
                color_discrete_sequence=["#16a34a", "#a855f7", "#2563eb"],
                labels={"value": "Seats", "variable": "Quota"}
            )
            apply_plot_style(fig_grp, height=340)
            st.plotly_chart(fig_grp, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">🏷️ Reservation Category Share Distribution</div>
            <div class="chart-subtitle">Percentage share of OPEN, OBC, SC, ST, SEBC, EWS across selected colleges</div>
        """, unsafe_allow_html=True)

        if not df_cat_filtered.empty:
            cat_totals = {
                "OPEN": df_cat_filtered["OPEN_G"].sum() + df_cat_filtered["OPEN_L"].sum(),
                "OBC": df_cat_filtered["OBC_G"].sum() + df_cat_filtered["OBC_L"].sum(),
                "SC": df_cat_filtered["SC_G"].sum() + df_cat_filtered["SC_L"].sum(),
                "ST": df_cat_filtered["ST_G"].sum() + df_cat_filtered["ST_L"].sum(),
                "SEBC": df_cat_filtered["SEBC_G"].sum() + df_cat_filtered["SEBC_L"].sum(),
                "EWS": df_cat_filtered["EWS"].sum(),
                "VJ/DT": df_cat_filtered["VJDT_G"].sum() + df_cat_filtered["VJDT_L"].sum(),
                "NT-B/C/D": df_cat_filtered["NTB_G"].sum() + df_cat_filtered["NTC_G"].sum() + df_cat_filtered["NTD_G"].sum()
            }

            df_cat_pie = pd.DataFrame([{"Category": k, "Seats": v} for k, v in cat_totals.items() if v > 0])
            fig_pie = px.pie(
                df_cat_pie,
                names="Category",
                values="Seats",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            apply_plot_style(fig_pie, height=340)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No category data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)

    with c3:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">⚖️ General (G) vs Ladies (30% L) Quota Split</div>
            <div class="chart-subtitle">Gender reservation breakdown per category</div>
        """, unsafe_allow_html=True)

        if not df_cat_filtered.empty:
            cat_sum = {
                "OPEN": (df_cat_filtered["OPEN_G"].sum(), df_cat_filtered["OPEN_L"].sum()),
                "OBC": (df_cat_filtered["OBC_G"].sum(), df_cat_filtered["OBC_L"].sum()),
                "SC": (df_cat_filtered["SC_G"].sum(), df_cat_filtered["SC_L"].sum()),
                "ST": (df_cat_filtered["ST_G"].sum(), df_cat_filtered["ST_L"].sum()),
                "SEBC": (df_cat_filtered["SEBC_G"].sum(), df_cat_filtered["SEBC_L"].sum()),
            }

            cat_df = pd.DataFrame([
                {"Category": k, "General (G)": v[0], "Ladies (L)": v[1]}
                for k, v in cat_sum.items()
            ])

            fig_gen_lad = px.bar(
                cat_df,
                x="Category",
                y=["General (G)", "Ladies (L)"],
                barmode="group",
                color_discrete_sequence=["#2563eb", "#ec4899"]
            )
            apply_plot_style(fig_gen_lad, height=340)
            st.plotly_chart(fig_gen_lad, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No category data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">🏆 Top Institutes Ranked by Total Intake Capacity</div>
            <div class="chart-subtitle">Top colleges in active selection ranked by Sanctioned Intake</div>
        """, unsafe_allow_html=True)

        if not df_inst_filtered.empty:
            df_top = df_inst_filtered.sort_values(by="Sanctioned Intake (SI)", ascending=False).head(10)
            df_top["Short Name"] = df_top["Institute Name"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
            fig_top = px.bar(
                df_top,
                y="Short Name",
                x="Sanctioned Intake (SI)",
                orientation="h",
                color="Region / City",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            apply_plot_style(fig_top, height=340, reverse_y=True)
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: COLLEGE MATRIX INSPECTOR & FULL-WIDTH COMPARATOR
# ---------------------------------------------------------
with tab2:
    st.markdown("### 🏫 Detailed College Seat Matrix Inspector & Side-by-Side Comparator")
    st.caption("Inspect a college from your active region filter, and compare its seat matrix with ANY college across all of Maharashtra in full-width stacked view!")

    # Top Selection Row (Clear 2-column layout)
    sel_c1, sel_c2 = st.columns(2)

    with sel_c1:
        st.markdown(f"#### 📌 Primary College ({active_reg_text})")
        selected_college_single = st.selectbox(
            "Select 1st College to Inspect:",
            options=available_colleges if available_colleges else ["No colleges in current filter"],
            key="single_college_select"
        )

    with sel_c2:
        st.markdown("#### ⚖️ Comparison College (Search All 440+ Colleges)")
        search_comp = st.text_input(
            "🔍 Search 2nd College (Name, City, Code):",
            value="",
            placeholder="Type e.g. COEP, Sydenham, VJTI, Mumbai, Pune, Nagpur, 6101...",
            key="tab2_compare_search_input"
        )

        all_state_colleges = sorted(list(set(df_inst_raw["Institute Name"].dropna().unique())))
        if search_comp.strip():
            all_state_colleges = [
                c for c in all_state_colleges 
                if search_comp.lower() in c.lower() or 
                   search_comp.lower() in df_inst_raw[df_inst_raw["Institute Name"] == c]["Institute Code"].values[0].lower() or
                   search_comp.lower() in df_inst_raw[df_inst_raw["Institute Name"] == c]["Region / City"].values[0].lower()
            ]

        all_state_colleges = [c for c in all_state_colleges if c != selected_college_single]

        compare_college = st.selectbox(
            "Select 2nd College to Compare:",
            options=all_state_colleges if all_state_colleges else ["No matching college found"],
            key="compare_college_select_full_state"
        )

    st.markdown("<hr style='border: none; border-top: 1px solid var(--border); margin: 1rem 0;' />", unsafe_allow_html=True)

    # 1st College Full-Width Section
    inst_row1 = df_inst_raw[df_inst_raw["Institute Name"] == selected_college_single].iloc[0] if selected_college_single and selected_college_single in df_inst_raw["Institute Name"].values else None
    cat_row1 = None
    if inst_row1 is not None:
        choice_code1 = inst_row1["Choice Code"]
        cat_row1 = df_cat_raw[df_cat_raw["Choice Code"] == choice_code1].iloc[0] if not df_cat_raw.empty and choice_code1 in df_cat_raw["Choice Code"].values else None

        st.markdown(f"""
        <div style="background: var(--card); border: 1px solid #2563eb; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="color: #2563eb; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.4rem;">
                📌 Primary College 1: {inst_row1['Institute Code']} - {inst_row1['Institute Name']}
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <span class="badge badge-blue">{inst_row1['Status']}</span>
                <span class="badge badge-green">📍 {inst_row1['Region / City']}</span>
                <span class="badge badge-purple">Course: {inst_row1['Course Name']}</span>
                <span class="badge badge-amber">Choice Code: {inst_row1['Choice Code']}</span>
                <span class="badge badge-blue">Intake (SI): {inst_row1['Sanctioned Intake (SI)']} Seats</span>
                <span class="badge badge-green">CAP Seats: {inst_row1['CAP Total Seats']}</span>
                <span class="badge badge-amber">Mgmt Seats: {inst_row1['Institute Seats']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if cat_row1 is not None:
            html_table1 = f"""
            <div class="table-responsive">
            <table class="seat-matrix-table">
                <thead>
                    <tr class="header-row" style="background: #2563eb;">
                        <th>Quota</th>
                        <th colspan="2">OPEN</th>
                        <th colspan="2">SC</th>
                        <th colspan="2">ST</th>
                        <th colspan="2">VJDT</th>
                        <th colspan="2">NTB</th>
                        <th colspan="2">NTC</th>
                        <th colspan="2">NTD</th>
                        <th colspan="2">OBC</th>
                        <th colspan="2">SEBC</th>
                        <th colspan="2">TOTAL</th>
                    </tr>
                    <tr class="sub-header">
                        <th></th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="quota-row">
                        <td><b style="color: #16a34a;">HU</b></td>
                        <td><b>{cat_row1.get('HU_OPEN_G', 0)}</b></td><td>{cat_row1.get('HU_OPEN_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_SC_G', 0)}</b></td><td>{cat_row1.get('HU_SC_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_ST_G', 0)}</b></td><td>{cat_row1.get('HU_ST_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_VJDT_G', 0)}</b></td><td>{cat_row1.get('HU_VJDT_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_NTB_G', 0)}</b></td><td>{cat_row1.get('HU_NTB_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_NTC_G', 0)}</b></td><td>{cat_row1.get('HU_NTC_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_NTD_G', 0)}</b></td><td>{cat_row1.get('HU_NTD_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_OBC_G', 0)}</b></td><td>{cat_row1.get('HU_OBC_L', 0)}</td>
                        <td><b>{cat_row1.get('HU_SEBC_G', 0)}</b></td><td>{cat_row1.get('HU_SEBC_L', 0)}</td>
                        <td><b style="color: #16a34a;">{cat_row1.get('HU_TOTAL', 0)}</b></td><td></td>
                    </tr>
                    <tr class="quota-row">
                        <td><b style="color: #a855f7;">OHU</b></td>
                        <td><b>{cat_row1.get('OHU_OPEN_G', 0)}</b></td><td>{cat_row1.get('OHU_OPEN_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_SC_G', 0)}</b></td><td>{cat_row1.get('OHU_SC_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_ST_G', 0)}</b></td><td>{cat_row1.get('OHU_ST_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_VJDT_G', 0)}</b></td><td>{cat_row1.get('OHU_VJDT_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_NTB_G', 0)}</b></td><td>{cat_row1.get('OHU_NTB_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_NTC_G', 0)}</b></td><td>{cat_row1.get('OHU_NTC_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_NTD_G', 0)}</b></td><td>{cat_row1.get('OHU_NTD_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_OBC_G', 0)}</b></td><td>{cat_row1.get('OHU_OBC_L', 0)}</td>
                        <td><b>{cat_row1.get('OHU_SEBC_G', 0)}</b></td><td>{cat_row1.get('OHU_SEBC_L', 0)}</td>
                        <td><b style="color: #a855f7;">{cat_row1.get('OHU_TOTAL', 0)}</b></td><td></td>
                    </tr>
                </tbody>
            </table>
            </div>
            """
            st.markdown(html_table1, unsafe_allow_html=True)

    # 2nd College Full-Width Section
    inst_row2 = df_inst_raw[df_inst_raw["Institute Name"] == compare_college].iloc[0] if compare_college and compare_college in df_inst_raw["Institute Name"].values else None
    cat_row2 = None
    if inst_row2 is not None:
        choice_code2 = inst_row2["Choice Code"]
        cat_row2 = df_cat_raw[df_cat_raw["Choice Code"] == choice_code2].iloc[0] if not df_cat_raw.empty and choice_code2 in df_cat_raw["Choice Code"].values else None

        st.markdown(f"""
        <div style="background: var(--card); border: 1px solid #7c3aed; border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem; margin-bottom: 1rem;">
            <div style="color: #7c3aed; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.4rem;">
                ⚖️ Comparison College 2: {inst_row2['Institute Code']} - {inst_row2['Institute Name']}
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <span class="badge badge-purple">{inst_row2['Status']}</span>
                <span class="badge badge-green">📍 {inst_row2['Region / City']}</span>
                <span class="badge badge-blue">Course: {inst_row2['Course Name']}</span>
                <span class="badge badge-amber">Choice Code: {inst_row2['Choice Code']}</span>
                <span class="badge badge-purple">Intake (SI): {inst_row2['Sanctioned Intake (SI)']} Seats</span>
                <span class="badge badge-green">CAP Seats: {inst_row2['CAP Total Seats']}</span>
                <span class="badge badge-amber">Mgmt Seats: {inst_row2['Institute Seats']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if cat_row2 is not None:
            html_table2 = f"""
            <div class="table-responsive">
            <table class="seat-matrix-table">
                <thead>
                    <tr class="header-row" style="background: #7c3aed;">
                        <th>Quota</th>
                        <th colspan="2">OPEN</th>
                        <th colspan="2">SC</th>
                        <th colspan="2">ST</th>
                        <th colspan="2">VJDT</th>
                        <th colspan="2">NTB</th>
                        <th colspan="2">NTC</th>
                        <th colspan="2">NTD</th>
                        <th colspan="2">OBC</th>
                        <th colspan="2">SEBC</th>
                        <th colspan="2">TOTAL</th>
                    </tr>
                    <tr class="sub-header">
                        <th></th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                        <th>G</th><th>L</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="quota-row">
                        <td><b style="color: #16a34a;">HU</b></td>
                        <td><b>{cat_row2.get('HU_OPEN_G', 0)}</b></td><td>{cat_row2.get('HU_OPEN_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_SC_G', 0)}</b></td><td>{cat_row2.get('HU_SC_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_ST_G', 0)}</b></td><td>{cat_row2.get('HU_ST_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_VJDT_G', 0)}</b></td><td>{cat_row2.get('HU_VJDT_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_NTB_G', 0)}</b></td><td>{cat_row2.get('HU_NTB_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_NTC_G', 0)}</b></td><td>{cat_row2.get('HU_NTC_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_NTD_G', 0)}</b></td><td>{cat_row2.get('HU_NTD_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_OBC_G', 0)}</b></td><td>{cat_row2.get('HU_OBC_L', 0)}</td>
                        <td><b>{cat_row2.get('HU_SEBC_G', 0)}</b></td><td>{cat_row2.get('HU_SEBC_L', 0)}</td>
                        <td><b style="color: #7c3aed;">{cat_row2.get('HU_TOTAL', 0)}</b></td><td></td>
                    </tr>
                    <tr class="quota-row">
                        <td><b style="color: #a855f7;">OHU</b></td>
                        <td><b>{cat_row2.get('OHU_OPEN_G', 0)}</b></td><td>{cat_row2.get('OHU_OPEN_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_SC_G', 0)}</b></td><td>{cat_row2.get('OHU_SC_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_ST_G', 0)}</b></td><td>{cat_row2.get('OHU_ST_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_VJDT_G', 0)}</b></td><td>{cat_row2.get('OHU_VJDT_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_NTB_G', 0)}</b></td><td>{cat_row2.get('OHU_NTB_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_NTC_G', 0)}</b></td><td>{cat_row2.get('OHU_NTC_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_NTD_G', 0)}</b></td><td>{cat_row2.get('OHU_NTD_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_OBC_G', 0)}</b></td><td>{cat_row2.get('OHU_OBC_L', 0)}</td>
                        <td><b>{cat_row2.get('OHU_SEBC_G', 0)}</b></td><td>{cat_row2.get('OHU_SEBC_L', 0)}</td>
                        <td><b style="color: #ec4899;">{cat_row2.get('OHU_TOTAL', 0)}</b></td><td></td>
                    </tr>
                </tbody>
            </table>
            </div>
            """
            st.markdown(html_table2, unsafe_allow_html=True)

    # Dynamic Comparative Analysis Summary Banner
    if inst_row1 is not None and inst_row2 is not None and cat_row1 is not None and cat_row2 is not None:
        c1_open = cat_row1.get("OPEN_G", 0) + cat_row1.get("OPEN_L", 0)
        c2_open = cat_row2.get("OPEN_G", 0) + cat_row2.get("OPEN_L", 0)
        
        c1_obc = cat_row1.get("OBC_G", 0) + cat_row1.get("OBC_L", 0)
        c2_obc = cat_row2.get("OBC_G", 0) + cat_row2.get("OBC_L", 0)

        c1_scst = cat_row1.get("SC_G", 0) + cat_row1.get("SC_L", 0) + cat_row1.get("ST_G", 0) + cat_row1.get("ST_L", 0)
        c2_scst = cat_row2.get("SC_G", 0) + cat_row2.get("SC_L", 0) + cat_row2.get("ST_G", 0) + cat_row2.get("ST_L", 0)

        st.markdown(f"""
        <div class="insight-banner" style="margin-top: 1.5rem;">
            <h4>⚖️ Side-by-Side Comparative Summary Analysis</h4>
            <ul>
                <li><b>Total Intake Capacity:</b> <b>{inst_row1['Institute Name']}</b> offers <b>{inst_row1['Sanctioned Intake (SI)']} seats</b> (CAP: {inst_row1['CAP Total Seats']} | Mgmt: {inst_row1['Institute Seats']}) vs <b>{inst_row2['Institute Name']}</b> offering <b>{inst_row2['Sanctioned Intake (SI)']} seats</b> (CAP: {inst_row2['CAP Total Seats']} | Mgmt: {inst_row2['Institute Seats']}).</li>
                <li><b>OPEN Category Seats:</b> College 1 offers <b>{c1_open} OPEN seats</b> ({cat_row1.get('HU_OPEN_G', 0)} General HU, {cat_row1.get('HU_OPEN_L', 0)} Ladies HU) vs College 2 offering <b>{c2_open} OPEN seats</b> ({cat_row2.get('HU_OPEN_G', 0)} General HU, {cat_row2.get('HU_OPEN_L', 0)} Ladies HU).</li>
                <li><b>Reserved Seats Breakdown (OBC / SC / ST):</b> College 1 has <b>{c1_obc} OBC seats</b> and <b>{c1_scst} SC/ST seats</b> vs College 2 with <b>{c2_obc} OBC seats</b> and <b>{c2_scst} SC/ST seats</b>.</li>
                <li><b>Location & Status Advantage:</b> <b>{inst_row1['Institute Name']}</b> is located in <b>📍 {inst_row1['Region / City']}</b> ({inst_row1['Status']}) whereas <b>{inst_row2['Institute Name']}</b> is in <b>📍 {inst_row2['Region / City']}</b> ({inst_row2['Status']}).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: MASTER DATA TABLE & EXPORT
# ---------------------------------------------------------
with tab3:
    st.markdown("### 📋 Complete Seat Matrix Master Table (HU, OHU, SL, CAP, AI, Inst Seats)")
    st.caption("Search, sort, and download complete college seat matrices with all quota types across Maharashtra")

    search_query = st.text_input("🔍 Search College Name, Code, City, or Course:", "", key="master_search_input_full")

    df_display = df_inst_filtered.copy()
    if search_query:
        df_display = df_display[
            df_display["Institute Name"].str.contains(search_query, case=False, na=False) |
            df_display["Institute Code"].str.contains(search_query, case=False, na=False) |
            df_display["Region / City"].str.contains(search_query, case=False, na=False) |
            df_display["Course Name"].str.contains(search_query, case=False, na=False)
        ]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Choice Code": st.column_config.TextColumn("Choice Code"),
            "Institute Code": st.column_config.TextColumn("Code"),
            "Sanctioned Intake (SI)": st.column_config.NumberColumn("Intake (SI)", format="%d"),
            "CAP Total Seats": st.column_config.NumberColumn("CAP Total", format="%d"),
            "Home University (HU) Seats": st.column_config.NumberColumn("HU Seats", format="%d"),
            "Other than Home University (OHU) Seats": st.column_config.NumberColumn("OHU Seats", format="%d"),
            "All India Seats": st.column_config.NumberColumn("AI Seats", format="%d"),
            "Institute Seats": st.column_config.NumberColumn("Mgmt Seats", format="%d"),
            "EWS Seats": st.column_config.NumberColumn("EWS Seats", format="%d"),
        }
    )

    ex_col1, ex_col2 = st.columns([3, 9])
    with ex_col1:
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Master Data as CSV",
            data=csv_data,
            file_name="MAH_CET_Seat_Matrix_Full_Master.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---------------------------------------------------------
# TAB 4: PDF PARSING INSPECTOR
# ---------------------------------------------------------
with tab4:
    st.markdown("### 📤 PDF Extraction Inspector")
    st.write("""
    Upload your official MAH-CET BBA/BCA/BMS/BBM Seat Matrix PDF to test live parsing logic.
    The parser uses **`pdfplumber`** and **`PyMuPDF`** to automatically extract all ~438 pages.
    """)

    inspect_pdf = st.file_uploader("Upload PDF file for inspection:", type=["pdf"], key="inspector_pdf_uploader")
    if inspect_pdf:
        st.success(f"File loaded: **{inspect_pdf.name}** ({inspect_pdf.size / 1024:.1f} KB)")
        try:
            pdf_bytes = io.BytesIO(inspect_pdf.read())
            df_parsed_inst, df_parsed_cat = parse_seat_matrix_pdf(pdf_bytes)

            if not df_parsed_inst.empty:
                st.markdown(f"#### ✅ Successfully Extracted {len(df_parsed_inst)} Colleges")
                st.dataframe(df_parsed_inst, use_container_width=True)
                if not df_parsed_cat.empty:
                    st.markdown(f"#### ✅ Extracted Category Matrix Grid")
                    st.dataframe(df_parsed_cat, use_container_width=True)
            else:
                st.info("PDF upload processed. Standard structure detected, fallback demo mode available.")
        except Exception as e:
            st.error(f"Error inspecting PDF: {e}")
