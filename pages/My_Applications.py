"""Screen — My Applications (Day 3, Round 4).

Tab-filtered application tracking: All / Applied / In Review / Shortlisted / Rejected
with status counts and opportunity detail cards.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar
from modules.applications import get_my_applications, get_application_counts
from modules import opportunities as opp_svc

st.set_page_config(page_title="My Applications — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()
render_student_sidebar()

# ── Page-specific CSS ─────────────────────────────────
_PAGE_CSS = """
<style>
    .page-heading {
        color: #2E7D32 !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 0.15rem 0;
        letter-spacing: 0.3px;
    }
    .page-subheading {
        color: #616161;
        font-size: 0.88rem;
        margin: 0 0 0.8rem 0;
    }
    .opp-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
        height: 100%;
        box-sizing: border-box;
    }
    .opp-card:hover {
        box-shadow: 0 4px 14px rgba(0,0,0,0.09);
        border-color: #BDBDBD;
    }
    .opp-card-inner {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }
    .opp-logo {
        width: 46px;
        height: 46px;
        min-width: 46px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .opp-body { flex: 1; min-width: 0; }
    .opp-title {
        color: #1B2A4A;
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 0.15rem 0;
        line-height: 1.3;
    }
    .opp-org {
        color: #616161;
        font-size: 0.82rem;
        margin: 0 0 0.45rem 0;
    }
    .opp-meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .opp-badge {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-category { background: #E8F5E9; color: #2E7D32; }
    .badge-type { background: #E3F2FD; color: #1565C0; }
    .badge-applied { background: #E0F2F1; color: #00695C; }
    .badge-in_review { background: #FFF8E1; color: #E65100; }
    .badge-shortlisted { background: #C8E6C9; color: #1B5E20; }
    .badge-rejected { background: #FFCDD2; color: #B71C1C; }
    .opp-location { color: #757575; font-size: 0.78rem; }
    .opp-deadline { color: #757575; font-size: 0.78rem; }
    .opp-deadline-urgent { color: #D32F2F; font-weight: 600; font-size: 0.78rem; }
    .opp-date { color: #9E9E9E; font-size: 0.75rem; }
    .results-count { color: #757575; font-size: 0.82rem; margin: 0.3rem 0 0.8rem 0; }
    .empty-state {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .empty-state p { color: #757575; font-size: 0.95rem; margin: 0; }
    .stat-pills {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    .stat-pill {
        padding: 0.45rem 1rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid #E0E0E0;
        background: #FFFFFF;
        color: #1B2A4A;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .stat-pill-active {
        border-color: #2E7D32;
        background: #E8F5E9;
        color: #2E7D32;
    }
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ── Logo colour map + icon ────────────────────────────
_LOGO_COLOURS = {
    "Scholarship": "#1565C0",
    "Internship": "#00897B",
    "Job": "#E65100",
    "Fellowship": "#6A1B9A",
    "Competition": "#C62828",
    "Programme": "#0097A7",
}

_ORG_ICON_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" width="24" height="24" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M12 7V3H2v18h20V7H12z" fill="rgba(255,255,255,0.85)"/>'
    '<path d="M6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2z'
    'm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2z'
    'm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2z'
    'm0 4h-2v2h2v-2zm-4 0v2h2v-2h-2z" fill="rgba(255,255,255,0.5)"/>'
    '</svg>'
)

# ── Heading ───────────────────────────────────────────
user_id = st.session_state.get("user_id")

st.markdown(
    """<div style="padding: 0.2rem 0 0.6rem 0;">
        <h1 class="page-heading">My Applications</h1>
        <p class="page-subheading">
            Track your submitted applications and their status
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Retrieve data ─────────────────────────────────────
applications = get_my_applications(user_id)
counts = get_application_counts(user_id)

# ── Stat pills / tab filters ──────────────────────────
_tab_labels = [
    ("All", "all", "#1B2A4A"),
    ("Applied", "applied", "#009688"),
    ("In Review", "in_review", "#FFA000"),
    ("Shortlisted", "shortlisted", "#2E7D32"),
    ("Rejected", "rejected", "#D32F2F"),
]

# Build pill HTML
pill_html = '<div class="stat-pills">'
for label, key, color in _tab_labels:
    count = counts.get(key, 0)
    pill_html += (
        f'<div class="stat-pill" style="border-color:{color}30;">'
        f'<span style="color:{color};">{label}</span>'
        f' <span style="background:{color}18; color:{color}; '
        f'padding:0.1rem 0.4rem; border-radius:10px; font-size:0.72rem; '
        f'margin-left:0.2rem;">{count}</span></div>'
    )
pill_html += '</div>'
st.markdown(pill_html, unsafe_allow_html=True)

# Streamlit tabs for actual filtering
tab_labels_display = [f"{label} ({counts.get(key, 0)})" for label, key, _ in _tab_labels]
tab_keys = [key for _, key, _ in _tab_labels]

tabs = st.tabs(tab_labels_display)

# ── Render helper ─────────────────────────────────────
_STATUS_BADGE_MAP = {
    "applied": ("badge-applied", "Applied"),
    "in_review": ("badge-in_review", "In Review"),
    "shortlisted": ("badge-shortlisted", "Shortlisted"),
    "rejected": ("badge-rejected", "Rejected"),
}


def _render_application_cards(apps: list[dict], tab_prefix: str = ""):
    """Render opportunity cards for a list of applications."""
    if not apps:
        st.markdown(
            """<div class="empty-state">
                <p>No applications in this category.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    for app in apps:
        opp_id = app.get("id")
        title = app.get("title", "")
        org = app.get("organization", "")
        category = app.get("category", "")
        opp_type = app.get("opportunity_type", "")
        location_label = opp_svc.get_location_label(app)
        deadline_str = opp_svc.format_deadline(app.get("deadline"))
        days_left = opp_svc.days_until_deadline(app.get("deadline"))
        status = (app.get("status") or "applied").lower()
        applied_at = app.get("applied_at")

        logo_bg = _LOGO_COLOURS.get(category, "#2E7D32")

        # Deadline styling
        if days_left is not None:
            if days_left < 0:
                deadline_html = '<span class="opp-deadline" style="color:#9E9E9E;">Closed</span>'
            elif days_left <= 14:
                deadline_html = f'<span class="opp-deadline-urgent">{days_left} days left</span>'
            else:
                deadline_html = f'<span class="opp-deadline">{deadline_str}</span>'
        else:
            deadline_html = f'<span class="opp-deadline">{deadline_str}</span>'

        # Status badge
        badge_cls, badge_label = _STATUS_BADGE_MAP.get(
            status, ("badge-applied", status.replace("_", " ").title())
        )

        # Applied date
        if applied_at and hasattr(applied_at, "strftime"):
            applied_str = applied_at.strftime("%d %b %Y")
        else:
            applied_str = str(applied_at) if applied_at else "—"

        card_col, action_col = st.columns([6, 1])

        with card_col:
            st.markdown(
                f"""<div class="opp-card">
                    <div class="opp-card-inner">
                        <div class="opp-logo" style="background:{logo_bg};">{_ORG_ICON_SVG}</div>
                        <div class="opp-body">
                            <div class="opp-title">{title}</div>
                            <div class="opp-org">{org}</div>
                            <div class="opp-meta-row">
                                <span class="opp-badge badge-category">{category}</span>
                                <span class="opp-badge badge-type">{opp_type}</span>
                                <span class="opp-badge {badge_cls}">{badge_label}</span>
                            </div>
                            <div class="opp-meta-row">
                                <span class="opp-location">{location_label}</span>
                                <span style="color:#BDBDBD;">|</span>
                                {deadline_html}
                                <span style="color:#BDBDBD;">|</span>
                                <span class="opp-date">Applied: {applied_str}</span>
                            </div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

        with action_col:
            if st.button("View Details", key=f"app_detail_{tab_prefix}_{opp_id}_{status}",
                         use_container_width=True, type="primary"):
                st.session_state["_view_opp_id"] = opp_id
                st.switch_page("pages/Opportunity_Details.py")

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)


# ── Render tabs ───────────────────────────────────────
for i, (tab, filter_key) in enumerate(zip(tabs, tab_keys)):
    with tab:
        if filter_key == "all":
            filtered = applications
        else:
            filtered = [a for a in applications if (a.get("status") or "").lower() == filter_key]

        total = len(filtered)
        st.markdown(
            f"""<p class="results-count">{total} application{'s' if total != 1 else ''}</p>""",
            unsafe_allow_html=True,
        )
        _render_application_cards(filtered, tab_prefix=filter_key)

# ── Empty state — no applications at all ──────────────
if not applications:
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("Browse Opportunities →", key="btn_browse_opps", type="primary"):
        st.switch_page("pages/All_Opportunities.py")
