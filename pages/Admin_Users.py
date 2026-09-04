"""Admin User Management — Day 5."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_admin, render_admin_sidebar
from components.icons import svg as _icon
from database.repositories import day5_repository as repo

st.set_page_config(page_title="User Management — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_admin()
render_admin_sidebar()

actor_id = st.session_state["user_id"]
actor_email = st.session_state.get("user_email", "admin")

st.markdown(
f"""<div style="padding:0.5rem 0 1rem 0;">
<h1 style="color:#1B2A4A;margin:0 0 0.2rem 0;font-size:1.7rem;">
{_icon("people",22,"#2E7D32")} User Management
</h1>
<p style="color:#616161;font-size:0.95rem;margin:0;">
View and manage all registered users.
</p>
</div>""",
    unsafe_allow_html=True,
)

if st.button("← Admin Dashboard", key="um_back"):
    st.switch_page("pages/Admin_Dashboard.py")

st.markdown("---")

# ── Feedback area ─────────────────────────────────────
if st.session_state.pop("_um_success", None):
    st.success(st.session_state.pop("_um_msg", "Done."))

# ── User table ────────────────────────────────────────
try:
    users = repo.get_all_users()
except Exception as exc:
    st.error(f"Could not load users: {exc}")
    st.stop()

if not users:
    st.info("No users found.")
    st.stop()

st.caption(f"{len(users)} user(s) registered")

# Header
hdr = st.columns([3, 3, 2, 2, 2])
for col, label in zip(hdr, ["Name", "Email", "Role", "Status", "Action"]):
    col.markdown(f"**{label}**")

st.markdown("<hr style='margin:0.3rem 0;'>", unsafe_allow_html=True)

for u in users:
    uid = u["id"]
    is_active = bool(u["is_active"])
    is_self = uid == actor_id

    row = st.columns([3, 3, 2, 2, 2])
    row[0].write(u["full_name"])
    row[1].write(u["email"])
    row[2].write(u["role"])
    row[3].write("Active" if is_active else "Deactivated")

    with row[4]:
        if is_self:
            st.caption("(you)")
        elif u["role"] == "ADMIN":
            st.caption("—")
        elif is_active:
            if st.button("Deactivate", key=f"um_deact_{uid}"):
                try:
                    repo.set_user_active(uid, False)
                    repo.log_action(actor_id, actor_email, "deactivate_user",
                                    "user", uid, f"Deactivated user {u['email']}")
                    st.session_state["_um_success"] = True
                    st.session_state["_um_msg"] = f"User {u['email']} deactivated."
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        else:
            if st.button("Activate", key=f"um_act_{uid}"):
                try:
                    repo.set_user_active(uid, True)
                    repo.log_action(actor_id, actor_email, "activate_user",
                                    "user", uid, f"Activated user {u['email']}")
                    st.session_state["_um_success"] = True
                    st.session_state["_um_msg"] = f"User {u['email']} activated."
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
