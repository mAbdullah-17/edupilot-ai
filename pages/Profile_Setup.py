
"""Screen 3 — Profile Setup.

Loads existing data, allows sections to be saved independently,
and calculates profile completion.
"""

import datetime

import streamlit as st

from components.theme import CUSTOM_CSS
from components.sidebar import require_login, render_student_sidebar
from components.icons import svg as _icon

from modules.profile import (
    save_section,
    calculate_completion,
    ensure_profile_exists,
    get_profile,
)


# ── Page configuration ────────────────────────────────

st.set_page_config(
    page_title="Profile Setup — EduPilot AI",
    layout="wide",
)


# ── Custom CSS ─────────────────────────────────────────

st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True,
)


# ── Remove unwanted SVG elements ──────────────────────

st.html(
    """
    <style>
        svg {
            display: none !important;
            visibility: hidden !important;
        }

        span[style*="display:inline-flex"] {
            display: inline-flex !important;
            visibility: visible !important;
        }
    </style>
    """
)


require_login()


# ── Sidebar ────────────────────────────────────────────

render_student_sidebar()


user_id = st.session_state["user_id"]

completed = st.session_state.setdefault(
    "completed_profile_sections",
    set()
)

ensure_profile_exists(user_id)


# ── Load existing profile data from MySQL ─────────────

if "_profile_loaded" not in st.session_state:

    profile = get_profile(user_id)

    if profile:

        profile_fields = (
            "date_of_birth",
            "nationality",
            "country",
            "province",
            "city",
            "education_level",
            "current_institution",
            "current_field",
            "phone",
            "linkedin_url",
            "github_url",
            "website",
            "experience",
            "skills",
            "career_preferences",
        )

        for key in profile_fields:

            value = profile.get(key)

            if value is not None:
                st.session_state[f"pf_{key}"] = value

        cgpa = profile.get("current_cgpa")

        if cgpa is not None:
            st.session_state["pf_current_cgpa"] = float(cgpa)

        st.session_state["_profile_loaded"] = True


# ══════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        padding: 0.5rem 0 1rem 0;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.2rem;
        ">
            {_icon("clipboard", 22, "#1B2A4A")}
            Complete Your Profile
        </div>

        <div style="
            color: #616161;
            font-size: 1rem;
            margin-top: 0.35rem;
        ">
            Every section is optional — skip what you don't know
            and fill in later.
        </div>

    </div>
    """
)


# ══════════════════════════════════════════════════════
# SECTION 1 — PERSONAL
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 0.5rem;
        border-left: 4px solid #2E7D32;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("person", 20, "#1B2A4A")}
            Personal Information
        </div>

    </div>
    """
)


with st.form("personal_form"):

    col1, col2 = st.columns(2)

    with col1:

        dob = st.date_input(
            "Date of Birth",
            value=None,
            key="pf_date_of_birth",
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today(),
        )

        nationality = st.text_input(
            "Nationality",
            key="pf_nationality",
        )

        country = st.text_input(
            "Country",
            key="pf_country",
        )

    with col2:

        province = st.text_input(
            "Province / State",
            key="pf_province",
        )

        city = st.text_input(
            "City",
            key="pf_city",
        )

    btn_save_personal = st.form_submit_button(
        "Save Personal Info",
        type="primary",
    )

    btn_skip_personal = st.form_submit_button(
        "Skip",
    )


if btn_save_personal:

    data = {
        "date_of_birth":
            dob if dob and dob.year > 1920 else None,

        "nationality":
            nationality,

        "country":
            country,

        "province":
            province,

        "city":
            city,
    }

    save_section(
        user_id,
        "personal",
        data,
    )

    completed.add("personal")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Personal information saved."
    )


if btn_skip_personal and not btn_save_personal:

    completed.add("personal")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Personal information skipped."
    )


st.html(
    "<div style='height: 1rem;'></div>"
)


# ══════════════════════════════════════════════════════
# SECTION 2 — EDUCATION
# ══════════════════════════════════════════════════════

EDU_OPTIONS = [
    "",
    "Intermediate / A-Levels",
    "Bachelor's",
    "Master's",
    "PhD",
    "Diploma",
    "Other",
]


saved_edu = st.session_state.get(
    "pf_education_level",
    "",
)

edu_index = (
    EDU_OPTIONS.index(saved_edu)
    if saved_edu in EDU_OPTIONS
    else 0
)


