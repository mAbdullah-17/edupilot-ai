"""Study Assistant — Screen 13: AI-assisted study from uploaded material."""

import os
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

# ── Session state defaults ─────────────────────────────────
_defaults = {
    "study_material_id": None,
    "study_file_path": None,
    "study_file_bytes": None,
    "study_filename": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────
render_student_sidebar()

# ── Helpers ────────────────────────────────────────────

def _get_ai_service():
    from modules.ai import AIService
    if "ai_service" not in st.session_state:
        st.session_state["ai_service"] = AIService()
    return st.session_state["ai_service"]


_LANG_INSTRUCTION = {
    "English": "Respond in English.",
    "Urdu": "Respond in Urdu language.",
}


def _toggle_task(task_id: int, completed: bool):
    """Callback for toggling a study task."""
    repo.toggle_study_task(task_id, completed)


# ── Page header ────────────────────────────────────────
st.markdown(
    f"<h1 style='color:#1B2A4A;margin-bottom:0.2rem;'>"
    f"{_icon('book', 28, '#2E7D32')} Study Assistant</h1>",
    unsafe_allow_html=True,
)
st.caption("Upload study material and let AI help you learn")

# ── Layout: two columns ────────────────────────────────
col_upload, col_results = st.columns([1, 2])

with col_upload:
    st.markdown(
        "<h4 style='color:#1B2A4A;margin:0 0 0.5rem 0;'>Upload Material</h4>",
        unsafe_allow_html=True,
    )

    lang = st.selectbox(
        "Language", ["English", "Urdu"],
        key="study_lang",
    )

    uploaded_file = st.file_uploader(
        "Upload PDF document",
        type=["pdf"],
        key="study_uploader",
        help="Supported: PDF files only",
    )

    if uploaded_file is not None:
        # Save file and create material record
        if (
            st.session_state.get("study_filename") != uploaded_file.name
        ):
            upload_dir = cfg.UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)
            safe_name = f"study_u{user_id}_{uploaded_file.name}"
            file_path = os.path.join(upload_dir, safe_name)
            file_bytes = uploaded_file.read()
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            mat_id = repo.save_study_material(
                user_id, uploaded_file.name, "pdf", file_path
            )
            st.session_state["study_material_id"] = mat_id
            st.session_state["study_file_path"] = file_path
            st.session_state["study_file_bytes"] = file_bytes
            st.session_state["study_filename"] = uploaded_file.name

        st.success(f"Uploaded: {uploaded_file.name}")
    else:
        # Clear state when file removed
        if st.session_state.get("study_filename"):
            for k in _defaults:
                st.session_state[k] = None

    # Previous materials
    st.markdown("---")
    st.markdown(
        "<h5 style='color:#1B2A4A;'>Previous Materials</h5>",
        unsafe_allow_html=True,
    )
    materials = repo.get_user_study_materials(user_id)
    if not materials:
        st.caption("No materials uploaded yet")
    else:
        for mat in materials:
            st.caption(mat["filename"])

