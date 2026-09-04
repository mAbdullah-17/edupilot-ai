"""Notifications page — Day 5. In-app notification list with read/unread state."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar, render_admin_sidebar
from components.icons import svg as _icon
from database.repositories import day5_repository as repo

st.set_page_config(page_title="Notifications — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()

role = st.session_state.get("role")
if role == "ADMIN":
    render_admin_sidebar()
else:
    render_student_sidebar()

user_id = st.session_state["user_id"]

st.markdown(
f"""<div style="padding:0.5rem 0 1rem 0;">
<h1 style="color:#1B2A4A;margin:0 0 0.2rem 0;font-size:1.7rem;">
{_icon("notifications",22,"#2E7D32")} Notifications
</h1>
<p style="color:#616161;font-size:0.95rem;margin:0;">
Your in-app notifications.
</p>
</div>""",
    unsafe_allow_html=True,
)

# ── Actions bar ───────────────────────────────────────
try:
    unread = repo.get_unread_count(user_id)
    notifications = repo.get_user_notifications(user_id)
except Exception as exc:
    st.error(f"Could not load notifications: {exc}")
    st.stop()

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.caption(f"{len(notifications)} notification(s) — {unread} unread")
with col_btn:
    if unread > 0:
        if st.button("Mark all as read", key="notif_mark_all",
                     use_container_width=True):
            try:
                repo.mark_all_read(user_id)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

st.markdown("---")

if not notifications:
    st.markdown(
"<div style='text-align:center;padding:3rem 1rem;color:#9E9E9E;'>"
"<div style='font-size:1.1rem;margin-bottom:0.5rem;'>No notifications yet</div>"
"<div>Activity on your account will appear here.</div></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── Notification cards ────────────────────────────────
_TYPE_COLOR = {
    "info": "#1B2A4A",
    "success": "#2E7D32",
    "warning": "#FFA000",
    "error": "#C62828",
}

for n in notifications:
    nid = n["id"]
    is_read = bool(n["is_read"])
    border_color = "#E0E0E0" if is_read else "#2E7D32"
    bg_color = "#FAFAFA" if is_read else "#FFFFFF"
    type_color = _TYPE_COLOR.get(n.get("notif_type", "info"), "#1B2A4A")

    ts = n["created_at"]
    ts_str = ts.strftime("%d %b %Y %H:%M") if hasattr(ts, "strftime") else str(ts)

    st.markdown(
f"""<div style="background:{bg_color};border:1px solid {border_color};
border-left:4px solid {type_color};border-radius:10px;
padding:1rem 1.2rem;margin-bottom:0.6rem;
box-shadow:0 1px 4px rgba(0,0,0,0.05);">
<div style="display:flex;justify-content:space-between;align-items:flex-start;">
<div>
<div style="color:#1B2A4A;font-weight:{'600' if not is_read else '400'};
font-size:0.95rem;">{n['title']}</div>
<div style="color:#616161;font-size:0.85rem;margin-top:0.2rem;">{n['message']}</div>
</div>
<div style="color:#9E9E9E;font-size:0.75rem;white-space:nowrap;margin-left:1rem;">
{ts_str}</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )

    if not is_read:
        btn_cols = st.columns([1, 1, 8])
        with btn_cols[0]:
            if st.button("Mark read", key=f"notif_read_{nid}"):
                try:
                    repo.mark_notification_read(nid, user_id)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with btn_cols[1]:
            if st.button("Delete", key=f"notif_del_{nid}"):
                try:
                    repo.delete_notification(nid, user_id)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    else:
        if st.button("Delete", key=f"notif_del_{nid}"):
            try:
                repo.delete_notification(nid, user_id)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
