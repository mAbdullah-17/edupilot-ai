"""Resume Analyzer — Screen 15: upload and analyze a resume against a target role."""

import os
import json
import streamlit as st
from components.sidebar import render_student_sidebar
from components.icons import svg as _icon
from config import settings as cfg
from database.repositories import day4_repository as repo

# ── Auth guard ─────────────────────────────────────────
if not st.session_state.get("authenticated"):
    st.switch_page("pages/Login.py")
    st.stop()
if st.session_state.get("role") != "STUDENT":
    st.switch_page("pages/Dashboard.py")
    st.stop()

user_id = st.session_state["user_id"]

# ── Sidebar ────────────────────────────────────────────
render_student_sidebar()

# ── Helpers ────────────────────────────────────────────

def _get_ai_service():
    from modules.ai import AIService
    if "ai_service" not in st.session_state:
        st.session_state["ai_service"] = AIService()
    return st.session_state["ai_service"]


# ── Page header ────────────────────────────────────────
st.markdown(
    f"<h1 style='color:#1B2A4A;margin-bottom:0.2rem;'>"
    f"{_icon('description', 28, '#2E7D32')} Resume Analyzer</h1>",
    unsafe_allow_html=True,
)
st.caption("Upload your resume and analyse it against a target role")

# ── Upload form ────────────────────────────────────────
with st.form("resume_analysis_form"):
    target_role = st.text_input(
        "Target Role",
        placeholder="e.g. Software Engineer, Data Analyst, Marketing Manager",
    )
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        key="resume_uploader",
    )
    submitted = st.form_submit_button(
        "Analyse Resume",
        use_container_width=True,
    )

if submitted:
    if not uploaded_file:
        st.warning("Please upload a resume file.")
    elif not target_role:
        st.warning("Please enter a target role.")
    else:
        # Save file
        upload_dir = cfg.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        safe_name = f"resume_u{user_id}_{uploaded_file.name}"
        file_path = os.path.join(upload_dir, safe_name)
        file_bytes = uploaded_file.read()
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Analyse with AI
        ai = _get_ai_service()
        task = (
            f"Analyse this resume for the target role: {target_role}. "
            f"Return a JSON object with these keys:\n"
            f"- strengths: a string listing key strengths (2-3 bullet points)\n"
            f"- weaknesses: a string listing areas for improvement "
            f"(2-3 bullet points)\n"
            f"- detected_skills: a string listing detected skills "
            f"(comma-separated)\n"
            f"- missing_keywords: a string listing keywords missing from "
            f"the resume that the target role typically requires\n"
            f"- ats_score: an integer 0-100 estimating ATS compatibility\n"
            f"- ats_notes: a string explaining that the ATS score is an "
            f"indicative estimate and NOT a guarantee of hiring or "
            f"interview selection\n\n"
            f"Return ONLY valid JSON. No text outside the JSON object."
        )

        with st.spinner("Analysing your resume..."):
            try:
                result = ai.analyze_document(
                    file_bytes, task, feature="resume"
                )
                # Parse JSON from response
                parsed = {}
                try:
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start != -1 and end > start:
                        parsed = json.loads(result[start:end])
                except (json.JSONDecodeError, ValueError):
                    parsed = {"raw": result}

                # Save to database
                analysis_id = repo.save_resume_analysis(
                    user_id,
                    uploaded_file.name,
                    target_role,
                    parsed.get("strengths", result),
                    parsed.get("weaknesses", ""),
                    parsed.get("detected_skills", ""),
                    parsed.get("missing_keywords", ""),
                    parsed.get("ats_score"),
                    parsed.get("ats_notes",
                               "This ATS score is an indicative estimate "
                               "and does not guarantee hiring or interview "
                               "selection."),
                )
                st.session_state["_resume_analysis_id"] = analysis_id
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

