"""Screen 3 — Dashboard  (Day 1 shell matching the approved UI/UX reference).

Reference: 11.png panel 3 — shows welcome header, profile completion card,
opportunity stat cards (All / For Me / Relevant), featured opportunity,
upcoming deadlines, and quick actions row.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar, render_admin_sidebar
from components.icons import svg as _icon
from modules.profile import get_profile, get_profile_view
from modules import opportunities as opp_svc
from modules.eligibility import get_for_me_opportunities, get_relevant_opportunities

st.set_page_config(page_title="Dashboard — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()

# ── Sidebar ───────────────────────────────────────────
role = st.session_state.get("role")
if role == "ADMIN":
    render_admin_sidebar()
else:
    render_student_sidebar()

# ── Welcome header ──
user_name = st.session_state.get("user_name", "Student")

st.markdown(
    f"""<div style="padding: 0.5rem 0 0.8rem 0;">
        <h1 style="color: #1B2A4A; margin: 0 0 0.2rem 0; font-size: 1.7rem;">
            Welcome back, {user_name} {_icon("bookmark", 22, "#2E7D32")}
        </h1>
        <p style="color: #616161; font-size: 0.95rem; margin: 0;">
            Your AI Companion for Academic &amp; Career Success
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Admin: redirect to dedicated Admin Dashboard ─────
if role == "ADMIN":
    st.switch_page("pages/Admin_Dashboard.py")

# ── Student Dashboard ─────────────────────────────────
user_id = st.session_state["user_id"]

