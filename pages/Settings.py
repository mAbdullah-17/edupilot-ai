"""Settings page — notification, language, location preferences."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar, render_admin_sidebar
from components.icons import svg as _icon
from modules.profile import get_user_preferences, save_user_preferences
from database.repositories import day5_repository as notif_repo

st.set_page_config(page_title="Settings — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()

# ── Sidebar ───────────────────────────────────────────
role = st.session_state.get("role")
if role == "ADMIN":
    render_admin_sidebar()
else:
    render_student_sidebar()

# ── Page Header ───────────────────────────────────────
st.markdown(
    f"""<div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: #1B2A4A; margin-bottom: 0.2rem;">{_icon("settings", 22, "#1B2A4A")} Settings</h1>
        <p style="color: #616161; font-size: 1rem;">
            Manage your application preferences.
        </p>
    </div>""",
    unsafe_allow_html=True,
)

user_id = st.session_state["user_id"]

# Load current preferences from MySQL
prefs = get_user_preferences(user_id)

# ── Notification Preferences ─────────────────────────
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
        border-left: 4px solid #2E7D32;
    ">
        <h4 style="color: #1B2A4A; margin: 0;">{_icon("notifications", 20, "#1B2A4A")} Notifications</h4>
    </div>""",
    unsafe_allow_html=True,
)

with st.form("settings_form"):
    notif_enabled = st.checkbox(
        "Enable in-app notifications",
        value=bool(prefs.get("notification_enabled", True)),
        key="set_notif",
    )
    email_enabled = st.checkbox(
        "Enable email notifications",
        value=bool(prefs.get("email_enabled", True)),
        key="set_email",
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ── Language & Location ──────────────────────────
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
            padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            margin-bottom: 0.5rem; border-left: 4px solid #009688;
        ">
            <h5 style="color: #1B2A4A; margin: 0;">{_icon("globe", 20, "#1B2A4A")} Language & Location</h5>
        </div>""",
        unsafe_allow_html=True,
    )

    language = st.selectbox(
        "Preferred Language",
        ["en", "ur", "ar", "es", "fr", "de", "zh"],
        index=["en", "ur", "ar", "es", "fr", "de", "zh"].index(
            prefs.get("preferred_language", "en")
        ) if prefs.get("preferred_language", "en") in
            ["en", "ur", "ar", "es", "fr", "de", "zh"] else 0,
        key="set_lang",
    )
    location = st.text_input(
        "Preferred Location",
        value=prefs.get("preferred_location", "") or "",
        key="set_location",
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    btn_save = st.form_submit_button(
        "Save Settings", type="primary", use_container_width=True
    )

if btn_save:
    save_user_preferences(user_id, {
        "notification_enabled": notif_enabled,
        "email_enabled": email_enabled,
        "preferred_language": language,
        "preferred_location": location if location else None,
    })
    st.success("Settings saved successfully.")
    # Seed a welcome notification when preferences are saved (only if none exist)
    try:
        existing = notif_repo.get_user_notifications(user_id, limit=1)
        if not existing:
            notif_repo.create_notification(
                user_id, "Welcome to EduPilot AI",
                "Your settings have been saved. Explore opportunities, AI tools, and more!",
                "success",
            )
    except Exception:
        pass

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Additional settings sections (reference: green sidebar panel) ──
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
            padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            margin-bottom: 1rem; border-left: 4px solid #1B2A4A;
        ">
            <h4 style="color: #1B2A4A; margin: 0 0 0.8rem 0;">{_icon("lock", 20, "#1B2A4A")} Privacy & Security</h4>
            <p style="color: #616161; font-size: 0.9rem; margin: 0;">
                Password management and account security settings.
            </p>
            <div style="color: #9E9E9E; font-size: 0.8rem; margin-top: 0.5rem;">
                Password hashing: Active &nbsp;|&nbsp; Two-factor auth: Coming soon
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
            padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            margin-bottom: 1rem; border-left: 4px solid #FFA000;
        ">
            <h4 style="color: #1B2A4A; margin: 0 0 0.8rem 0;">{_icon("palette", 20, "#1B2A4A")} Appearance</h4>
            <p style="color: #616161; font-size: 0.9rem; margin: 0;">
                Theme and display preferences.
            </p>
            <div style="color: #9E9E9E; font-size: 0.8rem; margin-top: 0.5rem;">
                Theme: EduPilot Green &nbsp;|&nbsp; Dark mode: Coming soon
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.button("← Back to Dashboard", key="settings_back"):
        st.switch_page("pages/Dashboard.py")
with col_s2:
    if st.button("View Notifications", key="settings_to_notif"):
        st.switch_page("pages/Notifications.py")
