"""AI Chat — Screen 18: context-aware conversational assistant."""

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

# ── Session state defaults ─────────────────────────────────
_defaults = {
    "chat_session_id": None,
    "chat_processing": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────
render_student_sidebar()

# ── Helpers ────────────────────────────────────────────

def _build_profile_context(profile: dict | None) -> str:
    """Build a concise context string from the student's profile."""
    if not profile:
        return ""
    parts = []
    if profile.get("education_level"):
        parts.append(f"Education level: {profile['education_level']}")
    if profile.get("current_field"):
        parts.append(f"Field of study: {profile['current_field']}")
    if profile.get("current_institution"):
        parts.append(f"Institution: {profile['current_institution']}")
    if profile.get("country"):
        parts.append(f"Country: {profile['country']}")
    if profile.get("city"):
        parts.append(f"City: {profile['city']}")
    return "\n".join(parts)


def _build_system_prompt(profile_ctx: str, language: str) -> str:
    """Build the system prompt for the AI chat."""
    base = (
        "You are EduPilot AI, a helpful educational assistant. "
        "You help students with scholarship opportunities, study planning, "
        "career guidance, and academic questions. "
        "Be concise, accurate, and encouraging. "
        "Never fabricate student credentials, application statuses, "
        "or official eligibility decisions. "
        "If information is unavailable, say so clearly."
    )
    if language == "Urdu":
        base += " Respond in Urdu language."
    if profile_ctx:
        base += (
            f"\n\nStudent profile context:\n{profile_ctx}\n"
            "Use this context when relevant. Do not invent additional "
            "profile information."
        )
    return base


def _get_ai_service():
    """Lazy-load the AI service singleton."""
    from modules.ai import AIService
    if "ai_service" not in st.session_state:
        st.session_state["ai_service"] = AIService()
    return st.session_state["ai_service"]


def _auto_title(first_message: str) -> str:
    """Generate a short title from the first message."""
    title = first_message.strip()[:50]
    return title + ("..." if len(first_message.strip()) > 50 else "")


# ── Page header ────────────────────────────────────────
st.markdown(
    f"<h1 style='color:#1B2A4A;margin-bottom:0.2rem;'>"
    f"{_icon('chat', 28, '#2E7D32')} AI Chat</h1>",
    unsafe_allow_html=True,
)
st.caption("Your context-aware educational assistant")

# ── Layout: sidebar for sessions + main chat area ─────
col_sessions, col_chat = st.columns([1, 3])

with col_sessions:
    st.markdown(
        "<h4 style='color:#1B2A4A;margin:0 0 0.5rem 0;'>Sessions</h4>",
        unsafe_allow_html=True,
    )

    if st.button(
        "New Chat",
        key="btn_new_chat", use_container_width=True,
    ):
        st.session_state["chat_session_id"] = None
        st.rerun()

    # Language selector
    lang = st.selectbox(
        "Language", ["English", "Urdu"],
        key="chat_lang",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Session list
    sessions = repo.get_user_chat_sessions(user_id)
    if not sessions:
        st.caption("No previous sessions")
    else:
        for sess in sessions:
            btn_label = sess["title"] or "New Chat"
            if len(btn_label) > 30:
                btn_label = btn_label[:30] + "..."
            is_active = (
                st.session_state.get("chat_session_id") == sess["id"]
            )
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                btn_label, key=f"sess_{sess['id']}",
                use_container_width=True, type=btn_type,
            ):
                st.session_state["chat_session_id"] = sess["id"]
                st.rerun()

with col_chat:
    # ── Load or create session ──
    session_id = st.session_state.get("chat_session_id")

    if session_id is None:
        # ── Empty state ──
        st.markdown(
            "<div style='text-align:center;padding:3rem 1rem;color:#9E9E9E;'>"
            "<div style='font-size:1.2rem;margin-bottom:0.5rem;'>"
            "Start a new conversation</div>"
            "<div>Ask about scholarships, study tips, career guidance, "
            "or any educational question.</div></div>",
            unsafe_allow_html=True,
        )

        # Suggested prompts
        st.markdown("**Suggested prompts:**")
        prompts = [
            "What scholarships match my profile?",
            "Help me create a study plan for my exams",
            "What skills should I develop for my career?",
            "How can I improve my application chances?",
        ]
        pcols = st.columns(2)
        for i, prompt_text in enumerate(prompts):
            with pcols[i % 2]:
                if st.button(
                    prompt_text, key=f"suggest_{i}",
                    use_container_width=True,
                ):
                    st.session_state["_chat_pending_prompt"] = prompt_text
                    st.rerun()

    # ── Load messages for active session ──
    messages = []
    if session_id is not None:
        messages = repo.get_chat_messages(session_id, user_id)

    # ── Render message thread ──
    for msg in messages:
        with st.chat_message(
            "user" if msg["role"] == "user" else "assistant"
        ):
            st.markdown(msg["content"])

    # ── Handle pending suggested prompt ──
    if st.session_state.get("_chat_pending_prompt"):
        pending = st.session_state.pop("_chat_pending_prompt")
        # Create session if needed
        if session_id is None:
            title = _auto_title(pending)
            session_id = repo.create_chat_session(
                user_id, title=title, context_type="General"
            )
            st.session_state["chat_session_id"] = session_id
        # Process
        repo.save_chat_message(session_id, "user", pending, user_id)
        profile = get_profile(user_id)
        profile_ctx = _build_profile_context(profile)
        system_prompt = _build_system_prompt(
            profile_ctx, st.session_state.get("chat_lang", "English")
        )
        full_prompt = f"{system_prompt}\n\nStudent: {pending}"
        with st.chat_message("user"):
            st.markdown(pending)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    ai = _get_ai_service()
                    response = ai.generate_text(
                        full_prompt, feature="chat"
                    )
                    st.markdown(response)
                    repo.save_chat_message(
                        session_id, "assistant", response, user_id
                    )
                except RuntimeError as exc:
                    error_msg = str(exc)
                    st.error(error_msg)
                    repo.save_chat_message(
                        session_id, "assistant",
                        f"[Error] {error_msg}", user_id,
                    )
        st.rerun()

    # ── Chat input ──
    user_input = st.chat_input("Ask me anything about education...")
    if user_input:
        # Create session if needed
        if session_id is None:
            title = _auto_title(user_input)
            session_id = repo.create_chat_session(
                user_id, title=title, context_type="General"
            )
            st.session_state["chat_session_id"] = session_id

        # Save user message
        repo.save_chat_message(session_id, "user", user_input, user_id)

        # Build context and call AI
        profile = get_profile(user_id)
        profile_ctx = _build_profile_context(profile)
        system_prompt = _build_system_prompt(
            profile_ctx, st.session_state.get("chat_lang", "English")
        )
        full_prompt = f"{system_prompt}\n\nStudent: {user_input}"

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    ai = _get_ai_service()
                    response = ai.generate_text(
                        full_prompt, feature="chat"
                    )
                    st.markdown(response)
                    repo.save_chat_message(
                        session_id, "assistant", response, user_id
                    )
                except RuntimeError as exc:
                    error_msg = str(exc)
                    st.error(error_msg)
                    repo.save_chat_message(
                        session_id, "assistant",
                        f"[Error] {error_msg}", user_id,
                    )
        st.rerun()
