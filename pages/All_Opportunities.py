"""Screen — All Opportunities (Day 2).

Displays searchable, filterable list of opportunity cards with
location-priority ordering, save/unsave, and view-details actions.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar, render_admin_sidebar
from modules import opportunities as opp_svc

st.set_page_config(page_title="All Opportunities — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()

# ── Sidebar ───────────────────────────────────────────
role = st.session_state.get("role")
if role == "ADMIN":
    render_admin_sidebar()
else:
    render_student_sidebar()

# ── Page-specific CSS ─────────────────────────────────
_PAGE_CSS = """
<style>
    /* ── Page heading ── */
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

    /* ── Search bar ── */
    [data-testid="stTextInput"] > div > div {
        border-radius: 8px !important;
    }

    /* ── Filter selectboxes ── */
    [data-testid="stSelectbox"] label {
        font-size: 0.8rem !important;
        color: #616161 !important;
    }

    /* ── Opportunity card (outer wrapper) ── */
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

    /* ── Card inner layout ── */
    .opp-card-inner {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }

    /* ── Logo square (left side of card) ── */
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

    /* ── Card body ── */
    .opp-body {
        flex: 1;
        min-width: 0;
    }
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

    /* ── Badges ── */
    .opp-badge {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-category {
        background: #E8F5E9;
        color: #2E7D32;
    }
    .badge-type {
        background: #E3F2FD;
        color: #1565C0;
    }

    /* ── Meta text ── */
    .opp-location {
        color: #757575;
        font-size: 0.78rem;
    }
    .opp-deadline {
        color: #757575;
        font-size: 0.78rem;
    }
    .opp-deadline-urgent {
        color: #D32F2F;
        font-weight: 600;
        font-size: 0.78rem;
    }

    /* ── Action column buttons ── */
    .opp-action-btn {
        border: 1.5px solid #2E7D32 !important;
        color: #2E7D32 !important;
        background: transparent !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    .opp-action-btn:hover {
        background: #E8F5E9 !important;
    }

    /* ── Results count ── */
    .results-count {
        color: #757575;
        font-size: 0.82rem;
        margin: 0.3rem 0 0.8rem 0;
    }

    /* ── Empty state ── */
    .empty-state {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .empty-state p {
        color: #757575;
        font-size: 0.95rem;
        margin: 0;
    }
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ── Logo colour map by category ───────────────────────
_LOGO_COLOURS = {
    "Scholarship": "#1565C0",
    "Internship": "#00897B",
    "Job": "#E65100",
    "Fellowship": "#6A1B9A",
    "Competition": "#C62828",
    "Programme": "#0097A7",
}

# ── Generic organisation/building fallback icon (white SVG) ──
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
        <h1 class="page-heading">All Opportunities</h1>
        <p class="page-subheading">
            Discover scholarships, internships, jobs, and programmes
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Live opportunity discovery ─────────────────────────
# Existing MySQL opportunities are always shown immediately. Groq GPT-OSS
# 120B browser search is only called when the user explicitly refreshes,
# preventing slow Streamlit reruns and unnecessary API usage. Capped at 8
# results per refresh — see modules.opportunity_discovery.MAX_RESULTS.
refresh_col, info_col = st.columns([1.4, 4])
with refresh_col:
    if st.button("Refresh Live Opportunities", key="refresh_live_opps", type="primary", use_container_width=True):
        with st.spinner("Finding current opportunities on the web..."):
            try:
                sync_result = opp_svc.refresh_live_opportunities(user_id=user_id, limit=8)
                st.success(
                    f"Found {sync_result['found']} verified results; "
                    f"added {sync_result['inserted']} new opportunities."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Live opportunity refresh failed: {exc}")
with info_col:
    st.caption(
        "Select Location And Click Refresh button to get upto 5 latest Oppourtunities more."
    )

# ── Search ────────────────────────────────────────────
search_query = st.text_input(
    "Search opportunities",
    placeholder="Search by title, organisation, category, or location...",
    key="opp_search",
    label_visibility="collapsed",
)

# ── Filters row ───────────────────────────────────────
filter_opts = opp_svc.get_filter_options()

col_f1, col_f2, col_f3 = st.columns([1, 1, 1])

with col_f1:
    cat_options = ["All Categories"] + filter_opts["categories"]
    selected_category = st.selectbox("Category", cat_options, key="filter_cat")

with col_f2:
    type_options = ["All Types"] + filter_opts["types"]
    selected_type = st.selectbox("Type", type_options, key="filter_type")

with col_f3:
    location_input = st.text_input("Location", placeholder="e.g. Lahore, Punjab",
                                   key="filter_loc", label_visibility="collapsed")

# ── Retrieve opportunities ────────────────────────────
has_filters = (
    search_query.strip()
    or selected_category != "All Categories"
    or selected_type != "All Types"
    or location_input.strip()
)

if search_query.strip():
    results = opp_svc.search(search_query.strip())
    # Post-filter search results by category / type / location
    if selected_category != "All Categories":
        results = [r for r in results if r.get("category") == selected_category]
    if selected_type != "All Types":
        results = [r for r in results if r.get("opportunity_type") == selected_type]
    if location_input.strip():
        loc = location_input.strip().lower()
        results = [
            r for r in results
            if loc in (r.get("city") or "").lower()
            or loc in (r.get("province") or "").lower()
            or loc in (r.get("country") or "").lower()
            or loc in (r.get("location") or "").lower()
        ]
elif selected_category != "All Categories" or selected_type != "All Types" or location_input.strip():
    results = opp_svc.filter_opportunities(
        category=selected_category if selected_category != "All Categories" else None,
        opportunity_type=selected_type if selected_type != "All Types" else None,
        location=location_input.strip() or None,
    )
else:
    results = opp_svc.get_all_opportunities(user_id=user_id)

# ── Results count ─────────────────────────────────────
total = len(results)
st.markdown(
    f"""<p class="results-count">{total} opportunit{'y' if total == 1 else 'ies'} found</p>""",
    unsafe_allow_html=True,
)

# ── Render cards ──────────────────────────────────────
if not results:
    st.markdown(
        """<div class="empty-state">
            <p>No opportunities match your search. Try adjusting your filters.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.stop()

for opp in results:
    opp_id = opp["id"]
    title = opp.get("title", "")
    org = opp.get("organization", "")
    desc = opp.get("description", "")
    category = opp.get("category", "")
    opp_type = opp.get("opportunity_type", "")
    location_label = opp_svc.get_location_label(opp)
    deadline_str = opp_svc.format_deadline(opp.get("deadline"))
    days_left = opp_svc.days_until_deadline(opp.get("deadline"))
    is_saved = opp_svc.is_saved(user_id, opp_id)

    # Logo square: category-coloured background with generic building icon
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

    # Two-column layout: card info (left) + action buttons (right)
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
        btn_label = "Unsave" if is_saved else "Save"
        btn_key = f"save_{opp_id}"
        if st.button(btn_label, key=btn_key, use_container_width=True):
            if is_saved:
                opp_svc.unsave_opportunity(user_id, opp_id)
            else:
                opp_svc.save_opportunity(user_id, opp_id)
            st.rerun()

        if st.button("View Details", key=f"detail_{opp_id}",
                     use_container_width=True, type="primary"):
            st.session_state["_view_opp_id"] = opp_id
            st.switch_page("pages/Opportunity_Details.py")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
