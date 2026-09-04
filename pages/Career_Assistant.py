
"""Career Assistant — Screen 14: career exploration and guidance hub."""

import json
import streamlit as st
from components.sidebar import render_student_sidebar
from components.icons import svg as _icon
from modules.profile import get_profile
from database.repositories import day4_repository as repo

# ── Auth guard ─────────────────────────────────────────
if not st.session_state.get("authenticated"):
    st.switch_page("pages/Login.py")
    st.stop()

if st.session_state.get("role") != "STUDENT":
    st.switch_page("pages/Dashboard.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "Student")

# ── Sidebar ────────────────────────────────────────────
render_student_sidebar()


# ── Helpers ────────────────────────────────────────────

def _get_ai_service():
    from modules.ai import AIService

    if "ai_service" not in st.session_state:
        st.session_state["ai_service"] = AIService()

    return st.session_state["ai_service"]


def _build_career_prompt(profile: dict | None) -> str:
    """Build a career recommendation prompt from the student's profile."""

    base = (
        "You are EduPilot AI, a career guidance assistant. "
        "Based on the student's profile, suggest 5 career paths that "
        "would be a good match. For each career provide:\n"
        "- career_title: the career/job title\n"
        "- match_score: an integer 0-100 based on how well it matches "
        "the student's education and skills\n"
        "- explanation: 2-3 sentences on why this is a good fit\n"
        "- skill_gaps: skills the student should develop\n"
        "- roadmap: suggested learning steps\n\n"
        "Return ONLY a valid JSON array of objects with the above keys. "
        "Do not add any text outside the JSON array.\n\n"
    )

    if profile:
        info = []

        if profile.get("education_level"):
            info.append(f"Education: {profile['education_level']}")

        if profile.get("current_field"):
            info.append(f"Field: {profile['current_field']}")

        if profile.get("current_institution"):
            info.append(
                f"Institution: {profile['current_institution']}"
            )

        if profile.get("country"):
            info.append(f"Country: {profile['country']}")

        if info:
            base += "Student profile:\n" + "\n".join(info)
        else:
            base += (
                "The student has not yet filled in their profile. "
                "Provide general career recommendations for a university "
                "student and clearly state that more personalised "
                "recommendations are available after completing the profile."
            )
    else:
        base += (
            "The student has not yet filled in their profile. "
            "Provide general career recommendations and clearly state "
            "that personalised recommendations require a completed profile."
        )

    return base


# ── Page header ────────────────────────────────────────

st.markdown(
    f"<h1 style='color:#1B2A4A;margin-bottom:0.2rem;'>"
    f"{_icon('work', 28, '#2E7D32')} Career Assistant</h1>",
    unsafe_allow_html=True,
)

st.caption("Career exploration and guidance based on your profile")


# ── Quick navigation to related tools ─────────────────

nav_cols = st.columns(2)

with nav_cols[0]:
    if st.button(
        "Resume Analyzer",
        key="career_to_resume",
        use_container_width=True,
    ):
        st.switch_page("pages/Resume_Analyzer.py")

with nav_cols[1]:
    if st.button(
        "Interview Coach",
        key="career_to_interview",
        use_container_width=True,
    ):
        st.switch_page("pages/Interview_Coach.py")


st.markdown("---")


# ── Generate / Refresh recommendations ────────────────

gen_col1, gen_col2 = st.columns([3, 1])

with gen_col1:
    st.markdown(
        "<h4 style='color:#1B2A4A;'>Career Recommendations</h4>",
        unsafe_allow_html=True,
    )

with gen_col2:
    if st.button(
        "Regenerate",
        key="career_regenerate",
        use_container_width=True,
    ):
        # Remove old recommendations from database
        repo.clear_career_recommendations(user_id)

        # IMPORTANT:
        # Reset the generation flag so the AI generation block
        # runs again after Streamlit reruns.
        st.session_state.pop("_career_generated", None)
        st.session_state.pop("_career_results", None)
        st.session_state.pop("_career_force_new", None)

        # Immediately rerun the page and generate fresh recommendations
        st.rerun()


# ── Load existing recommendations ─────────────────────

existing = repo.get_user_career_recommendations(user_id)


if existing and not st.session_state.get("_career_force_new"):

    # Show saved recommendations
    for rec in existing:
        with st.container():

            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E0E0E0;"
                f"border-radius:10px;padding:1.2rem;margin-bottom:0.8rem;'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;'>"
                f"<h4 style='color:#1B2A4A;margin:0;'>"
                f"{rec['career_title']}</h4>"
                f"<span style='background:#E8F5E9;color:#2E7D32;"
                f"padding:0.3rem 0.8rem;border-radius:20px;font-weight:600;'>"
                f"{rec['match_score']}% Match</span>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            if rec.get("explanation"):
                st.markdown(rec["explanation"])

            if rec.get("skill_gaps"):
                skill_gaps = rec["skill_gaps"]

                # Display JSON/list data cleanly if necessary
                if isinstance(skill_gaps, str):
                    try:
                        parsed_skill_gaps = json.loads(skill_gaps)

                        if isinstance(parsed_skill_gaps, list):
                            skill_gaps = ", ".join(
                                str(item) for item in parsed_skill_gaps
                            )
                        elif isinstance(parsed_skill_gaps, dict):
                            skill_gaps = ", ".join(
                                f"{key}: {value}"
                                for key, value in parsed_skill_gaps.items()
                            )
                    except (json.JSONDecodeError, TypeError):
                        pass

                st.markdown(f"**Skill Gaps:** {skill_gaps}")

            if rec.get("roadmap"):
                roadmap = rec["roadmap"]

                # Display JSON/list data cleanly if necessary
                if isinstance(roadmap, str):
                    try:
                        parsed_roadmap = json.loads(roadmap)

                        if isinstance(parsed_roadmap, list):
                            roadmap = "\n".join(
                                f"{index + 1}. {item}"
                                for index, item in enumerate(parsed_roadmap)
                            )
                        elif isinstance(parsed_roadmap, dict):
                            roadmap = "\n".join(
                                f"**{key}:** {value}"
                                for key, value in parsed_roadmap.items()
                            )
                    except (json.JSONDecodeError, TypeError):
                        pass

                st.markdown(f"**Roadmap:** {roadmap}")


else:

    # ── Generate new recommendations ──────────────────

    profile = get_profile(user_id)

    if not profile or (
        not profile.get("education_level")
        and not profile.get("current_field")
    ):
        st.info(
            "Your profile is incomplete. Career recommendations will be "
            "general. Complete your profile for personalised guidance."
        )

    # Check if we should generate
    if "_career_generated" not in st.session_state:

        # Mark generation as attempted
        st.session_state["_career_generated"] = True

        ai = _get_ai_service()
        prompt = _build_career_prompt(profile)

        with st.spinner(
            "Analysing your profile for career matches..."
        ):
            try:
                result = ai.generate_structured_response(
                    prompt,
                    feature="career",
                )

                # Parse the result
                recs = []

                if isinstance(result, list):
                    recs = result

                elif isinstance(result, dict):

                    # Try to find array in response
                    if "raw" in result:
                        raw = result["raw"]

                        try:
                            start = raw.find("[")
                            end = raw.rfind("]") + 1

                            if start != -1 and end > start:
                                recs = json.loads(
                                    raw[start:end]
                                )

                        except (
                            json.JSONDecodeError,
                            ValueError,
                        ):
                            st.markdown(raw)

                    else:
                        recs = [result]

                # Save recommendations
                saved_count = 0

                for rec in recs:

                    if isinstance(rec, dict):

                        repo.save_career_recommendation(
                            user_id,
                            rec.get(
                                "career_title",
                                "Career Option",
                            ),
                            rec.get("match_score"),
                            rec.get("explanation", ""),
                            rec.get("skill_gaps", ""),
                            rec.get("roadmap", ""),
                        )

                        saved_count += 1

                # If recommendations were successfully saved,
                # reload the page so they appear immediately.
                if saved_count > 0:
                    st.rerun()

                else:
                    st.warning(
                        "EduPilot AI could not generate career "
                        "recommendations right now. Please try "
                        "Regenerate again."
                    )

                    # Allow another generation attempt
                    st.session_state.pop(
                        "_career_generated",
                        None,
                    )

            except RuntimeError as exc:

                st.error(str(exc))

                # Allow retry after an AI failure
                st.session_state.pop(
                    "_career_generated",
                    None,
                )

            except Exception as exc:

                st.error(
                    f"Career recommendation generation failed: {exc}"
                )

                # Allow retry after an unexpected failure
                st.session_state.pop(
                    "_career_generated",
                    None,
                )

    else:

        # Already tried, show empty state
        st.markdown(
            "<div style='text-align:center;padding:2rem;color:#9E9E9E;'>"
            "Click 'Regenerate' to get career recommendations.</div>",
            unsafe_allow_html=True,
        )


# ── Profile info used ─────────────────────────────────

st.markdown("---")

profile = get_profile(user_id)

if profile:

    st.markdown(
        "<h5 style='color:#1B2A4A;'>Profile Information Used</h5>",
        unsafe_allow_html=True,
    )

    info_items = []

    if profile.get("education_level"):
        info_items.append(
            f"Education: {profile['education_level']}"
        )

    if profile.get("current_field"):
        info_items.append(
            f"Field: {profile['current_field']}"
        )

    if profile.get("current_institution"):
        info_items.append(
            f"Institution: {profile['current_institution']}"
        )

    if profile.get("country"):
        info_items.append(
            f"Country: {profile['country']}"
        )

    if info_items:

        for item in info_items:
            st.caption(item)

    else:

        st.caption(
            "No profile details available. "
            "Complete your profile for personalised recommendations."
        )

else:

    st.caption(
        "Profile not found. Complete your profile setup for better results."
    )

