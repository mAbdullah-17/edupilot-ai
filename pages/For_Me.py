"""Screen — For Me (Day 3).

Displays opportunities matched to the student's profile,
sorted by match percentage, with eligibility status badges.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar
from modules.eligibility import get_for_me_opportunities
from modules import opportunities as opp_svc

st.set_page_config(page_title="For Me — EduPilot AI", layout="wide")
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
    .badge-match { background: #E8F5E9; color: #2E7D32; }
    .badge-match-high { background: #C8E6C9; color: #1B5E20; }
    .badge-match-med { background: #FFF8E1; color: #F57F17; }
    .badge-match-low { background: #FFF3E0; color: #E65100; }
    .badge-eligible { background: #C8E6C9; color: #1B5E20; }
    .badge-undecided { background: #FFF8E1; color: #F57F17; }
    .opp-location { color: #757575; font-size: 0.78rem; }
    .opp-deadline { color: #757575; font-size: 0.78rem; }
    .opp-deadline-urgent { color: #D32F2F; font-weight: 600; font-size: 0.78rem; }
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
    .match-ring {
        width: 48px; height: 48px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
        border: 3px solid; margin-right: 0.3rem;
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
        <h1 class="page-heading">For Me</h1>
        <p class="page-subheading">
            Opportunities matched to your profile — sorted by best fit
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Retrieve matched opportunities ────────────────────
with st.spinner("Analysing your profile against all opportunities..."):
    results = get_for_me_opportunities(user_id)

# ── Results count ─────────────────────────────────────
total = len(results)
st.markdown(
    f"""<p class="results-count">{total} opportunit{'y' if total == 1 else 'ies'} matched to your profile</p>""",
    unsafe_allow_html=True,
)

# ── Empty state ───────────────────────────────────────
if not results:
    st.markdown(
        """<div class="empty-state">
            <p>No opportunities matched your profile yet. Complete your profile to get personalised recommendations.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("Complete Your Profile →", key="btn_profile_cta", type="primary"):
        st.switch_page("pages/Profile_Setup.py")
    st.stop()

# ── Render cards ──────────────────────────────────────
for opp in results:
    opp_id = opp["id"]
    title = opp.get("title", "")
    org = opp.get("organization", "")
    category = opp.get("category", "")
    opp_type = opp.get("opportunity_type", "")
    location_label = opp_svc.get_location_label(opp)
    deadline_str = opp_svc.format_deadline(opp.get("deadline"))
    days_left = opp_svc.days_until_deadline(opp.get("deadline"))
    match_pct = opp.get("match_pct", 0)
    elig_status = opp.get("eligibility_status", "")

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

    # Match badge class
    if match_pct >= 75:
        match_cls = "badge-match-high"
    elif match_pct >= 40:
        match_cls = "badge-match-med"
    else:
        match_cls = "badge-match-low"

    # Eligibility badge
    if elig_status == "Eligible":
        elig_cls = "badge-eligible"
    else:
        elig_cls = "badge-undecided"

    # Match ring colour
    if match_pct >= 75:
        ring_color = "#2E7D32"
        ring_bg = "#E8F5E9"
    elif match_pct >= 40:
        ring_color = "#F57F17"
        ring_bg = "#FFF8E1"
    else:
        ring_color = "#E65100"
        ring_bg = "#FFF3E0"

    card_col, action_col = st.columns([6, 1])

    with card_col:
        st.markdown(
            f"""<div class="opp-card">
                <div class="opp-card-inner">
                    <div class="match-ring" style="border-color:{ring_color}; background:{ring_bg}; color:{ring_color};">
                        {match_pct}%
                    </div>
                    <div class="opp-logo" style="background:{logo_bg};">{_ORG_ICON_SVG}</div>
                    <div class="opp-body">
                        <div class="opp-title">{title}</div>
                        <div class="opp-org">{org}</div>
                        <div class="opp-meta-row">
                            <span class="opp-badge badge-category">{category}</span>
                            <span class="opp-badge badge-type">{opp_type}</span>
                            <span class="opp-badge {elig_cls}">{elig_status}</span>
                        </div>
                        <div class="opp-meta-row">
                            <span class="opp-location">{location_label}</span>
                            <span style="color:#BDBDBD;">|</span>
                            {deadline_html}
                        </div>
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button("View Details", key=f"fm_detail_{opp_id}",
                     use_container_width=True, type="primary"):
            st.session_state["_view_opp_id"] = opp_id
            st.switch_page("pages/Opportunity_Details.py")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
