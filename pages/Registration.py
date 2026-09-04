"""Screen 2 — Registration / Sign Up.

Visual design: unified rounded card with white form panel (left) seamlessly
joined to a green illustration panel (right).  White page background, no sidebar.
"""

import os
import base64
import streamlit as st
from components.theme import CUSTOM_CSS
from modules.auth import register

st.set_page_config(page_title="Register — EduPilot AI", layout="wide",
                     initial_sidebar_state="collapsed")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Redirect if already authenticated ─────────────────
if st.session_state.get("authenticated"):
    st.switch_page("pages/Dashboard.py")

# ── Asset paths ───────────────────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ILLUST_IMG = os.path.join(_BASE, "assets", "login_panel.png")
_LOGO_IMG = os.path.join(_BASE, "assets", "logo_icon.png")

# ── Card CSS (scoped to auth-card wrapper) ────────────
_CARD_CSS = """
<style>
    /* ── Auth card column layout (the ONLY stHorizontalBlock on this page is the auth card) ── */
    [data-testid="stHorizontalBlock"] {
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        border: 1px solid #E0E0E0;
        overflow: hidden;
        max-width: 920px;
        margin: 0.5rem auto 1.5rem;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        padding: 0 !important;
    }
    /* Stretch column wrappers to full height without cascading into Streamlit internals */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > [data-testid="stMarkdownContainer"] {
        height: 100%;
    }
    /* Reset: prevent height cascade into form content */
    [data-testid="stHorizontalBlock"] [data-testid="stColumn"] .form-panel * {
        height: auto !important;
    }
    /* Tabs left padding to align with form fields */
    .form-panel [data-testid="stTabs"] {
        padding-left: 0.8rem;
    }
    /* Remove gap between elements inside card */
    [data-testid="stHorizontalBlock"] .element-container { margin: 0 !important; }
    [data-testid="stHorizontalBlock"] [data-testid="stVerticalBlock"] > div {
        margin: 0 !important;
    }
    .form-panel {
        background: #FFFFFF;
        padding: 1.5rem 2.2rem 2rem 3rem;
        border-radius: 16px 0 0 16px;
        height: 100%;
        box-sizing: border-box;
    }
    .illust-panel {
        background: #2E7D32;
        border-radius: 0 16px 16px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        overflow: hidden;
    }
    .illust-panel img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 0 16px 16px 0;
    }
    /* Hide sidebar completely on auth pages */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] ~ div {
        margin-left: 0 !important;
    }
    button[data-testid="stSidebarCollapsedControl"],
    button[title="Expand sidebar"],
    button[title="Collapse sidebar"],
    header[data-testid="stHeader"] button[kind="icon"] {
        display: none !important;
        visibility: hidden !important;
    }
</style>
"""
st.markdown(_CARD_CSS, unsafe_allow_html=True)

# ── Auth card wrapper ─────────────────────────────────
with st.container():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    col_form, col_art = st.columns([1, 1], gap="small")

    # ═══════════════════════════════════════════════════
    # LEFT PANEL — WHITE FORM
    # ═══════════════════════════════════════════════════
    with col_form:
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)

        # ── Branding — single-line logo icon + app name ──
        st.markdown(
            """<div style="display:flex; align-items:center; justify-content:center; gap:1rem; margin-bottom:1.2rem; white-space:nowrap;">
                <img src="data:image/png;base64,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"
                     alt="" style="height:90px; width:auto;" />
                <span style="font-size:2.6rem; font-weight:700; color:#1B2A4A; white-space:nowrap;">
                    EduPilot <span style="color:#2E7D32;">AI</span>
                </span>
            </div>""",
            unsafe_allow_html=True,
        )

        # ── Heading ──
        st.markdown(
            """<div style="padding: 0 0 0.8rem 0.8rem;">
                <h1 style="color: #1B2A4A; margin: 0 0 0.2rem 0; font-size: 1.7rem; font-weight: 700;">
                    Create Your Account
                </h1>
                <p style="color: #666666; font-size: 0.95rem; margin: 0;">
                    Join EduPilot AI and unlock opportunities.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )

        # ── Registration form ──
        with st.form("registration_form"):
            full_name = st.text_input("Full Name", key="reg_name",
                                       placeholder="Enter your full name")
            email = st.text_input("Email Address", key="reg_email",
                                   placeholder="student@example.com")
            password = st.text_input("Password", type="password", key="reg_pw",
                                      placeholder="Create a strong password",
                                      help="Minimum 8 characters")
            confirm_pw = st.text_input("Confirm Password", type="password", key="reg_cpw",
                                        placeholder="Confirm your password")

            agree_terms = st.checkbox(
                "I agree to the Terms & Conditions and Privacy Policy",
                key="reg_agree_terms",
            )

            st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account", type="primary",
                                               use_container_width=True)

        if submitted:
            if not agree_terms:
                st.warning("Please agree to the Terms & Conditions to continue.")
            elif password != confirm_pw:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating your account…"):
                    result = register(full_name, email, password)

                if result["ok"]:
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"] = result["user_id"]
                    st.session_state["user_name"] = full_name.strip()
                    st.session_state["role"] = "STUDENT"
                    st.session_state["completed_profile_sections"] = set()
                    st.success(result["message"])
                    st.switch_page("pages/Profile_Setup.py")
                else:
                    st.error(result["message"])

        # ── Login link ──
        st.markdown(
            """<div style="text-align:center; margin-top: 1rem; color: #666666; font-size: 0.9rem;">
                Already have an account?
                <a href="Login" target="_self"
                   style="color: #2E7D32; font-weight: 600; text-decoration: none;">
                    Login
                </a>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown('</div>', unsafe_allow_html=True)  # close form-panel

    # ═══════════════════════════════════════════════════
    # RIGHT PANEL — GREEN ILLUSTRATION
    # ═══════════════════════════════════════════════════
    with col_art:
        if os.path.exists(_ILLUST_IMG):
            with open(_ILLUST_IMG, "rb") as _f:
                _illust_b64 = base64.b64encode(_f.read()).decode()
            st.markdown(
                f"""<div class="illust-panel">
                    <img src="data:image/png;base64,{_illust_b64}" />
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="illust-panel"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close auth-card

# ── Footer ─────────────────────────────────────────────
st.markdown(
    """<div style="text-align:center; color: #9E9E9E; font-size: 0.75rem; margin-top: 1.5rem;">
        EduPilot AI v1.4 &mdash; Your AI Companion for Academic &amp; Career Success
    </div>""",
    unsafe_allow_html=True,
)
