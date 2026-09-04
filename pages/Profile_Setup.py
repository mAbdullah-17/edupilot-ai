"""Screen 3 — Profile Setup  (loads existing data, optional/skippable sections)."""

import datetime
import streamlit as st
from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar
from components.icons import svg as _icon
from modules.profile import (
    save_section, calculate_completion, ensure_profile_exists,
    get_profile,
)

st.set_page_config(page_title="Profile Setup — EduPilot AI", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
require_login()

# ── Sidebar ───────────────────────────────────────────
render_student_sidebar()

user_id = st.session_state["user_id"]
completed = st.session_state.setdefault("completed_profile_sections", set())

ensure_profile_exists(user_id)

# ── Load existing profile data from MySQL ─────────────
# Pre-populate session state so form widgets show saved values.
if "_profile_loaded" not in st.session_state:
    profile = get_profile(user_id)
    if profile:
        for key in ("date_of_birth", "nationality", "country", "province", "city",
                     "education_level", "current_institution", "current_field",
                     "phone", "linkedin_url", "github_url", "website"):
            val = profile.get(key)
            if val is not None:
                st.session_state[f"pf_{key}"] = val
        cgpa = profile.get("current_cgpa")
        if cgpa is not None:
            st.session_state["pf_current_cgpa"] = float(cgpa)
        st.session_state["_profile_loaded"] = True

# ── Page Header ───────────────────────────────────────
st.markdown(
    f"""<div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: #1B2A4A; margin-bottom: 0.2rem;">{_icon("clipboard", 22, "#1B2A4A")} Complete Your Profile</h1>
        <p style="color: #616161; font-size: 1rem;">
            Every section is optional — skip what you don't know and fill in later.
        </p>
    </div>""",
    unsafe_allow_html=True,
)

# ── Section 1: Personal ──────────────────────────────
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
        border-left: 4px solid #2E7D32;
    ">
        <h4 style="color: #1B2A4A; margin: 0;">{_icon("person", 20, "#1B2A4A")} Personal Information</h4>
    </div>""",
    unsafe_allow_html=True,
)
with st.form("personal_form"):
    col1, col2 = st.columns(2)
    with col1:
        dob = st.date_input("Date of Birth", value=None, key="pf_date_of_birth",
                            min_value=datetime.date(1920, 1, 1),
                            max_value=datetime.date.today())
        nationality = st.text_input("Nationality", key="pf_nationality")
        country = st.text_input("Country", key="pf_country")
    with col2:
        province = st.text_input("Province / State", key="pf_province")
        city = st.text_input("City", key="pf_city")

    btn_save_personal = st.form_submit_button("Save Personal Info", type="primary")
    btn_skip_personal = st.form_submit_button("Skip")

if btn_save_personal:
    data = {
        "date_of_birth": dob if dob and dob.year > 1920 else None,
        "nationality": nationality,
        "country": country,
        "province": province,
        "city": city,
    }
    save_section(user_id, "personal", data)
    completed.add("personal")
    calculate_completion(user_id, completed)
    st.success("Personal information saved.")

if btn_skip_personal and not btn_save_personal:
    pass  # nothing to persist

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Section 2: Education ─────────────────────────────
EDU_OPTIONS = ["", "Intermediate / A-Levels", "Bachelor's",
               "Master's", "PhD", "Diploma", "Other"]

# Determine the saved education level index
_saved_edu = st.session_state.get("pf_education_level", "")
_edu_index = EDU_OPTIONS.index(_saved_edu) if _saved_edu in EDU_OPTIONS else 0

st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
        border-left: 4px solid #009688;
    ">
        <h4 style="color: #1B2A4A; margin: 0;">{_icon("school", 20, "#1B2A4A")} Education</h4>
    </div>""",
    unsafe_allow_html=True,
)
with st.form("education_form"):
    col1, col2 = st.columns(2)
    with col1:
        edu_level = st.selectbox("Education Level", EDU_OPTIONS,
                                 index=_edu_index, key="pf_education_level")
        institution = st.text_input("Current Institution", key="pf_current_institution")
    with col2:
        field = st.text_input("Field of Study", key="pf_current_field")
        cgpa = st.number_input("Current CGPA", min_value=0.0, max_value=4.0,
                               step=0.01, key="pf_current_cgpa")

    btn_save_edu = st.form_submit_button("Save Education", type="primary")
    btn_skip_edu = st.form_submit_button("Skip")

