
"""Interview Coach — Screen 17: AI-powered mock interview practice."""

import streamlit as st

from components.sidebar import render_student_sidebar
from components.icons import svg as _icon
from database.repositories import day4_repository as repo


# ── Auth guard ─────────────────────────────────────────

if not st.session_state.get("authenticated"):
    st.switch_page("pages/Login.py")
    st.stop()

if st.session_state.get("role") != "STUDENT":
    st.switch_page("pages/Dashboard.py")
    st.stop()

user_id = st.session_state["user_id"]


# ── Session state defaults ─────────────────────────────

_defaults = {
    "interview_session_id": None,
    "interview_current_q": 0,
    "interview_questions": [],
    "interview_active": False,
}

for key, value in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── Sidebar ────────────────────────────────────────────

render_student_sidebar()


# ── Helpers ────────────────────────────────────────────

def _get_groq_client():
    """Return a cached Groq client for fast interview responses."""

    from groq import Groq
    from config import settings

    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "Groq API key is not configured."
        )

    if "_interview_groq_client" not in st.session_state:
        st.session_state["_interview_groq_client"] = Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=20.0,
        )

    return st.session_state["_interview_groq_client"]


def _groq_text(prompt: str, max_tokens: int = 180) -> str:
    """Generate concise interview content using Groq."""

    try:
        import groq as groq_sdk

        response = _get_groq_client().chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise interview coach. "
                        "Answer directly. "
                        "Do not invent candidate facts."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_completion_tokens=max_tokens,
            reasoning_effort="low",
            include_reasoning=False,
        )

        if not response.choices:
            raise RuntimeError(
                "Groq returned no response choices."
            )

        text = (
            response.choices[0].message.content or ""
        ).strip()

        if not text:
            raise RuntimeError(
                "Groq returned an empty response."
            )

        return text

    except groq_sdk.RateLimitError as exc:
        raise RuntimeError(
            "Interview AI is temporarily rate-limited. "
            "Please try again shortly."
        ) from exc

    except groq_sdk.AuthenticationError as exc:
        raise RuntimeError(
            "Groq API key was rejected. "
            "Check GROQ_API_KEY in your .env file."
        ) from exc

    except (
        groq_sdk.APIConnectionError,
        groq_sdk.APITimeoutError,
    ) as exc:
        raise RuntimeError(
            "Could not reach Interview AI. "
            "Please check the internet connection."
        ) from exc

    except groq_sdk.APIStatusError as exc:
        raise RuntimeError(
            f"Interview AI returned an error "
            f"(status {exc.status_code}): {exc}"
        ) from exc

def _generate_question(
    role: str,
    difficulty: str,
    interview_type: str,
    q_number: int,
) -> str:
    """Generate one interview question."""

    prompt = (
        f"Create ONE {difficulty} {interview_type} "
        f"interview question for a candidate applying "
        f"for {role}. "
        f"This is question {q_number}. "
        "Return only the question."
    )

    return _groq_text(
        prompt,
        max_tokens=90,
    )


def _generate_feedback(
    question: str,
    answer: str,
    role: str,
    interview_type: str,
) -> str:
    """Generate short and useful interview feedback."""

    answer = answer.strip()[:3500]
    question = question.strip()[:1000]

    prompt = (
        f"Role: {role}\n"
        f"Interview: {interview_type}\n"
        f"Question: {question}\n"
        f"Candidate answer: {answer}\n\n"
        "Give concise feedback in exactly 3 bullet points:\n"
        "1) What was good\n"
        "2) What to improve\n"
        "3) One practical tip\n"
        "Keep the complete response under 100 words."
    )

    return _groq_text(
        prompt,
        max_tokens=140,
    )


# ── Page header ────────────────────────────────────────

st.markdown(
    f"<h1 style='color:#1B2A4A;margin-bottom:0.2rem;'>"
    f"{_icon('mic', 28, '#2E7D32')} Interview Coach"
    f"</h1>",
    unsafe_allow_html=True,
)

st.caption(
    "Practice mock interviews with AI-powered feedback"
)


# ── Active session ─────────────────────────────────────

