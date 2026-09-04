"""Screen — Opportunity Details (Day 2).

Displays full details for a single opportunity including
description, requirements, external URL, and save/unsave.
"""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar, render_admin_sidebar
from modules import opportunities as opp_svc

st.set_page_config(page_title="Opportunity Details — EduPilot AI", layout="wide")
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
    .detail-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1.2rem;
    }
    .detail-title {
        color: #1B2A4A;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
    }
    .detail-org {
        color: #616161;
        font-size: 1rem;
        margin: 0 0 1rem 0;
    }
    .detail-section-heading {
        color: #1B2A4A;
        font-size: 1rem;
        font-weight: 700;
        margin: 1.2rem 0 0.5rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #E8F5E9;
    }
    .detail-meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-bottom: 1rem;
    }
    .detail-meta-item {
        display: flex;
        flex-direction: column;
    }
    .detail-meta-label {
        color: #9E9E9E;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 0.15rem;
    }
    .detail-meta-value {
        color: #1B2A4A;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .detail-badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .detail-desc {
        color: #424242;
        font-size: 0.92rem;
        line-height: 1.6;
    }
    .req-item {
        background: #F5F7FA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
    }
    .req-type {
        color: #2E7D32;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .req-desc {
        color: #424242;
        font-size: 0.88rem;
        margin-top: 0.15rem;
    }
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ── Resolve opportunity ───────────────────────────────
user_id = st.session_state.get("user_id")
opp_id = st.session_state.get("_view_opp_id")

if not opp_id:
    st.warning("No opportunity selected.")
    if st.button("Back to All Opportunities", key="btn_back_empty"):
        st.switch_page("pages/All_Opportunities.py")
    st.stop()

opp = opp_svc.get_opportunity(opp_id)

if not opp:
    st.error("Opportunity not found.")
    if st.button("Back to All Opportunities", key="btn_back_notfound"):
        st.switch_page("pages/All_Opportunities.py")
    st.stop()

# ── Back button ───────────────────────────────────────
if st.button("Back to All Opportunities", key="btn_back_top"):
    st.switch_page("pages/All_Opportunities.py")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── Main detail card ──────────────────────────────────
title = opp.get("title", "")
org = opp.get("organization", "")
desc = opp.get("description", "")
category = opp.get("category", "")
opp_type = opp.get("opportunity_type", "")
location_label = opp_svc.get_location_label(opp)
deadline_str = opp_svc.format_deadline(opp.get("deadline"))
days_left = opp_svc.days_until_deadline(opp.get("deadline"))
external_url = opp.get("external_url")
eligibility = opp.get("eligibility_summary")
is_saved = opp_svc.is_saved(user_id, opp_id)

# Deadline indicator
if days_left is not None:
    if days_left < 0:
        deadline_display = "Closed"
        deadline_color = "#9E9E9E"
    elif days_left <= 14:
        deadline_display = f"{deadline_str} ({days_left} days left)"
        deadline_color = "#D32F2F"
    else:
        deadline_display = f"{deadline_str} ({days_left} days left)"
        deadline_color = "#1B2A4A"
else:
    deadline_display = deadline_str
    deadline_color = "#1B2A4A"

_elig_html = (f'<div class="detail-section-heading">Eligibility Summary</div>'
              f'<div class="detail-desc">{eligibility}</div>') if eligibility else ''

st.markdown(
f'<div class="detail-card">'
f'<div class="detail-title">{title}</div>'
f'<div class="detail-org">{org}</div>'
f'<div class="detail-meta-row">'
f'<div class="detail-meta-item">'
f'<span class="detail-meta-label">Category</span>'
f'<span class="detail-badge" style="background:#E8F5E9; color:#2E7D32;">{category}</span>'
f'</div>'
f'<div class="detail-meta-item">'
f'<span class="detail-meta-label">Type</span>'
f'<span class="detail-badge" style="background:#E3F2FD; color:#1565C0;">{opp_type}</span>'
f'</div>'
f'<div class="detail-meta-item">'
f'<span class="detail-meta-label">Location</span>'
f'<span class="detail-meta-value">{location_label}</span>'
f'</div>'
f'<div class="detail-meta-item">'
f'<span class="detail-meta-label">Deadline</span>'
f'<span class="detail-meta-value" style="color:{deadline_color};">{deadline_display}</span>'
f'</div>'
f'</div>'
f'<div class="detail-section-heading">Description</div>'
f'<div class="detail-desc">{desc}</div>'
f'{_elig_html}'
f'</div>',
unsafe_allow_html=True,
)

# ── Requirements section ──────────────────────────────
requirements = opp_svc.get_requirements(opp_id)

if requirements:
    st.markdown(
'<div class="detail-section-heading" style="padding: 0 0.2rem;">Requirements</div>',
        unsafe_allow_html=True,
    )
    for req in requirements:
        req_type = req.get("requirement_type", "").upper()
        req_desc = req.get("description", "")
        st.markdown(
f'<div class="req-item"><div class="req-type">{req_type}</div><div class="req-desc">{req_desc}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

# ── Actions ───────────────────────────────────────────
action_col1, action_col2, action_col3, action_spacer = st.columns([1, 1, 1, 3])

with action_col1:
    btn_label = "Unsave Opportunity" if is_saved else "Save Opportunity"
    if st.button(btn_label, key="detail_save", use_container_width=True):
        if is_saved:
            opp_svc.unsave_opportunity(user_id, opp_id)
        else:
            opp_svc.save_opportunity(user_id, opp_id)
        st.rerun()

with action_col2:
    if st.button("Check Eligibility", key="detail_check_elig",
                 use_container_width=True):
        st.session_state["_elig_run_id"] = opp_id
        st.switch_page("pages/Eligibility_Analysis.py")

with action_col3:
    if external_url:
        st.markdown(
            f"""<a href="{external_url}" target="_blank" rel="noopener noreferrer"
                   style="display: inline-block; width: 100%; text-align: center;
                          padding: 0.45rem 1rem; background-color: #2E7D32;
                          color: #FFFFFF; border-radius: 8px; text-decoration: none;
                          font-weight: 600; font-size: 0.9rem;">
                Apply Externally
            </a>""",
            unsafe_allow_html=True,
        )
