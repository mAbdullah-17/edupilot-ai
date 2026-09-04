"""Shared sidebar / navigation component.

Layout: single-line logo+name, initial avatar, nav list, green logout.
"""

import streamlit as st
from components.icons import svg as _icon

# ── Base64 logo icon (sidebar size) ───────────────────
_LOGO_B64 = (
    "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"
    "ewErMD/AApRULk9lZl9AAAAAElFTKSuQmCC"
)

# ── Sidebar CSS — active pill + consistent styling ──
_SIDEBAR_CSS = """
<style>
/* Sidebar nav link base styling — covers both stPageLink and stSidebarNavLink */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    margin: 2px 0;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    padding: 0.35rem 0.8rem !important;
    text-decoration: none !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: #1B2A4A !important;
    background: transparent !important;
    transition: background 0.15s ease;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a p,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] p {
    color: #1B2A4A !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
    background: #F5F7FA !important;
}
/* Active page — green pill, white text */
section[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"],
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #2E7D32 !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a p,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] p,
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] p {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a:hover,
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"]:hover {
    background: #256b29 !important;
}
/* Page link icon span — hide default Streamlit icon */
section[data-testid="stSidebar"] [data-testid="stPageLink"] a span[data-testid="stPageLinkIcon"],
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] svg {
    display: none !important;
}
</style>
"""

# ── Styled disabled nav item HTML ─────────────────────
_DISABLED_NAV = """
<div style="
    padding: 0.5rem 0.8rem; margin: 0.15rem 0; border-radius: 8px;
    color: #1B2A4A; font-size: 0.9rem; display: flex; align-items: center;
    gap: 0.5rem; font-weight: 500; opacity: 0.55; cursor: default;
">
    {icon}
    <span>{label}</span>
    <span style="font-size: 0.6rem; margin-left: auto;
                 background: #F5F7FA; padding: 0.1rem 0.4rem;
                 border-radius: 4px; color: #999;">Soon</span>
</div>
"""

def _perform_logout():
    """Clear all session state and redirect to Login."""
    st.session_state.clear()
    st.switch_page("pages/Login.py")


def _render_brand_header():
    """Render single-line logo icon + 'EduPilot AI' text."""
    st.markdown(
        f"""<div style="display:flex; align-items:center; gap:0.5rem;
                        margin-bottom:0.6rem; white-space:nowrap;">
            <img src="data:image/png;base64,{_LOGO_B64}"
                 alt="" style="height:28px; width:auto;" />
            <span style="font-size:1.15rem; font-weight:700; color:#1B2A4A;">
                EduPilot <span style="color:#2E7D32;">AI</span>
            </span>
        </div>""",
        unsafe_allow_html=True,
    )


def _render_avatar(user_name: str, size: int = 48):
    """Render the circular initial-letter avatar inline."""
    initial = user_name[0].upper() if user_name else "?"
    st.markdown(
        f"""<div style="
            width:{size}px; height:{size}px; border-radius:50%;
            background: linear-gradient(135deg, #2E7D32, #1B5E20);
            color:white;
            display:flex; align-items:center; justify-content:center;
            font-size:{size // 2}px; font-weight:bold;
            border: 2px solid #E0E0E0;
        ">{initial}</div>""",
        unsafe_allow_html=True,
    )