with col_results:
    # ── Empty state ──
    if not st.session_state.get("study_file_bytes"):
        st.markdown(
            "<div style='text-align:center;padding:3rem 1rem;color:#9E9E9E;'>"
            "<div style='font-size:1.2rem;margin-bottom:0.5rem;'>"
            "Upload a study document to begin</div>"
            "<div>Upload a PDF and choose a study action.</div></div>",
            unsafe_allow_html=True,
        )
        st.stop()

    # ── Study actions ──
    st.markdown(
        "<h4 style='color:#1B2A4A;margin:0 0 0.5rem 0;'>Study Actions</h4>",
        unsafe_allow_html=True,
    )
    st.caption("AI-assisted content — verify important information independently")

    action_cols = st.columns(3)
    actions = [
        ("summarize", "Summarize", "clipboard"),
        ("key_points", "Key Points", "list_alt"),
        ("mcqs", "Generate MCQs", "assignment"),
        ("flashcards", "Flashcards", "book"),
        ("explain", "Explain", "school"),
        ("ask", "Ask a Question", "chat"),
    ]

    ai = _get_ai_service()
    file_bytes = st.session_state["study_file_bytes"]
    lang_instr = _LANG_INSTRUCTION.get(
        st.session_state.get("study_lang", "English"), ""
    )
    mat_id = st.session_state.get("study_material_id")

    for idx, (action_key, label, icon_name) in enumerate(actions):
        with action_cols[idx % 3]:
            if st.button(
                label,
                key=f"study_{action_key}",
                use_container_width=True,
            ):
                st.session_state["_study_action"] = action_key
                st.rerun()

    # ── Process action ──
    action = st.session_state.get("_study_action")
    if action:
        # Check if result already cached for this action+material
        cache_key = f"_study_result_{action}_{mat_id}"
        if cache_key in st.session_state:
            st.markdown("---")
            st.markdown(
                f"<h5 style='color:#1B2A4A;'>"
                f"{action.replace('_', ' ').title()} Result</h5>",
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state[cache_key])
        else:
            st.markdown("---")
            task_map = {
                "summarize": (
                    f"Provide a comprehensive summary of this document. "
                    f"{lang_instr}"
                ),
                "key_points": (
                    f"Extract the key points and main concepts from this "
                    f"document as a bulleted list. {lang_instr}"
                ),
                "mcqs": (
                    f"Generate 10 multiple-choice questions based on this "
                    f"document. For each question provide 4 options (A-D) "
                    f"and indicate the correct answer. {lang_instr}"
                ),
                "flashcards": (
                    f"Create 10 flashcards from this document. Format each "
                    f"as 'Front: [question/term]' and 'Back: [answer]'. "
                    f"{lang_instr}"
                ),
                "explain": (
                    f"Explain the main concepts in this document in simple "
                    f"terms as if teaching a student. {lang_instr}"
                ),
                "ask": None,  # handled separately
            }

            if action == "ask":
                question = st.text_input(
                    "Ask a question about this document:",
                    key="study_question_input",
                )
                if st.button("Submit Question", key="study_ask_btn"):
                    if question:
                        with st.spinner("Analyzing document..."):
                            try:
                                result = ai.analyze_document(
                                    file_bytes,
                                    f"Answer this question about the "
                                    f"document: {question}. {lang_instr}",
                                    feature="study",
                                )
                                st.session_state[cache_key] = result
                                if mat_id:
                                    repo.save_study_result(
                                        mat_id, user_id, "ask", result
                                    )
                                st.rerun()
                            except RuntimeError as exc:
                                st.error(str(exc))
                    else:
                        st.warning("Please enter a question.")
            else:
                task = task_map.get(action, "")
                with st.spinner(f"Processing {action.replace('_', ' ')}..."):
                    try:
                        result = ai.analyze_document(
                            file_bytes, task, feature="study"
                        )
                        st.session_state[cache_key] = result
                        if mat_id:
                            repo.save_study_result(
                                mat_id, user_id, action, result
                            )
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))
                        st.session_state.pop("_study_action", None)

# ── Study Planner (submodule — below main area) ────────
st.markdown("---")
st.markdown(
    f"<h3 style='color:#1B2A4A;'>"
    f"{_icon('calendar', 22, '#2E7D32')} Study Planner</h3>",
    unsafe_allow_html=True,
)
st.caption("Tell EduPilot what you want to learn and get a practical task-by-task plan you can follow")

plan_col_form, plan_col_list = st.columns([1, 1])