if btn_save_edu:
    data = {
        "education_level": edu_level,
        "current_institution": institution,
        "current_field": field,
        "current_cgpa": cgpa if cgpa > 0 else None,
    }
    save_section(user_id, "education", data)
    completed.add("education")
    calculate_completion(user_id, completed)
    st.success("Education information saved.")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Section 3: Contact / Professional ────────────────
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 0.5rem;
        border-left: 4px solid #1B2A4A;
    ">
        <h4 style="color: #1B2A4A; margin: 0;">{_icon("phone", 20, "#1B2A4A")} Contact & Professional Information</h4>
    </div>""",
    unsafe_allow_html=True,
)
with st.form("contact_form"):
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("Phone / Contact Number", key="pf_phone")
        linkedin = st.text_input("LinkedIn URL", key="pf_linkedin_url",
                                 placeholder="https://linkedin.com/in/...")
    with col2:
        github = st.text_input("GitHub URL", key="pf_github_url",
                               placeholder="https://github.com/...")
        website = st.text_input("Personal / Portfolio Website", key="pf_website",
                                placeholder="https://...")

    btn_save_contact = st.form_submit_button("Save Contact Info", type="primary")
    btn_skip_contact = st.form_submit_button("Skip")

if btn_save_contact:
    # Basic URL validation
    url_fields = {"linkedin_url": linkedin, "github_url": github, "website": website}
    valid = True
    for name, url in url_fields.items():
        if url and not url.startswith(("http://", "https://")):
            st.error(f"{name.replace('_', ' ').title()} must start with http:// or https://")
            valid = False
            break
    if valid:
        data = {
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
            "website": website,
        }
        save_section(user_id, "contact", data)
        st.success("Contact information saved.")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Section 4: Experience (placeholder for Day 2+) ───
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem; opacity: 0.75;
    ">
        <h5 style="color: #1B2A4A;">{_icon("work", 20, "#1B2A4A")} Experience</h5>
        <p style="color: #9E9E9E; font-size: 0.9rem;">
            Experience tracking will be available soon. You can skip this section for now.
        </p>
    </div>""",
    unsafe_allow_html=True,
)
if st.button("Skip Experience", key="skip_exp"):
    completed.add("experience")
    calculate_completion(user_id, completed)
    st.success("Skipped.")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── Section 5: Skills (placeholder for Day 2+) ───────
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem; opacity: 0.75;
    ">
        <h5 style="color: #1B2A4A;">{_icon("build", 20, "#1B2A4A")} Skills</h5>
        <p style="color: #9E9E9E; font-size: 0.9rem;">
            Skills management will be available soon. You can skip this section for now.
        </p>
    </div>""",
    unsafe_allow_html=True,
)
if st.button("Skip Skills", key="skip_skills"):
    completed.add("skills")
    calculate_completion(user_id, completed)
    st.success("Skipped.")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── Section 6: Career Preferences (placeholder) ──────
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
        padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem; opacity: 0.75;
    ">
        <h5 style="color: #1B2A4A;">{_icon("bookmark", 20, "#1B2A4A")} Career Preferences</h5>
        <p style="color: #9E9E9E; font-size: 0.9rem;">
            Career preferences will be available soon. You can skip this section for now.
        </p>
    </div>""",
    unsafe_allow_html=True,
)
if st.button("Skip Career Preferences", key="skip_career"):
    completed.add("career")
    calculate_completion(user_id, completed)
    st.success("Skipped.")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# ── Completion summary ────────────────────────────────
completion_pct = st.session_state.get("_last_completion", None)
if completion_pct is None:
    from modules.profile import get_profile as _gp
    _p = _gp(user_id)
    completion_pct = _p["profile_completion"] if _p else 0

progress_color = "#2E7D32" if completion_pct >= 75 else ("#FFA000" if completion_pct >= 40 else "#D32F2F")
st.markdown(
    f"""<div style="
        background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        text-align: center; margin-bottom: 1.5rem;
    ">
        <h4 style="color: #616161; font-size: 0.85rem;">Profile Completion</h4>
        <div style="font-size: 2.5rem; font-weight: 700; color: {progress_color};">{completion_pct}%</div>
    </div>""",
    unsafe_allow_html=True,
)
st.progress(completion_pct / 100 if completion_pct else 0)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# ── Finish / Go to Dashboard ─────────────────────────
col_finish, col_later = st.columns(2)
with col_finish:
    if st.button("Go to Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
with col_later:
    if st.button("Finish Later", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
