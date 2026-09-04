"""Admin Opportunity Management — Day 5. Create / Edit / Archive."""

import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_admin, render_admin_sidebar
from components.icons import svg as _icon
from database.repositories import day5_repository as repo
from modules.opportunities import get_opportunity

st.set_page_config(page_title="Opportunity Management — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_admin()
render_admin_sidebar()

actor_id = st.session_state["user_id"]
actor_email = st.session_state.get("user_email", "admin")

st.markdown(
f"""<div style="padding:0.5rem 0 1rem 0;">
<h1 style="color:#1B2A4A;margin:0 0 0.2rem 0;font-size:1.7rem;">
{_icon("work",22,"#1B2A4A")} Opportunity Management
</h1>
<p style="color:#616161;font-size:0.95rem;margin:0;">
Create, edit, and archive opportunities.
</p>
</div>""",
    unsafe_allow_html=True,
)

if st.button("← Admin Dashboard", key="om_back"):
    st.switch_page("pages/Admin_Dashboard.py")

st.markdown("---")

# ── Feedback ──────────────────────────────────────────
if st.session_state.pop("_om_success", None):
    st.success(st.session_state.pop("_om_msg", "Done."))

_CATEGORIES = ["Scholarship", "Internship", "Job", "Fellowship", "Competition",
                "Grant", "Workshop", "Course", "Exchange Program", "Other"]
_TYPES = ["Merit-Based", "Need-Based", "Open", "Competitive", "Invitation-Only"]

tab_list, tab_create, tab_edit = st.tabs(["All Opportunities", "Create New", "Edit / Archive"])

# ── TAB 1: List ────────────────────────────────────────
with tab_list:
    try:
        opps = repo.get_all_opportunities_admin()
    except Exception as exc:
        st.error(str(exc))
        opps = []

    if not opps:
        st.info("No opportunities found.")
    else:
        st.caption(f"{len(opps)} total opportunities")
        hdr = st.columns([4, 3, 2, 2, 2, 2])
        for col, lbl in zip(hdr, ["Title", "Organization", "Category", "Type", "Status", "Action"]):
            col.markdown(f"**{lbl}**")
        st.markdown("<hr style='margin:0.3rem 0;'>", unsafe_allow_html=True)

        for o in opps:
            oid = o["id"]
            row = st.columns([4, 3, 2, 2, 2, 2])
            row[0].write(o["title"][:40] + ("…" if len(o["title"]) > 40 else ""))
            row[1].write(o["organization"][:30])
            row[2].write(o["category"])
            row[3].write(o["opportunity_type"])
            row[4].write(o["status"])
            with row[5]:
                if o["status"] == "active":
                    if st.button("Archive", key=f"om_arch_{oid}"):
                        try:
                            repo.archive_opportunity(oid)
                            repo.log_action(actor_id, actor_email,
                                            "archive_opportunity", "opportunity",
                                            oid, f"Archived: {o['title']}")
                            st.session_state["_om_success"] = True
                            st.session_state["_om_msg"] = f'"{o["title"]}" archived.'
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                else:
                    st.caption("archived")

# ── TAB 2: Create ──────────────────────────────────────
with tab_create:
    with st.form("create_opp_form"):
        st.markdown("**New Opportunity**")
        c_title = st.text_input("Title *", key="cr_title")
        c_org = st.text_input("Organization *", key="cr_org")
        c_desc = st.text_area("Description *", key="cr_desc", height=100)
        col_a, col_b = st.columns(2)
        with col_a:
            c_cat = st.selectbox("Category *", _CATEGORIES, key="cr_cat")
            c_city = st.text_input("City", key="cr_city")
            c_province = st.text_input("Province", key="cr_prov")
            c_deadline = st.date_input("Deadline", value=None, key="cr_dead")
        with col_b:
            c_type = st.selectbox("Type *", _TYPES, key="cr_type")
            c_country = st.text_input("Country", key="cr_country")
            c_url = st.text_input("External URL", key="cr_url")
            c_elig = st.text_area("Eligibility Summary", key="cr_elig", height=68)
        submitted = st.form_submit_button("Create Opportunity", type="primary",
                                          use_container_width=True)

    if submitted:
        if not c_title.strip() or not c_org.strip() or not c_desc.strip():
            st.error("Title, Organization, and Description are required.")
        else:
            try:
                new_id = repo.create_opportunity({
                    "title": c_title.strip(),
                    "organization": c_org.strip(),
                    "description": c_desc.strip(),
                    "category": c_cat,
                    "opportunity_type": c_type,
                    "city": c_city.strip(),
                    "province": c_province.strip(),
                    "country": c_country.strip(),
                    "deadline": str(c_deadline) if c_deadline else None,
                    "external_url": c_url.strip(),
                    "eligibility_summary": c_elig.strip(),
                })
                repo.log_action(actor_id, actor_email, "create_opportunity",
                                "opportunity", new_id, f"Created: {c_title.strip()}")
                st.session_state["_om_success"] = True
                st.session_state["_om_msg"] = f'Opportunity "{c_title.strip()}" created.'
                st.rerun()
            except Exception as exc:
                st.error(f"Error: {exc}")

# ── TAB 3: Edit ────────────────────────────────────────
with tab_edit:
    try:
        opps_edit = repo.get_all_opportunities_admin()
    except Exception:
        opps_edit = []

    active_opps_edit = [o for o in opps_edit if o["status"] == "active"]
    if not active_opps_edit:
        st.info("No active opportunities to edit.")
    else:
        choices = {f"{o['title']} (#{o['id']})": o["id"] for o in active_opps_edit}
        selected_label = st.selectbox("Select opportunity to edit",
                                      list(choices.keys()), key="ed_select")
        sel_id = choices[selected_label]
        opp_data = get_opportunity(sel_id)

        if opp_data:
            with st.form("edit_opp_form"):
                e_title = st.text_input("Title *", value=opp_data.get("title", ""),
                                        key="ed_title")
                e_org = st.text_input("Organization *",
                                      value=opp_data.get("organization", ""),
                                      key="ed_org")
                e_desc = st.text_area("Description *",
                                      value=opp_data.get("description", ""),
                                      key="ed_desc", height=100)
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_cat_idx = _CATEGORIES.index(opp_data["category"]) \
                        if opp_data.get("category") in _CATEGORIES else 0
                    e_cat = st.selectbox("Category", _CATEGORIES,
                                         index=e_cat_idx, key="ed_cat")
                    e_city = st.text_input("City",
                                           value=opp_data.get("city", "") or "",
                                           key="ed_city")
                    e_prov = st.text_input("Province",
                                           value=opp_data.get("province", "") or "",
                                           key="ed_prov")
                with col_e2:
                    e_type_idx = _TYPES.index(opp_data["opportunity_type"]) \
                        if opp_data.get("opportunity_type") in _TYPES else 0
                    e_type = st.selectbox("Type", _TYPES,
                                          index=e_type_idx, key="ed_type")
                    e_country = st.text_input("Country",
                                              value=opp_data.get("country", "") or "",
                                              key="ed_country")
                    e_url = st.text_input("External URL",
                                          value=opp_data.get("external_url", "") or "",
                                          key="ed_url")
                e_elig = st.text_area("Eligibility Summary",
                                      value=opp_data.get("eligibility_summary", "") or "",
                                      key="ed_elig", height=68)
                save_btn = st.form_submit_button("Save Changes", type="primary",
                                                 use_container_width=True)

            if save_btn:
                if not e_title.strip() or not e_org.strip() or not e_desc.strip():
                    st.error("Title, Organization, and Description are required.")
                else:
                    try:
                        repo.update_opportunity(sel_id, {
                            "title": e_title.strip(),
                            "organization": e_org.strip(),
                            "description": e_desc.strip(),
                            "category": e_cat,
                            "opportunity_type": e_type,
                            "city": e_city.strip(),
                            "province": e_prov.strip(),
                            "country": e_country.strip(),
                            "external_url": e_url.strip(),
                            "eligibility_summary": e_elig.strip(),
                        })
                        repo.log_action(actor_id, actor_email, "edit_opportunity",
                                        "opportunity", sel_id,
                                        f"Edited: {e_title.strip()}")
                        st.session_state["_om_success"] = True
                        st.session_state["_om_msg"] = "Changes saved."
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error: {exc}")