# ── Show latest analysis result if just generated ─────
analysis_id = st.session_state.get("_resume_analysis_id")
if analysis_id:
    analysis = repo.get_resume_analysis(analysis_id, user_id)
    if analysis:
        st.markdown("---")
        st.markdown(
            f"<h3 style='color:#1B2A4A;'>Analysis Results</h3>"
            f"<p style='color:#616161;'>Target role: "
            f"<strong>{analysis.get('target_role', 'N/A')}</strong></p>",
            unsafe_allow_html=True,
        )

        # ATS Score with disclaimer
        if analysis.get("ats_score") is not None:
            score_color = (
                "#2E7D32" if analysis["ats_score"] >= 60
                else "#FFA000" if analysis["ats_score"] >= 40
                else "#D32F2F"
            )
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #E0E0E0;"
                f"border-radius:10px;padding:1.2rem;margin-bottom:1rem;"
                f"text-align:center;'>"
                f"<div style='font-size:2rem;font-weight:700;"
                f"color:{score_color};'>"
                f"{analysis['ats_score']}%</div>"
                f"<div style='color:#616161;font-size:0.85rem;'>"
                f"ATS Compatibility Indicator (indicative estimate only)</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.caption(
                "This ATS score is an indicative/helpful signal only. "
                "It is NOT a hiring guarantee, employment guarantee, "
                "guaranteed ATS pass, or guaranteed interview."
            )

        result_cols = st.columns(2)
        with result_cols[0]:
            st.markdown(
                "<div class='success-card'><strong>Strengths</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(analysis.get("strengths", "N/A"))

            st.markdown(
                "<div class='warning-card'>"
                "<strong>Areas for Improvement</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(analysis.get("weaknesses", "N/A"))

        with result_cols[1]:
            st.markdown(
                "<div style='background:#E3F2FD;border-left:4px solid #2E7D32;"
                "padding:1rem;border-radius:4px;margin-bottom:1rem;'>"
                "<strong>Detected Skills</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(analysis.get("detected_skills", "N/A"))

            st.markdown(
                "<div style='background:#FFF3E0;border-left:4px solid #FFA000;"
                "padding:1rem;border-radius:4px;margin-bottom:1rem;'>"
                "<strong>Missing Keywords</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(analysis.get("missing_keywords", "N/A"))

        # Actions
        st.markdown("---")
        act_cols = st.columns(3)
        with act_cols[0]:
            if st.button(
                "Re-analyse",
                key="resume_reanalyse", use_container_width=True,
            ):
                st.session_state.pop("_resume_analysis_id", None)
                st.rerun()
        with act_cols[1]:
            # Download notes
            notes = (
                f"Resume Analysis — {analysis.get('target_role', '')}\n\n"
                f"Strengths:\n{analysis.get('strengths', 'N/A')}\n\n"
                f"Areas for Improvement:\n{analysis.get('weaknesses', 'N/A')}"
                f"\n\nDetected Skills:\n"
                f"{analysis.get('detected_skills', 'N/A')}\n\n"
                f"Missing Keywords:\n"
                f"{analysis.get('missing_keywords', 'N/A')}\n\n"
                f"ATS Score: {analysis.get('ats_score', 'N/A')}% "
                f"(indicative estimate only)\n"
            )
            st.download_button(
                "Download Notes",
                data=notes, file_name="resume_analysis.txt",
                mime="text/plain", use_container_width=True,
                key="resume_download",
            )
        with act_cols[2]:
            if st.button(
                "Career Assistant",
                key="resume_to_career", use_container_width=True,
            ):
                st.switch_page("pages/Career_Assistant.py")

        st.session_state.pop("_resume_analysis_id", None)
        st.stop()

# ── Previous analyses ─────────────────────────────────
st.markdown("---")
st.markdown(
    "<h4 style='color:#1B2A4A;'>Previous Analyses</h4>",
    unsafe_allow_html=True,
)
analyses = repo.get_user_resume_analyses(user_id)
if not analyses:
    st.caption("No previous analyses")
else:
    for a in analyses:
        with st.expander(
            f"{a.get('filename', 'Resume')} — {a.get('target_role', 'N/A')} "
            f"({a.get('created_at', '')})"
        ):
            if a.get("ats_score") is not None:
                st.caption(
                    f"ATS Indicator: {a['ats_score']}% "
                    f"(indicative estimate only, not a hiring guarantee)"
                )
            if a.get("strengths"):
                st.markdown(f"**Strengths:** {a['strengths']}")
            if a.get("weaknesses"):
                st.markdown(f"**Improvement Areas:** {a['weaknesses']}")
            if a.get("detected_skills"):
                st.markdown(f"**Skills:** {a['detected_skills']}")
            if a.get("missing_keywords"):
                st.markdown(f"**Missing Keywords:** {a['missing_keywords']}")