# ── Profile View mode (from user menu) ───────────────
if st.session_state.pop("_profile_view", False):
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
            padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 1rem;
        ">
            <h3 style="color: #1B2A4A;">{_icon("clipboard", 20, "#1B2A4A")} Your Profile</h3>
        </div>""",
        unsafe_allow_html=True,
    )
    view = get_profile_view(user_id)

    for section_name, section_data in view.items():
        if section_name == "completion":
            continue
        if isinstance(section_data, dict):
            with st.expander(section_name.title(), expanded=True):
                for label, value in section_data.items():
                    st.markdown(f"**{label}:** {value}")

    completion = view.get("completion", 0)
    st.markdown("---")
    st.markdown(f"**Profile Completion:** {completion}%")
    st.progress(completion / 100)

    if st.button("← Back to Dashboard", key="btn_back_dash"):
        st.rerun()
    st.stop()

# ── Normal dashboard ──────────────────────────────────
profile = get_profile(user_id)
completion = profile["profile_completion"] if profile else 0

# ── Profile Completion Card + Stat Cards Row ───────────
col_pc, col_opp, col_for_me, col_relevant = st.columns([1.3, 1, 1, 1])

with col_pc:
    progress_color = "#2E7D32" if completion >= 75 else ("#FFA000" if completion >= 40 else "#D32F2F")
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
            padding: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            height: 120px;
        ">
            <div style="color: #616161; font-size: 0.8rem; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">
                {_icon("clipboard", 16, "#616161")} Profile Completion
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {progress_color};">
                {completion}%
            </div>
            <div style="background: #E0E0E0; border-radius: 4px; height: 8px; margin-top: 0.4rem;">
                <div style="background: {progress_color}; height: 8px; border-radius: 4px;
                            width: {completion}%;"></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with col_opp:
    opp_count = opp_svc.count_opportunities()
    st.markdown(
        f"""<div style="
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9); border: 1px solid #A5D6A7;
            border-radius: 12px; padding: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            height: 120px;
        ">
            <div style="color: #2E7D32; font-size: 0.8rem; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">
                All Opportunities
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1B2A4A;">{opp_count}</div>
            <div style="color: #616161; font-size: 0.75rem; margin-top: 0.3rem;">
                Active listings
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with col_for_me:
    for_me_list = get_for_me_opportunities(user_id)
    for_me_count = len(for_me_list)
    st.markdown(
        f"""<div style="
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border: 1px solid #90CAF9;
            border-radius: 12px; padding: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            height: 120px;
        ">
            <div style="color: #1565C0; font-size: 0.8rem; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">
                {_icon("bookmark", 16, "#1565C0")} For Me
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1B2A4A;">{for_me_count}</div>
            <div style="color: #616161; font-size: 0.75rem; margin-top: 0.3rem;">
                Matched to profile
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

with col_relevant:
    relevant_list = get_relevant_opportunities(user_id)
    relevant_count = len(relevant_list)
    st.markdown(
        f"""<div style="
            background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFCC80;
            border-radius: 12px; padding: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            height: 120px;
        ">
            <div style="color: #E65100; font-size: 0.8rem; font-weight: 600;
                        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem;">
                {_icon("star", 16, "#E65100")} Relevant
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1B2A4A;">{relevant_count}</div>
            <div style="color: #616161; font-size: 0.75rem; margin-top: 0.3rem;">
                Profile connection
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

# CTA if profile incomplete
if completion < 100:
    st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
    if st.button("Complete Your Profile →", key="btn_complete_profile", type="primary"):
        st.switch_page("pages/Profile_Setup.py")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Featured Opportunity + Upcoming Deadlines (live data) ──
col_featured, col_deadlines = st.columns([1.5, 1])

with col_featured:
    # Use best For Me match as featured, or first available opportunity
    if for_me_list:
        featured = for_me_list[0]
        feat_match = featured.get("match_pct", 0)
        feat_match_html = f'Match: {feat_match}%'
    else:
        all_opps_dash = opp_svc.get_all_opportunities(user_id=user_id)
        featured = all_opps_dash[0] if all_opps_dash else None
        feat_match_html = 'Match: \u2014'

    if featured:
        feat_title = featured.get("title", "")
        feat_org = featured.get("organization", "")
        feat_type = featured.get("opportunity_type", "")
        feat_deadline = opp_svc.format_deadline(featured.get("deadline"))
        feat_days = opp_svc.days_until_deadline(featured.get("deadline"))
        if feat_days is not None and feat_days >= 0:
            feat_deadline_extra = f" &nbsp;|&nbsp; {feat_days} days left"
        else:
            feat_deadline_extra = ""
        feat_id = featured["id"]

        _featured_html = f"""<div style="background:#FFFFFF;border:1px solid #E0E0E0;border-radius:12px;padding:1.5rem;box-shadow:0 2px 6px rgba(0,0,0,0.06);">
<h4 style="color:#1B2A4A;margin:0 0 0.8rem 0;">{_icon("trophy",20,"#1B2A4A")} Featured Opportunity</h4>
<div style="background:#F5F7FA;border-radius:10px;padding:1.2rem;border:1px solid #E0E0E0;">
<div style="font-weight:600;color:#1B2A4A;font-size:1.05rem;">{feat_title}</div>
<div style="color:#616161;font-size:0.85rem;margin-top:0.3rem;">{feat_org} &nbsp;|&nbsp; {feat_type} &nbsp;|&nbsp; Deadline: {feat_deadline}{feat_deadline_extra}</div>
<div style="margin-top:0.6rem;"><span style="background:#E8F5E9;color:#2E7D32;padding:0.2rem 0.6rem;border-radius:12px;font-size:0.8rem;font-weight:600;">{feat_match_html}</span></div>
</div></div>"""
        if hasattr(st, "html"):
            st.html(_featured_html)
        else:
            st.markdown(_featured_html, unsafe_allow_html=True)
        if st.button("View Details \u2192", key="btn_featured_details"):
            st.session_state["_view_opp_id"] = feat_id
            st.switch_page("pages/Opportunity_Details.py")
    else:
        st.markdown(
            f"""<div style="
                background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
                padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            ">
                <h4 style="color: #1B2A4A; margin: 0 0 0.8rem 0;">{_icon("trophy", 20, "#1B2A4A")} Featured Opportunity</h4>
                <div style="color: #9E9E9E; font-size: 0.9rem;">No opportunities available yet.</div>
            </div>""",
            unsafe_allow_html=True,
        )

with col_deadlines:
    # Get upcoming deadlines — active opps sorted by deadline ASC, filter future only
    from datetime import date as _today_cls
    _today = _today_cls.today()
    _all_deadline_opps = opp_svc.get_all_opportunities(user_id=user_id)
    _upcoming = [
        o for o in _all_deadline_opps
        if opp_svc.days_until_deadline(o.get("deadline")) is not None
        and opp_svc.days_until_deadline(o.get("deadline")) >= 0
    ][:3]  # top 3

    _deadline_items_html = ""
    for _dl_opp in _upcoming:
        _dl_title = _dl_opp.get("title", "")
        _dl_days = opp_svc.days_until_deadline(_dl_opp.get("deadline"))
        _dl_days_text = f"{_dl_days} day{'s' if _dl_days != 1 else ''} left"
        _dl_color = "#D32F2F" if _dl_days <= 14 else "#616161"
        _deadline_items_html += (
            f'<div style="padding: 0.6rem 0; border-bottom: 1px solid #F0F0F0;">'
            f'<div style="color: #1B2A4A; font-weight: 500; font-size: 0.9rem;">'
            f'{_dl_title}</div>'
            f'<div style="color: {_dl_color}; font-size: 0.8rem;">{_dl_days_text}</div></div>'
        )

    if not _deadline_items_html:
        _deadline_items_html = (
            '<div style="color: #9E9E9E; font-size: 0.9rem; padding: 1rem 0;">'
            'No upcoming deadlines.</div>'
        )

    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
            padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        ">
            <h4 style="color: #1B2A4A; margin: 0 0 0.8rem 0;">{_icon("calendar", 20, "#1B2A4A")} Upcoming Deadlines</h4>
            {_deadline_items_html}
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

# ── Quick Actions (reference: 4 action cards in a row) ──
st.markdown(
    f"""<h3 style="color: #1B2A4A; margin: 0 0 0.8rem 0; font-size: 1.1rem;">
        {_icon("bolt", 18, "#1B2A4A")} Quick Actions
    </h3>""",
    unsafe_allow_html=True,
)

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
            padding: 1.2rem; text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.4rem;">{_icon("search", 36, "#2E7D32")}</div>
            <div style="font-weight: 600; color: #1B2A4A; font-size: 0.9rem;">
                Find Opportunities
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Browse", use_container_width=True, key="qa_find"):
        st.switch_page("pages/All_Opportunities.py")

with col_b:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
            padding: 1.2rem; text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.4rem;">{_icon("book", 36, "#2E7D32")}</div>
            <div style="font-weight: 600; color: #1B2A4A; font-size: 0.9rem;">
                Study Assistant
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Study", use_container_width=True, key="qa_study"):
        st.switch_page("pages/Study_Assistant.py")

with col_c:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
            padding: 1.2rem; text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.4rem;">{_icon("description", 36, "#2E7D32")}</div>
            <div style="font-weight: 600; color: #1B2A4A; font-size: 0.9rem;">
                Analyze Resume
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Analyze", use_container_width=True, key="qa_resume"):
        st.switch_page("pages/Resume_Analyzer.py")

with col_d:
    st.markdown(
        f"""<div style="
            background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
            padding: 1.2rem; text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.4rem;">{_icon("mic", 36, "#2E7D32")}</div>
            <div style="font-weight: 600; color: #1B2A4A; font-size: 0.9rem;">
                Practice Interview
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Practice", use_container_width=True, key="qa_interview"):
        st.switch_page("pages/Interview_Coach.py")

st.caption("Explore all AI-powered tools from the sidebar.")
