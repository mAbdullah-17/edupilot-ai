"""Admin Dashboard — Day 5. Real database metrics."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_admin, render_admin_sidebar
from components.icons import svg as _icon
from database.repositories import day5_repository as repo
from modules.opportunities import count_opportunities

st.set_page_config(page_title="Admin Dashboard — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_admin()
render_admin_sidebar()

admin_name = st.session_state.get("user_name", "Administrator")

st.markdown(
f"""<div style="padding:0.5rem 0 1rem 0;">
<h1 style="color:#1B2A4A;margin:0 0 0.2rem 0;font-size:1.7rem;">
{_icon("shield", 22, "#2E7D32")} Admin Dashboard
</h1>
<p style="color:#616161;font-size:0.95rem;margin:0;">
System overview and management — {admin_name}
</p>
</div>""",
    unsafe_allow_html=True,
)

# ── Live metrics ──────────────────────────────────────
try:
    total_users = repo.count_users()
    active_students = repo.count_active_students()
    active_opps = count_opportunities()
    total_apps = repo.count_total_applications()
    total_audits = repo.count_audit_logs()
except Exception:
    total_users = active_students = active_opps = total_apps = total_audits = "—"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Users", total_users)
with c2:
    st.metric("Active Students", active_students)
with c3:
    st.metric("Active Opportunities", active_opps)
with c4:
    st.metric("Total Applications", total_apps)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Navigation cards ──────────────────────────────────
st.markdown(
"<h4 style='color:#1B2A4A;margin:0 0 0.8rem 0;'>Management</h4>",
    unsafe_allow_html=True,
)

nav_cols = st.columns(3)

with nav_cols[0]:
    st.markdown(
f"""<div style="background:#FFFFFF;border:1px solid #E0E0E0;border-radius:12px;
padding:1.2rem;box-shadow:0 2px 6px rgba(0,0,0,0.06);border-left:4px solid #2E7D32;
margin-bottom:0.5rem;">
<h5 style="color:#1B2A4A;margin:0 0 0.4rem 0;">{_icon("people",18,"#2E7D32")} User Management</h5>
<p style="color:#616161;font-size:0.85rem;margin:0;">View and manage student accounts.</p>
</div>""",
        unsafe_allow_html=True,
    )
    if st.button("Open User Management", key="admin_nav_users", use_container_width=True):
        st.switch_page("pages/Admin_Users.py")

with nav_cols[1]:
    st.markdown(
f"""<div style="background:#FFFFFF;border:1px solid #E0E0E0;border-radius:12px;
padding:1.2rem;box-shadow:0 2px 6px rgba(0,0,0,0.06);border-left:4px solid #1B2A4A;
margin-bottom:0.5rem;">
<h5 style="color:#1B2A4A;margin:0 0 0.4rem 0;">{_icon("work",18,"#1B2A4A")} Opportunity Management</h5>
<p style="color:#616161;font-size:0.85rem;margin:0;">Create, edit, and archive opportunities.</p>
</div>""",
        unsafe_allow_html=True,
    )
    if st.button("Open Opportunities", key="admin_nav_opps", use_container_width=True):
        st.switch_page("pages/Admin_Opportunities.py")

with nav_cols[2]:
    st.markdown(
f"""<div style="background:#FFFFFF;border:1px solid #E0E0E0;border-radius:12px;
padding:1.2rem;box-shadow:0 2px 6px rgba(0,0,0,0.06);border-left:4px solid #009688;
margin-bottom:0.5rem;">
<h5 style="color:#1B2A4A;margin:0 0 0.4rem 0;">{_icon("list_alt",18,"#009688")} Audit Logs</h5>
<p style="color:#616161;font-size:0.85rem;margin:0;">{total_audits} log entries recorded.</p>
</div>""",
        unsafe_allow_html=True,
    )
    if st.button("View Audit Logs", key="admin_nav_audit", use_container_width=True):
        st.switch_page("pages/Admin_Audit.py")
