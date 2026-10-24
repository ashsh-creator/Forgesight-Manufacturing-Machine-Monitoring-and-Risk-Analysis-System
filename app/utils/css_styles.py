"""Shared ForgeSight light-theme styles.

Drop-in replacement for app/utils/css_styles.py.
Preserves get_common_styles, get_dashboard_styles and
get_component_specific_styles for existing imports.
"""


def get_common_styles():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --fs-primary:#2457C5; --fs-primary-dark:#1945A5;
  --fs-primary-light:#EDF3FF; --fs-bg:#F5F7FB;
  --fs-surface:#FFFFFF; --fs-border:#E3E8F0;
  --fs-text:#17243A; --fs-muted:#68768B;
  --fs-success:#16845B; --fs-warning:#B7791F;
  --fs-danger:#C43D4B; --fs-radius:12px;
}
html, body, .stApp, [data-testid="stApp"],
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
  font-family:'Inter',sans-serif !important;
  background:#F5F7FB !important; color:#17243A !important;
}
[data-testid="stHeader"] {background:#F5F7FB !important;}
/* The central application panel remains white; the surrounding canvas is pale blue-gray. */
[data-testid="stMainBlockContainer"], .main .block-container {
  background:#FFFFFF !important;
  max-width:1500px;
  padding:1.8rem 2.2rem 3rem !important;
  box-sizing:border-box;
}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6 {
  color:#17243A !important; font-weight:700; letter-spacing:-.025em;
}
.stApp p,.stApp label {line-height:1.55;}
section[data-testid="stSidebar"] {background:#FFFFFF; border-right:1px solid #E3E8F0;}
.stButton > button,.stDownloadButton > button {
  background:#FFFFFF !important; color:#2457C5 !important;
  border:1px solid #DCE5F2 !important; border-radius:8px !important;
  min-height:40px; font-weight:600; box-shadow:none !important;
}
.stButton > button:hover,.stDownloadButton > button:hover {
  background:#EDF3FF !important; color:#1945A5 !important;
  border-color:#2457C5 !important;
}
.stButton > button[kind="primary"],.stDownloadButton > button[kind="primary"] {
  background:#2457C5 !important; color:#FFFFFF !important;
  border-color:#2457C5 !important;
}
.stButton > button[kind="primary"]:hover,.stDownloadButton > button[kind="primary"]:hover {
  background:#1945A5 !important; color:#FFFFFF !important;
}
.stTextInput input,.stNumberInput input,.stTextArea textarea {
  background:#FFFFFF !important; color:#17243A !important;
  border:1px solid #DCE5F2 !important; border-radius:8px !important;
}
.stTextInput input::placeholder {color:#94A3B8 !important;}
.stTextInput input:focus {border-color:#2457C5 !important; box-shadow:0 0 0 1px #2457C5 !important;}
.stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background:#FFFFFF !important; color:#17243A !important;
  border-color:#DCE5F2 !important; border-radius:8px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {color:#17243A !important;}
div[data-baseweb="popover"],ul[role="listbox"],li[role="option"] {
  background:#FFFFFF !important; color:#17243A !important;
}
li[role="option"]:hover,li[role="option"][aria-selected="true"] {
  background:#EDF3FF !important; color:#2457C5 !important;
}
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stExpander"] {
  background:#FFFFFF !important; border-color:#E3E8F0 !important;
  border-radius:12px !important; color:#17243A !important;
}
.common-card,.professional-card,.metric-card,.maintenance-card,.alert-item {
  background:#FFFFFF; border:1px solid #E3E8F0;
  border-radius:12px; padding:1.25rem;
  box-shadow:0 2px 8px rgba(23,36,58,.035);
}
.metric-card {border-left:3px solid #2457C5;}
.professional-card {min-height:120px; display:flex; align-items:center; justify-content:space-between; gap:1rem;}
[data-testid="stMetric"] {
  background:#FFFFFF; border:1px solid #E3E8F0;
  border-radius:12px; padding:1.1rem 1.25rem;
}
[data-testid="stMetricLabel"] {color:#68768B; font-weight:600;}
[data-testid="stMetricValue"] {color:#17243A; font-size:1.8rem; font-weight:700;}
[data-testid="stDataFrame"],[data-testid="stTable"] {
  border:1px solid #E3E8F0; border-radius:10px; overflow:hidden;
}
[data-testid="stAlert"] {border-radius:10px;}
.alert-high {background:#FFF1F2; border-left:4px solid #C43D4B;}
.alert-medium {background:#FFF8E8; border-left:4px solid #B7791F;}
.alert-low {background:#ECFDF5; border-left:4px solid #16845B;}
.main-header {font-size:2.2rem; font-weight:800; color:#17243A; margin-bottom:.4rem;}
.header-subtitle {font-size:1rem; color:#68768B; margin-bottom:1.5rem;}
.header-stats {display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; margin-top:1rem;}
.stat-item {color:#17243A; margin:.25rem 0;}
.stat-number {display:block; font-size:1.5rem; font-weight:700; color:#2457C5;}
.stat-label,.last-updated {font-size:.85rem; color:#68768B;}
.company-logo {font-size:1.35rem; font-weight:800; color:#2457C5;}
.footer {border-top:1px solid #E3E8F0; padding:1.25rem 0; margin-top:2rem; text-align:center; color:#68768B; font-size:.82rem;}
.footer-links a {color:#2457C5; text-decoration:none; margin:0 .5rem;}
.landing-header {background:#FFFFFF; padding:1rem 1.25rem; border:1px solid #E3E8F0; border-radius:10px; margin-bottom:1.5rem;}
.landing-header-content,.landing-header-left {display:flex; align-items:center; justify-content:space-between; gap:1rem;}
.landing-content {display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:50vh; text-align:center; padding:2rem;}
.welcome-title {font-size:2.3rem; font-weight:800; color:#17243A;}
.welcome-subtitle {font-size:1.05rem; color:#68768B; max-width:680px;}
.table-header-row,.machines-table-row {display:grid; grid-template-columns:repeat(8,minmax(0,1fr)); align-items:center; gap:.65rem; padding:.8rem; border:1px solid #E3E8F0;}
.table-header-row {background:#F0F4FA; border-radius:8px 8px 0 0;}
.machines-table-row {background:#FFFFFF; border-top:0;}
.table-header-cell,.table-cell {min-width:0; overflow-wrap:anywhere; font-size:.82rem;}
.machine-details-header {border-bottom:1px solid #E3E8F0; padding-bottom:.8rem; margin-bottom:1rem;}
.service-notes-section {background:#F8FAFD; border:1px solid #E3E8F0; border-radius:8px; padding:1rem;}
/* The Plotly chart is its own card. Do not add a second outer card or clip its labels. */
[data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"] {
  background:#FFFFFF; border:1px solid #E3E8F0;
  border-radius:12px; padding:1rem 1.15rem !important;
  box-sizing:border-box; overflow:visible;
}
@media(max-width:900px) {
  [data-testid="stMainBlockContainer"],.main .block-container {padding:1.2rem 1rem 2rem !important;}
  .table-header-row,.machines-table-row {gap:.35rem;}
}
@media(max-width:600px) {
  .professional-card {min-height:auto; padding:1rem;}
  .landing-header-content,.landing-header-left {flex-wrap:wrap;}
}
</style>
"""


def get_dashboard_styles():
    """Dashboard card spacing; injected by the existing main.py."""
    return """
<style>
/* Custom dashboard cards: padding belongs on the card itself, not on st.columns. */
.fs-metric,.fs-metric-card,.fs-risk-card,.fs-machine-card,
.fs-risk-summary,.fs-risk-machine,.fs-chart-card {
  box-sizing:border-box;
  border-radius:12px;
}
.fs-metric,.fs-metric-card {
  padding:1.35rem 1.4rem !important;
  min-height:126px;
}
.fs-risk-card,.fs-risk-summary {padding:1.25rem 1.35rem !important;}
.fs-machine-card,.fs-risk-machine {padding:1rem 1.2rem !important;}
.fs-chart-card {padding:1.1rem 1.25rem !important;}
.fs-section-title,.dashboard-section-title {
  font-size:1.15rem; font-weight:700; color:#17243A;
  margin:1.4rem 0 .9rem;
}
/* Don't apply padding to Streamlit columns: that shrinks chart widths and breaks grids. */
</style>
"""


def get_component_specific_styles(component_name):
    """Maintain compatibility with existing component-specific imports."""
    styles = {
        'landing_page': '.landing-header{margin-bottom:1.5rem}.landing-content{min-height:50vh}',
        'dashboard': '.dashboard-section-title{font-size:1.15rem;font-weight:700;color:#17243A;margin-bottom:.75rem}',
        'machines': '.machine-status{display:inline-block;border-radius:20px;padding:.25rem .65rem;font-size:.78rem;font-weight:600}',
        'machine_details': '.machine-details-header{border-bottom:1px solid #E3E8F0;padding-bottom:.8rem}',
        'maintenance': '.maintenance-card{padding:1.25rem;margin-bottom:1rem}',
        'alerts': '.alert-item{padding:1rem;margin-bottom:.75rem}',
    }
    return '<style>' + styles.get(str(component_name).lower(), '') + '</style>'