with plan_col_form:
    with st.form("study_planner_form"):
        plan_title = st.text_input("Plan title (optional)", placeholder="e.g. AI Learning Plan")
        plan_subject = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Python for AI, Machine Learning, Web Development",
        )
        plan_goal = st.text_input(
            "Learning goal (optional)",
            placeholder="e.g. Build a small ML project by the end",
        )
        plan_exam = st.date_input("Target date (optional)", value=None)
        plan_hours = st.number_input(
            "Available hours per week", min_value=1, max_value=60, value=10
        )
        submitted = st.form_submit_button(
            "Create Plan",
            use_container_width=True,
        )

    if submitted and not plan_subject:
        st.warning("Please enter what you want to learn.")

    if submitted and plan_subject:
        ai_svc = _get_ai_service()
        final_plan_title = plan_title.strip() or f"{plan_subject.strip()} Learning Plan"
        exam_date = str(plan_exam) if plan_exam else None
        plan_id = repo.create_study_plan(
            user_id, final_plan_title, plan_subject.strip(), exam_date, plan_hours
        )
        # Generate tasks with AI
        prompt = (
            f"Create a practical learning plan for a student who wants to learn "
            f"'{plan_subject.strip()}'. "
            f"Learning goal: {plan_goal or 'Build solid understanding and practical ability'}. "
            f"Available time: {plan_hours} hours per week. "
            f"Target date: {exam_date or 'none'}. "
            "The plan must be actionable: the student should know exactly what to study "
            "and practise each day. Start from fundamentals and progress toward practical "
            "application. Include learning, hands-on practice, revision, and checkpoints. "
            "Do not make vague tasks such as 'study more'. Create 4 weeks with 5 "
            "actionable tasks per week (one task per study day). Each task must contain: "
            "'title', 'description', 'week_number', 'day_of_week'. Descriptions should "
            "say exactly what the student should learn or do. Return ONLY a JSON array."
        )
        with st.spinner("Generating study plan..."):
            try:
                result = ai_svc.generate_structured_response(
                    prompt, feature="planner", max_output_tokens=1000
                )
                tasks = result if isinstance(result, list) else result.get("tasks", []) if isinstance(result, dict) else []

                # Some Gemini responses wrap the array in a tasks field; support
                # both shapes. Never silently create an empty plan.
                valid_tasks = []
                if isinstance(tasks, list):
                    for task in tasks:
                        if not isinstance(task, dict):
                            continue
                        title = str(task.get("title") or "").strip()
                        description = str(task.get("description") or "").strip()
                        if title and description:
                            valid_tasks.append(task)

                if not valid_tasks:
                    # Reliable local fallback for demo use if the model returns
                    # malformed JSON: the plan still contains concrete actions.
                    subject = plan_subject.strip()
                    fallback = [
                        ("Learn the fundamentals", f"Study the core concepts of {subject}. Write short notes defining the main terms and ideas."),
                        ("Guided practice", f"Complete 3 beginner exercises on {subject}. Check each solution and record mistakes."),
                        ("Hands-on task", f"Build or complete a small practical exercise using {subject}. Focus on applying what you learned."),
                        ("Revision and recall", f"Review this week's {subject} notes without looking at them first, then answer 10 self-test questions."),
                        ("Checkpoint project", f"Create a small project or practical demonstration using {subject} and list the concepts you still need to practise."),
                    ]
                    valid_tasks = [
                        {"title": title, "description": desc, "week_number": 1, "day_of_week": day}
                        for day, (title, desc) in zip(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], fallback)
                    ]

                for task in valid_tasks:
                    repo.create_study_task(
                        plan_id,
                        task["title"],
                        task["description"],
                        None,
                        task.get("week_number") or 1,
                        task.get("day_of_week") or "Monday",
                    )
                st.success(f"Study plan created with {len(valid_tasks)} actionable tasks.")
                st.rerun()
            except RuntimeError as exc:
                # Save plan even if AI fails (user can add tasks manually)
                st.warning(f"Plan saved but AI tasks could not be generated: {exc}")
                st.rerun()

with plan_col_list:
    plans = repo.get_user_study_plans(user_id)
    if not plans:
        st.caption("No study plans yet")
    else:
        for plan in plans[:5]:
            with st.expander(f"{plan['title']}"):
                st.caption(f"Subject: {plan.get('subject', 'N/A')}")
                st.caption(f"Created: {plan['created_at']}")
                tasks = repo.get_study_tasks(plan["id"])
                if tasks:
                    for task in tasks:
                        checked = task["is_completed"]
                        st.checkbox(
                            task["title"],
                            value=checked,
                            key=f"task_{task['id']}",
                            on_change=_toggle_task,
                            args=(task["id"], not checked),
                        )
                        if task.get("description"):
                            st.caption(task["description"])
                        if task.get("week_number") or task.get("day_of_week"):
                            st.caption(f"Week {task.get('week_number') or 1} • {task.get('day_of_week') or ''}")
                else:
                    st.caption("No tasks in this plan")
