"""Screen — Eligibility Analysis (Day 3, Round 3).

Select an opportunity and check eligibility with a per-requirement
breakdown: Eligible / Not Eligible / Cannot Determine.
Includes Apply Now button or Already Applied indicator.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar
from modules.eligibility import analyze_eligibility
from modules import opportunities as opp_svc
from modules.applications import (
    apply_to_opportunity,
    get_application_status,
)

st.set_page_config(page_title="Eligibility Analysis — EduPilot AI", layout="wide")
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
    .elig-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .elig-overall {
        text-align: center;
        padding: 1.2rem 1rem;
    }
    .elig-ring {
        width: 88px; height: 88px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.5rem;
        border: 5px solid; margin-bottom: 0.5rem;
    }
    .elig-label {
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }
    .req-row {
        background: #F5F7FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.5rem;
    }
    .req-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }
    .req-type {
        color: #1B2A4A;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .req-status {
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .status-eligible { background: #C8E6C9; color: #1B5E20; }
    .status-not-eligible { background: #FFCDD2; color: #B71C1C; }
    .status-cannot { background: #FFF8E1; color: #F57F17; }
    .req-detail {
        color: #616161;
        font-size: 0.82rem;
        line-height: 1.4;
        margin-top: 0.15rem;
    }
    .req-values {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.35rem;
        font-size: 0.82rem;
    }
    .req-val-label {
        color: #9E9E9E;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .req-val-text {
        color: #1B2A4A;
        font-weight: 500;
    }
    .legend-row {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 0.6rem 0 1rem 0;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.78rem;
        color: #616161;
    }
    .legend-dot {
        width: 10px; height: 10px; border-radius: 50%;
        display: inline-block;
    }
    .apply-banner {
        background: #E8F5E9;
        border: 1px solid #A5D6A7;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.8rem;
    }
    .applied-banner {
        background: #E0F2F1;
        border: 1px solid #80CBC4;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.8rem;
    }
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ── Heading ───────────────────────────────────────────
user_id = st.session_state.get("user_id")

st.markdown(
    """<div style="padding: 0.2rem 0 0.6rem 0;">
        <h1 class="page-heading">Eligibility Analysis</h1>
        <p class="page-subheading">
            Select an opportunity to check how well your profile matches its requirements
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Opportunity selector ──────────────────────────────
all_opps = opp_svc.get_all_opportunities(user_id=user_id)

if not all_opps:
    st.info("No opportunities available.")
    st.stop()

opp_labels = [f"{o['title']}  ({o.get('organization', '')})" for o in all_opps]
opp_map = dict(zip(opp_labels, [o["id"] for o in all_opps]))

selected_label = st.selectbox(
    "Choose an opportunity",
    opp_labels,
    key="elig_select",
    label_visibility="collapsed",
    placeholder="Select an opportunity to analyse...",
)

selected_opp_id = opp_map.get(selected_label)

# ── Analyse button (live — no caching) ────────────────
if st.button("Check Eligibility", key="btn_check_elig", type="primary",
             use_container_width=True):
    st.session_state["_elig_run_id"] = selected_opp_id

# ── Show results ──────────────────────────────────────
opp_id = st.session_state.get("_elig_run_id", selected_opp_id)
if not opp_id:
    st.stop()

opp = opp_svc.get_opportunity(opp_id)
if not opp:
    st.error("Opportunity not found.")
    st.stop()

# Live recomputation — fresh call every time
result = analyze_eligibility(user_id, opp_id)
overall = result["overall"]
match_pct = result["match_pct"]
rows = result["rows"]

# ── Overall result card ───────────────────────────────
if overall == "Eligible":
    ring_color, ring_bg, label_color = "#2E7D32", "#E8F5E9", "#2E7D32"
elif overall == "Not Eligible":
    ring_color, ring_bg, label_color = "#C62828", "#FFEBEE", "#C62828"
else:
    ring_color, ring_bg, label_color = "#F57F17", "#FFF8E1", "#F57F17"

title = opp.get("title", "")
org = opp.get("organization", "")

st.markdown(
    f"""<div class="elig-card">
        <div class="elig-overall">
            <div class="elig-ring"
                 style="border-color:{ring_color}; background:{ring_bg}; color:{ring_color};">
                {match_pct}%
            </div>
            <div class="elig-label" style="color:{label_color};">{overall}</div>
            <div style="color:#616161; font-size:0.88rem; margin-top:0.25rem;">
                {title}<br/>
                <span style="font-size:0.8rem; color:#9E9E9E;">{org}</span>
            </div>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Legend ─────────────────────────────────────────────
st.markdown(
    """<div class="legend-row">
        <div class="legend-item"><span class="legend-dot" style="background:#2E7D32;"></span> Eligible</div>
        <div class="legend-item"><span class="legend-dot" style="background:#C62828;"></span> Not Eligible</div>
        <div class="legend-item"><span class="legend-dot" style="background:#F57F17;"></span> Cannot Determine</div>
    </div>""",
    unsafe_allow_html=True,
)

# ── Per-requirement breakdown ─────────────────────────
if rows:
    st.markdown(
        '<div style="color:#1B2A4A; font-weight:700; font-size:0.95rem; margin:0.6rem 0 0.5rem 0;">'
        'Requirement Breakdown</div>',
        unsafe_allow_html=True,
    )

    for row in rows:
        status = row["status"]
        if status == "Eligible":
            status_cls = "status-eligible"
        elif status == "Not Eligible":
            status_cls = "status-not-eligible"
        else:
            status_cls = "status-cannot"

        st.markdown(
            f"""<div class="req-row">
                <div class="req-header">
                    <span class="req-type">{row['requirement']}</span>
                    <span class="req-status {status_cls}">{status}</span>
                </div>
                <div class="req-values">
                    <div><span class="req-val-label">Your Value</span><br/>
                         <span class="req-val-text">{row['user_value']}</span></div>
                    <div><span class="req-val-label">Required</span><br/>
                         <span class="req-val-text">{row['required']}</span></div>
                </div>
                <div class="req-detail">{row['explanation']}</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("This opportunity has no requirements defined.")

# ── Apply / Already Applied banner ────────────────────
existing_app = get_application_status(user_id, opp_id)

if existing_app:
    # Already applied — show indicator + link
    st.markdown(
        """<div class="applied-banner">
            <div>
                <span style="color:#00695C; font-weight:700; font-size:0.95rem;">
                    ✓ Already Applied
                </span>
                <span style="color:#616161; font-size:0.85rem; margin-left:0.5rem;">
                    You have already submitted an application for this opportunity.
                </span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
    if st.button("View in My Applications →", key="btn_view_apps",
                 use_container_width=True):
        st.switch_page("pages/My_Applications.py")
else:
    # Not yet applied — show Apply Now button
    col_apply, col_spacer = st.columns([1, 2])
    with col_apply:
        if st.button("Apply Now", key="btn_apply_now", type="primary",
                     use_container_width=True):
            result_apply = apply_to_opportunity(user_id, opp_id)
            if result_apply["success"]:
                st.success(result_apply["message"])
                st.rerun()
            else:
                st.error(result_apply["message"])
