"""EduPilot AI design-system colour palette and shared styles."""

# ── Colour palette (Section 04) ───────────────────────

PRIMARY = "#2E7D32"          # Green — buttons, active states, success
BASE = "#FFFFFF"             # White — backgrounds, cards
DARK_NAVY = "#1B2A4A"        # Sidebar, headings, strong contrast
LIGHT_GREEN = "#E8F5E9"      # Highlights, selected cards
TEAL = "#009688"             # Secondary accent
GRAY = "#9E9E9E"             # Borders, secondary text, disabled
LIGHT_GRAY = "#F5F7FA"       # Page backgrounds
AMBER = "#FFA000"            # Pending / Cannot Determine
RED = "#D32F2F"              # Errors / Not Eligible (used sparingly)

# ── Status colours ────────────────────────────────────
STATUS_GREEN = PRIMARY
STATUS_AMBER = AMBER
STATUS_RED = RED

# ── Streamlit custom CSS ─────────────────────────────

CUSTOM_CSS = """
<style>
    /* ── Global page background ── */
    .stApp {
        background-color: #F5F7FA;
    }

    /* ── Main content area ── */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ── Headings ── */
    h1, h2, h3, h4, h5, h6 {
        color: #1B2A4A;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    /* ── Sidebar base styling — WHITE with light-gray border ── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        padding-top: 1rem;
        border-right: 1px solid #E0E0E0;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        color: #1B2A4A;
    }
    section[data-testid="stSidebar"] .stMarkdown hr {
        border-color: #E0E0E0;
        margin: 0.8rem 0;
    }

    /* ── Sidebar buttons — navy text on transparent bg, GREEN on hover ── */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #1B2A4A !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        padding: 0.45rem 1rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        text-align: left;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #E8F5E9 !important;
        color: #2E7D32 !important;
    }
    /* Sidebar logout button — green primary style */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        text-align: center;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #1B5E20 !important;
        color: #FFFFFF !important;
    }

    /* ── Sidebar labels & selectbox ── */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        color: #1B2A4A;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #1B2A4A;
    }

    /* ── Hide Streamlit auto-generated page nav (duplicate links) ── */
    section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] {
        display: none !important;
    }

    /* ── Sidebar page links — navy text, green active pill ── */
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"],
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
        background-color: transparent !important;
        color: #1B2A4A !important;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        margin: 0.15rem 0;
        font-weight: 500;
        transition: background 0.2s ease;
        text-decoration: none !important;
    }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
        background-color: #F5F7FA !important;
        color: #2E7D32 !important;
    }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover svg,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover svg {
        color: #2E7D32 !important;
        stroke: #2E7D32 !important;
    }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover p,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover p {
        color: #2E7D32 !important;
    }
    /* Active page link — solid green pill, white text (Day 3) */
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="true"],
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="true"] {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] p {
        color: inherit !important;
    }
    /* Active nav icon (SVG) white */
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] svg,
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="true"] svg,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] svg,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="true"] svg {
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }

    /* ── Sidebar caption text ── */
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: #666666;
    }

    /* ── Sidebar selectbox styling ── */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #F5F7FA !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 6px !important;
        color: #1B2A4A !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: #2E7D32 !important;
    }

    /* ── Primary button colour — override ALL Streamlit defaults ── */
    .stButton > button[kind="primary"],
    button[data-testid="stFormSubmitButton"],
    button[data-testid="stBaseButton-primary"],
    .stFormSubmitButton button {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="stFormSubmitButton"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    .stFormSubmitButton button:hover {
        background-color: #1B5E20 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(46,125,50,0.25) !important;
    }
    /* Ensure no Streamlit default blue/red bleeds through */
    .stButton > button {
        border-radius: 8px;
    }

    /* ── Links — EduPilot green, not browser blue ── */
    a {
        color: #2E7D32;
    }
    a:hover {
        color: #1B5E20;
    }

    /* ── Checkbox accent — EduPilot green ── */
    input[type="checkbox"]:checked {
        accent-color: #2E7D32 !important;
    }
    /* Streamlit custom checkbox */
    .stCheckbox label {
        color: #1B2A4A;
    }
    .stCheckbox [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] {
        background-color: #2E7D32 !important;
        border-color: #2E7D32 !important;
    }
    .stCheckbox [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] svg {
        color: #FFFFFF !important;
    }
    /* Streamlit v1.30+ checkbox targeting */
    div[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {
        background-color: #2E7D32 !important;
        border-color: #2E7D32 !important;
    }
    div[data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] svg {
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label {
        color: #1B2A4A;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #2E7D32;
    }

    /* ── Progress bar ── */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #2E7D32;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F5F7FA;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
        color: #1B2A4A;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        border-bottom: 3px solid #2E7D32 !important;
        color: #2E7D32 !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        color: #1B2A4A;
        font-weight: 500;
        border-radius: 8px;
    }

    /* ── Text inputs ── */
    input[type="text"],
    input[type="password"],
    input[type="email"],
    textarea {
        border-radius: 6px !important;
        border: 1px solid #E0E0E0 !important;
    }
    input[type="text"]:focus,
    input[type="password"]:focus,
    input[type="email"]:focus,
    textarea:focus {
        border-color: #2E7D32 !important;
        box-shadow: 0 0 0 2px rgba(46,125,50,0.15) !important;
    }

    /* ── Success card ── */
    .success-card {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D32;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    /* ── Warning card ── */
    .warning-card {
        background-color: #FFF8E1;
        border-left: 4px solid #FFA000;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    /* ── Error card ── */
    .error-card {
        background-color: #FFEBEE;
        border-left: 4px solid #D32F2F;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    /* ── Dashboard card ── */
    .edu-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .edu-card h4 {
        color: #1B2A4A;
        margin-bottom: 0.5rem;
    }
    .edu-card p {
        color: #616161;
    }

    /* ── Feature card (placeholder) ── */
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        opacity: 0.75;
    }
    .feature-card h5 {
        color: #1B2A4A;
        margin-bottom: 0.4rem;
    }

    /* ── Login / Registration unified card ── */
    .auth-card-outer {
        display: flex;
        max-width: 900px;
        margin: 2rem auto;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        border: 1px solid #E0E0E0;
    }
    .auth-form-panel {
        flex: 1.15;
        padding: 2.5rem 2rem;
        background: #FFFFFF;
    }
    .auth-illust-panel {
        flex: 0.85;
        background: #2E7D32;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .auth-illust-panel img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* ── Hide Streamlit default hamburger menu on login ── */
    .login-page #MainMenu {
        visibility: hidden;
    }

    /* ── Hide sidebar completely on auth pages (Login & Registration) ── */
    button[data-testid="stSidebarCollapsedControl"],
    button[title="Expand sidebar"] {
        display: none !important;
    }
</style>
"""