session_id = st.session_state.get(
    "interview_session_id"
)

is_active = st.session_state.get(
    "interview_active"
)


if is_active and session_id:

    questions = repo.get_interview_questions(
        session_id
    )

    current_q = st.session_state.get(
        "interview_current_q",
        0,
    )

    # ── Session header ──

    st.markdown(
        "<div style='background:#E8F5E9;"
        "border-radius:8px;padding:0.8rem;"
        "margin-bottom:1rem;'>"
        "<strong>Mock Interview Session</strong> — "
        f"Question {current_q + 1}"
        "</div>",
        unsafe_allow_html=True,
    )

    if current_q < len(questions):

        q = questions[current_q]

        # ── Show question ──

        with st.chat_message("assistant"):
            st.markdown(
                f"**Question {current_q + 1}:**\n\n"
                f"{q['question']}"
            )

        # ── Answer form ──

        if not q.get("user_answer"):

            answer = st.text_area(
                "Your answer:",
                key=f"int_answer_{q['id']}",
                height=120,
                placeholder="Type your answer here...",
            )

            if st.button(
                "Submit Answer",
                key=f"int_submit_{q['id']}",
                use_container_width=True,
            ):

                if answer.strip():

                    with st.spinner("Saving answer..."):
                        repo.update_question_answer(
                            q["id"],
                            answer,
                        )

                    st.rerun()

                else:
                    st.warning(
                        "Please provide an answer."
                    )

        # ── Generate feedback ──

        elif (
            q.get("user_answer")
            and not q.get("feedback")
        ):

            st.markdown(
                f"**Your answer:**\n\n"
                f"{q['user_answer']}"
            )

            with st.spinner(
                "Generating feedback..."
            ):

                try:

                    feedback = _generate_feedback(
                        q["question"],
                        q["user_answer"],
                        st.session_state.get(
                            "_int_role",
                            "the role",
                        ),
                        st.session_state.get(
                            "_int_type",
                            "Mixed",
                        ),
                    )

                    repo.update_question_feedback(
                        q["id"],
                        feedback,
                    )

                    st.rerun()

                except RuntimeError as exc:

                    st.error(str(exc))

        # ── Show feedback ──

        else:

            st.markdown(
                f"**Your answer:**\n\n"
                f"{q['user_answer']}"
            )

            st.markdown(
                f"<div class='success-card'>"
                f"<strong>Feedback:</strong><br>"
                f"{q['feedback']}"
                f"</div>",
                unsafe_allow_html=True,
            )

            # ── Navigation ──

            nav_cols = st.columns(2)

            with nav_cols[0]:

                question_count = int(
                    st.session_state.get(
                        "_int_count",
                        len(questions),
                    )
                )

                if current_q < question_count - 1:

                    if st.button(
                        "Next Question",
                        key=f"int_next_{q['id']}",
                        use_container_width=True,
                    ):

                        next_index = current_q + 1

                        try:

                            with st.spinner(
                                "Generating next question..."
                            ):

                                next_question = (
                                    _generate_question(
                                        st.session_state.get(
                                            "_int_role",
                                            "the role",
                                        ),
                                        st.session_state.get(
                                            "_int_difficulty",
                                            "Intermediate",
                                        ),
                                        st.session_state.get(
                                            "_int_type",
                                            "Mixed",
                                        ),
                                        next_index + 1,
                                    )
                                )

                                repo.save_interview_question(
                                    session_id,
                                    next_question,
                                    next_index,
                                )

                            st.session_state[
                                "interview_current_q"
                            ] = next_index

                            st.rerun()

                        except RuntimeError as exc:

                            st.error(str(exc))

            with nav_cols[1]:

                if st.button(
                    "Finish Session",
                    key=f"int_finish_{q['id']}",
                    use_container_width=True,
                ):

                    repo.finish_interview_session(
                        session_id,
                        user_id,
                    )

                    st.session_state[
                        "interview_active"
                    ] = False

                    st.session_state[
                        "interview_session_id"
                    ] = None

                    st.session_state[
                        "interview_current_q"
                    ] = 0

                    st.rerun()

    else:

        st.info(
            "All questions answered. "
            "Finishing session..."
        )

        repo.finish_interview_session(
            session_id,
            user_id,
        )

        st.session_state[
            "interview_active"
        ] = False

        st.session_state[
            "interview_session_id"
        ] = None

        st.session_state[
            "interview_current_q"
        ] = 0

        st.rerun()

    # ── Cancel button ──

    st.markdown("---")

    if st.button(
        "Cancel Session",
        key="int_cancel",
    ):

        st.session_state[
            "interview_active"
        ] = False

        st.session_state[
            "interview_session_id"
        ] = None

        st.session_state[
            "interview_current_q"
        ] = 0

        st.rerun()


