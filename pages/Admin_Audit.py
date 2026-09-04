"""Admin Audit Logs — Day 5."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_admin, render_admin_sidebar
from components.icons import svg as _icon
from database.repositories import day5_repository as repo

st.set_page_config(page_title="Audit Logs — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_admin()
render_admin_sidebar()

st.markdown(
f"""<div style="padding:0.5rem 0 1rem 0;">
<h1 style="color:#1B2A4A;margin:0 0 0.2rem 0;font-size:1.7rem;">
{_icon("list_alt",22,"#009688")} Audit Logs
</h1>
<p style="color:#616161;font-size:0.95rem;margin:0;">
Administrative action history.
</p>
</div>""",
    unsafe_allow_html=True,
)

if st.button("← Admin Dashboard", key="audit_back"):
    st.switch_page("pages/Admin_Dashboard.py")

st.markdown("---")

try:
    logs = repo.get_audit_logs(limit=200)
except Exception as exc:
    st.error(f"Could not load audit logs: {exc}")
    st.stop()

if not logs:
    st.info("No audit log entries yet. Admin actions will appear here.")
    st.stop()

st.caption(f"{len(logs)} log entries (most recent first)")

hdr = st.columns([2, 3, 2, 3, 2])
for col, lbl in zip(hdr, ["Timestamp", "Actor", "Action", "Details", "Entity"]):
    col.markdown(f"**{lbl}**")

st.markdown("<hr style='margin:0.3rem 0;'>", unsafe_allow_html=True)

for log in logs:
    row = st.columns([2, 3, 2, 3, 2])
    ts = log["created_at"]
    ts_str = ts.strftime("%d %b %Y %H:%M") if hasattr(ts, "strftime") else str(ts)
    row[0].caption(ts_str)
    row[1].write(log.get("actor_email", "—"))
    row[2].write(log.get("action", "—").replace("_", " ").title())
    row[3].caption(log.get("details") or "—")
    entity = ""
    if log.get("entity_type"):
        entity = f"{log['entity_type']} #{log.get('entity_id', '?')}"
    row[4].caption(entity or "—")