st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 0.5rem;
        border-left: 4px solid #009688;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("school", 20, "#1B2A4A")}
            Education
        </div>

    </div>
    """
)


with st.form("education_form"):

    col1, col2 = st.columns(2)

    with col1:

        edu_level = st.selectbox(
            "Education Level",
            EDU_OPTIONS,
            index=edu_index,
            key="pf_education_level",
        )

        institution = st.text_input(
            "Current Institution",
            key="pf_current_institution",
        )

    with col2:

        field = st.text_input(
            "Field of Study",
            key="pf_current_field",
        )

        cgpa = st.number_input(
            "Current CGPA",
            min_value=0.0,
            max_value=4.0,
            step=0.01,
            key="pf_current_cgpa",
        )

    btn_save_edu = st.form_submit_button(
        "Save Education",
        type="primary",
    )

    btn_skip_edu = st.form_submit_button(
        "Skip",
    )


if btn_save_edu:

    data = {
        "education_level":
            edu_level,

        "current_institution":
            institution,

        "current_field":
            field,

        "current_cgpa":
            cgpa if cgpa > 0 else None,
    }

    save_section(
        user_id,
        "education",
        data,
    )

    completed.add("education")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Education information saved."
    )


if btn_skip_edu and not btn_save_edu:

    completed.add("education")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Education skipped."
    )


st.html(
    "<div style='height: 1rem;'></div>"
)


# ══════════════════════════════════════════════════════
# SECTION 3 — CONTACT / PROFESSIONAL
# KEPT UNCHANGED
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 0.5rem;
        border-left: 4px solid #1B2A4A;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("phone", 20, "#1B2A4A")}
            Contact & Professional Information
        </div>

    </div>
    """
)


with st.form("contact_form"):

    col1, col2 = st.columns(2)

    with col1:

        phone = st.text_input(
            "Phone / Contact Number",
            key="pf_phone",
        )

        linkedin = st.text_input(
            "LinkedIn URL",
            key="pf_linkedin_url",
            placeholder="https://linkedin.com/in/...",
        )

    with col2:

        github = st.text_input(
            "GitHub URL",
            key="pf_github_url",
            placeholder="https://github.com/...",
        )

        website = st.text_input(
            "Personal / Portfolio Website",
            key="pf_website",
            placeholder="https://...",
        )

    btn_save_contact = st.form_submit_button(
        "Save Contact Info",
        type="primary",
    )

    btn_skip_contact = st.form_submit_button(
        "Skip",
    )


if btn_save_contact:

    # Basic URL validation
    url_fields = {
        "linkedin_url": linkedin,
        "github_url": github,
        "website": website,
    }

    valid = True

    for name, url in url_fields.items():

        if url and not url.startswith(
            ("http://", "https://")
        ):

            st.error(
                f"{name.replace('_', ' ').title()} "
                "must start with http:// or https://"
            )

            valid = False
            break

    if valid:

        data = {
            "phone": phone,
            "linkedin_url": linkedin,
            "github_url": github,
            "website": website,
        }

        save_section(
            user_id,
            "contact",
            data,
        )

        completed.add("contact")

        calculate_completion(
            user_id,
            completed,
        )

        st.success(
            "Contact information saved."
        )


if btn_skip_contact and not btn_save_contact:

    completed.add("contact")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Contact information skipped."
    )


st.html(
    "<div style='height: 1rem;'></div>"
)


# ══════════════════════════════════════════════════════
# SECTION 4 — EXPERIENCE
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem;
        border-left: 4px solid #2E7D32;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("work", 20, "#1B2A4A")}
            Experience
        </div>

        <div style="
            color: #616161;
            font-size: 0.9rem;
            margin-top: 0.6rem;
        ">
            Tell us about your work, internship, volunteer,
            or project experience.
        </div>

    </div>
    """
)


with st.form("experience_form"):

    experience = st.text_area(
        "Experience",
        key="pf_experience",
        placeholder=(
            "Example: Software Engineering Intern at ABC Company "
            "for 3 months. Worked on Python and web development."
        ),
        height=130,
    )

    col1, col2 = st.columns(2)

    with col1:

        btn_save_experience = st.form_submit_button(
            "Save Experience",
            type="primary",
        )

    with col2:

        btn_skip_experience = st.form_submit_button(
            "Skip",
        )


if btn_save_experience:

    if experience.strip():

        save_section(
            user_id,
            "experience",
            {
                "experience":
                    experience.strip()
            },
        )

        completed.add("experience")

        calculate_completion(
            user_id,
            completed,
        )

        st.success(
            "Experience information saved."
        )

    else:

        st.warning(
            "Please enter your experience or choose Skip."
        )


if btn_skip_experience and not btn_save_experience:

    completed.add("experience")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Experience skipped."
    )


st.html(
    "<div style='height: 0.5rem;'></div>"
)


# ══════════════════════════════════════════════════════
# SECTION 5 — SKILLS
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem;
        border-left: 4px solid #009688;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("build", 20, "#1B2A4A")}
            Skills
        </div>

        <div style="
            color: #616161;
            font-size: 0.9rem;
            margin-top: 0.6rem;
        ">
            Add the technical and professional skills you have.
        </div>

    </div>
    """
)