# ── New session setup ─────────────────────────────────

else:

    st.markdown(
        "<h4 style='color:#1B2A4A;'>"
        "Start a New Session"
        "</h4>",
        unsafe_allow_html=True,
    )

    with st.form("interview_setup_form"):

        int_role = st.text_input(
            "Target Role",
            placeholder=(
                "e.g. Software Engineer, "
                "Data Analyst"
            ),
        )

        int_difficulty = st.selectbox(
            "Difficulty",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
            ],
        )

        int_type = st.selectbox(
            "Interview Type",
            [
                "Mixed",
                "HR",
                "Technical",
                "Behavioral",
            ],
        )

        int_count = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=10,
            value=5,
        )

        start_clicked = st.form_submit_button(
            "Start Session",
            use_container_width=True,
        )

    if start_clicked:

        if not int_role:

            st.warning(
                "Please enter a target role."
            )

        else:

            # ── Create session ──

            new_session_id = (
                repo.create_interview_session(
                    user_id,
                    int_role,
                    int_difficulty,
                    int_type,
                )
            )

            st.session_state[
                "_int_role"
            ] = int_role

            st.session_state[
                "_int_difficulty"
            ] = int_difficulty

            st.session_state[
                "_int_type"
            ] = int_type

            # ── Generate first question only ──
            # Remaining questions are generated lazily
            # when the student clicks Next Question.

            with st.spinner(
                "Generating first interview question..."
            ):

                try:

                    question = _generate_question(
                        int_role,
                        int_difficulty,
                        int_type,
                        1,
                    )

                    repo.save_interview_question(
                        new_session_id,
                        question,
                        0,
                    )

                except RuntimeError as exc:

                    st.error(
                        "Could not generate the first question: "
                        f"{exc}"
                    )

                    st.stop()

            # ── Store session state ──

            st.session_state[
                "_int_count"
            ] = int_count

            st.session_state[
                "interview_session_id"
            ] = new_session_id

            st.session_state[
                "interview_active"
            ] = True

            st.session_state[
                "interview_current_q"
            ] = 0

            st.rerun()

    # ── Previous Sessions ──

    st.markdown("---")

    st.markdown(
        "<h4 style='color:#1B2A4A;'>"
        "Previous Sessions"
        "</h4>",
        unsafe_allow_html=True,
    )

    sessions = repo.get_user_interview_sessions(
        user_id
    )

    if not sessions:

        st.markdown(
            "<div style='text-align:center;"
            "padding:2rem;color:#9E9E9E;'>"
            "No interview sessions yet. "
            "Start one above."
            "</div>",
            unsafe_allow_html=True,
        )

    else:

        for sess in sessions:

            with st.expander(
                f"{sess['role_title']} — "
                f"{sess['difficulty']} "
                f"({sess['interview_type']})"
            ):

                st.caption(
                    f"Status: {sess['status']}  |  "
                    f"Started: {sess['created_at']}"
                )

                questions = (
                    repo.get_interview_questions(
                        sess["id"]
                    )
                )

                if questions:

                    for q in questions:

                        st.markdown(
                            f"**Q:** {q['question']}"
                        )

                        if q.get("user_answer"):

                            st.markdown(
                                f"*A:* "
                                f"{q['user_answer']}"
                            )

                        if q.get("feedback"):

                            st.markdown(
                                f"<div class='success-card'>"
                                f"{q['feedback']}"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                        st.markdown("---")