def _render_profile_section(user_id: int, user_name: str):
    """Render avatar + user menu dropdown inline."""
    role_label = "Student" if st.session_state.get("role") != "ADMIN" else "Administrator"

    col_img, col_name = st.columns([1, 3])
    with col_img:
        _render_avatar(user_name)
    with col_name:
        st.markdown(
            f"""<div style="padding-top: 0.35rem;">
                <div style="color: #1B2A4A; font-weight: 600; font-size: 0.85rem;">
                    {user_name}
                </div>
                <div style="color: #666666; font-size: 0.72rem;">
                    {role_label}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    action = st.selectbox(
        "User Menu",
        ["\u2014", "View Profile", "Edit Profile", "Settings"],
        key="sidebar_user_menu",
        label_visibility="collapsed",
    )

    if action == "View Profile":
        st.session_state["_profile_view"] = True
        st.switch_page("pages/Dashboard.py")
    elif action == "Edit Profile":
        st.switch_page("pages/Profile_Setup.py")
    elif action == "Settings":
        st.switch_page("pages/Settings.py")


def render_student_sidebar():
    """Render the student sidebar with brand header, avatar, nav, and logout."""
    with st.sidebar:
        # ── Inject sidebar CSS for active pill ──
        st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

        # ── Brand header: logo + name on single line ──
        _render_brand_header()

        st.markdown("---")

        # ── Profile section ──
        user_id = st.session_state.get("user_id", 0)
        user_name = st.session_state.get("user_name", "Student")
        _render_profile_section(user_id, user_name)

        st.markdown("---")

        # ── Navigation links ──
        st.page_link("pages/Dashboard.py", label="Dashboard")
        st.page_link("pages/All_Opportunities.py", label="All Opportunities")

        # Day 3: Eligibility & Applications
        st.page_link("pages/For_Me.py", label="For Me")
        st.page_link("pages/Relevant_Opportunities.py", label="Relevant Opportunities")
        st.page_link("pages/My_Applications.py", label="My Applications")
        st.page_link("pages/Eligibility_Analysis.py", label="Eligibility Analysis")

        # Day 4: AI Student Tools
        st.page_link("pages/AI_Chat.py", label="AI Chat")
        st.page_link("pages/Study_Assistant.py", label="Study Assistant")
        st.page_link("pages/Career_Assistant.py", label="Career Assistant")
        st.page_link("pages/Resume_Analyzer.py", label="Resume Analyzer")
        st.page_link("pages/Interview_Coach.py", label="Interview Coach")

        # Day 5: Notifications
        st.page_link("pages/Notifications.py", label="Notifications")

        st.markdown("---")

        # Settings
        st.page_link("pages/Settings.py", label="Settings")

        st.markdown("---")

        # ── Logout — green styled ──
        if st.button("Logout", key="sidebar_logout_btn",
                     use_container_width=True, type="primary"):
            _perform_logout()


def render_admin_sidebar():
    """Render the admin sidebar with brand header, avatar + name inline, and logout."""
    with st.sidebar:
        # ── Inject sidebar CSS for active pill ──
        st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

        _render_brand_header()

        st.markdown("---")

        user_id = st.session_state.get("user_id", 0)
        admin_name = st.session_state.get("user_name", "Administrator")

        # ── Avatar + name ──
        col_img, col_name = st.columns([1, 3])
        with col_img:
            _render_avatar(admin_name)
        with col_name:
            st.markdown(
                f"""<div style="padding-top: 0.35rem;">
                    <div style="color: #1B2A4A; font-weight: 600; font-size: 0.85rem;">
                        {admin_name}
                    </div>
                    <div style="color: #666666; font-size: 0.72rem;">
                        Administrator
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        action = st.selectbox(
            "Admin Menu",
            ["\u2014", "View Profile", "Edit Profile", "Settings"],
            key="admin_sidebar_user_menu",
            label_visibility="collapsed",
        )

        if action == "View Profile":
            st.session_state["_profile_view"] = True
            st.switch_page("pages/Dashboard.py")
        elif action == "Edit Profile":
            st.switch_page("pages/Profile_Setup.py")
        elif action == "Settings":
            st.switch_page("pages/Settings.py")

        st.markdown("---")

        st.page_link("pages/Admin_Dashboard.py", label="Admin Dashboard")
        st.page_link("pages/Admin_Users.py", label="User Management")
        st.page_link("pages/Admin_Opportunities.py", label="Opportunity Management")
        st.page_link("pages/Admin_Audit.py", label="Audit Logs")
        st.page_link("pages/Notifications.py", label="Notifications")

        st.markdown("---")

        if st.button("Logout", key="admin_logout_btn",
                     use_container_width=True, type="primary"):
            _perform_logout()


def require_login():
    """Guard: redirect to Login if no authenticated session."""
    if not st.session_state.get("authenticated"):
        st.switch_page("pages/Login.py")


def require_admin():
    """Guard: redirect to Login if not an authenticated admin."""
    require_login()
    if st.session_state.get("role") != "ADMIN":
        st.error("Access denied.")
        st.stop()