with st.form("skills_form"):

    skills = st.text_area(
        "Skills",
        key="pf_skills",
        placeholder=(
            "Example: Python, C++, Machine Learning, "
            "HTML, CSS, MySQL, Communication"
        ),
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:

        btn_save_skills = st.form_submit_button(
            "Save Skills",
            type="primary",
        )

    with col2:

        btn_skip_skills = st.form_submit_button(
            "Skip",
        )


if btn_save_skills:

    if skills.strip():

        save_section(
            user_id,
            "skills",
            {
                "skills":
                    skills.strip()
            },
        )

        completed.add("skills")

        calculate_completion(
            user_id,
            completed,
        )

        st.success(
            "Skills saved."
        )

    else:

        st.warning(
            "Please enter your skills or choose Skip."
        )


if btn_skip_skills and not btn_save_skills:

    completed.add("skills")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Skills skipped."
    )


st.html(
    "<div style='height: 0.5rem;'></div>"
)


# ══════════════════════════════════════════════════════
# SECTION 6 — CAREER PREFERENCES
# ══════════════════════════════════════════════════════

st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 0.5rem;
        border-left: 4px solid #1B2A4A;
    ">

        <div style="
            color: #1B2A4A;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        ">
            {_icon("bookmark", 20, "#1B2A4A")}
            Career Preferences
        </div>

        <div style="
            color: #616161;
            font-size: 0.9rem;
            margin-top: 0.6rem;
        ">
            Tell EduPilot AI what type of career opportunities
            you are interested in.
        </div>

    </div>
    """
)


with st.form("career_form"):

    career_preferences = st.text_area(
        "Career Preferences",
        key="pf_career_preferences",
        placeholder=(
            "Example: I am interested in AI, Machine Learning "
            "and Software Engineering internships and jobs."
        ),
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:

        btn_save_career = st.form_submit_button(
            "Save Career Preferences",
            type="primary",
        )

    with col2:

        btn_skip_career = st.form_submit_button(
            "Skip",
        )


if btn_save_career:

    if career_preferences.strip():

        save_section(
            user_id,
            "career",
            {
                "career_preferences":
                    career_preferences.strip()
            },
        )

        completed.add("career")

        calculate_completion(
            user_id,
            completed,
        )

        st.success(
            "Career preferences saved."
        )

    else:

        st.warning(
            "Please enter your career preferences or choose Skip."
        )


if btn_skip_career and not btn_save_career:

    completed.add("career")

    calculate_completion(
        user_id,
        completed,
    )

    st.success(
        "Career preferences skipped."
    )


st.html(
    "<div style='height: 1.5rem;'></div>"
)


# ══════════════════════════════════════════════════════
# COMPLETION SUMMARY
# ══════════════════════════════════════════════════════

completion_pct = st.session_state.get(
    "_last_completion",
    None,
)

if completion_pct is None:

    profile = get_profile(user_id)

    completion_pct = (
        profile["profile_completion"]
        if profile
        else 0
    )


progress_color = (
    "#2E7D32"
    if completion_pct >= 75
    else (
        "#FFA000"
        if completion_pct >= 40
        else "#D32F2F"
    )
)


st.html(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        text-align: center;
        margin-bottom: 1.5rem;
    ">

        <div style="
            color: #616161;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        ">
            Profile Completion
        </div>

        <div style="
            font-size: 2.5rem;
            font-weight: 700;
            color: {progress_color};
        ">
            {completion_pct}%
        </div>

    </div>
    """
)


st.progress(
    completion_pct / 100
    if completion_pct
    else 0
)


st.html(
    "<div style='height: 1rem;'></div>"
)


# ══════════════════════════════════════════════════════
# FINISH
# ══════════════════════════════════════════════════════

col_finish, col_later = st.columns(2)


with col_finish:

    if st.button(
        "Go to Dashboard",
        type="primary",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )


with col_later:

    if st.button(
        "Finish Later",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )

