"""EduPilot AI — main entry point.

Run with:  streamlit run app.py
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from modules.auth import bootstrap_admin

# ── Page config ────────────────────────────────────────
st.set_page_config(
    page_title="EduPilot AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject custom theme CSS ───────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Bootstrap: ensure database & admin account exist ──
try:
    from database.database import get_db
    get_db()  # triggers DB creation + schema migration
    bootstrap_admin()
except Exception as e:
    st.error(f"Application startup failed: {e}")
    st.stop()

# ── Initialise session state defaults ─────────────────
_defaults = {
    "authenticated": False,
    "user_id": None,
    "user_name": "",
    "role": None,
    "completed_profile_sections": set(),
}
for key, value in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ── Route to Login if not authenticated ───────────────
if not st.session_state.get("authenticated"):
    st.switch_page("pages/Login.py")
else:
    st.switch_page("pages/Dashboard.py")
