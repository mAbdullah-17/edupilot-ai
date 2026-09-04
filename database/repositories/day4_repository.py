"""Day 4 data-access functions — AI Chat, Study, Career, Resume, Interview.

All queries are scoped to the authenticated user (user_id filter).
"""

import json
from database.database import get_db


# ── Chat ────────────────────────────────────────────────

def create_chat_session(user_id: int, title: str = "New Chat",
                        context_type: str = "General",
                        context_id: int | None = None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO chat_sessions (user_id, title, context_type, context_id) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, title, context_type, context_id),
    )


def get_user_chat_sessions(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, title, context_type, context_id, created_at, updated_at "
        "FROM chat_sessions WHERE user_id = %s "
        "ORDER BY updated_at DESC",
        (user_id,), fetch=True,
    )


def get_chat_messages(session_id: int, user_id: int) -> list:
    db = get_db()
    # Verify ownership first
    owner = db.execute(
        "SELECT user_id FROM chat_sessions WHERE id = %s",
        (session_id,), fetch=True,
    )
    if not owner or owner[0]["user_id"] != user_id:
        return []
    return db.execute(
        "SELECT id, role, content, created_at FROM chat_messages "
        "WHERE session_id = %s ORDER BY created_at ASC",
        (session_id,), fetch=True,
    )


def save_chat_message(session_id: int, role: str, content: str,
                      user_id: int) -> int | None:
    db = get_db()
    # Verify ownership
    owner = db.execute(
        "SELECT user_id FROM chat_sessions WHERE id = %s",
        (session_id,), fetch=True,
    )
    if not owner or owner[0]["user_id"] != user_id:
        return None
    msg_id = db.execute(
        "INSERT INTO chat_messages (session_id, role, content) "
        "VALUES (%s, %s, %s)",
        (session_id, role, content),
    )
    # Touch session updated_at
    db.execute(
        "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s",
        (session_id,),
    )
    return msg_id


def update_chat_title(session_id: int, user_id: int, title: str):
    db = get_db()
    db.execute(
        "UPDATE chat_sessions SET title = %s WHERE id = %s AND user_id = %s",
        (title, session_id, user_id),
    )


def delete_chat_session(session_id: int, user_id: int):
    db = get_db()
    db.execute(
        "DELETE FROM chat_sessions WHERE id = %s AND user_id = %s",
        (session_id, user_id),
    )


# ── Study Materials & Results ──────────────────────────

def save_study_material(user_id: int, filename: str,
                        file_type: str | None = None,
                        file_path: str | None = None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO study_materials (user_id, filename, file_type, file_path) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, filename, file_type, file_path),
    )


def get_user_study_materials(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, filename, file_type, uploaded_at "
        "FROM study_materials WHERE user_id = %s ORDER BY uploaded_at DESC",
        (user_id,), fetch=True,
    )


def get_study_material_path(material_id: int, user_id: int) -> str | None:
    db = get_db()
    rows = db.execute(
        "SELECT file_path FROM study_materials WHERE id = %s AND user_id = %s",
        (material_id, user_id), fetch=True,
    )
    return rows[0]["file_path"] if rows else None


def save_study_result(material_id: int, user_id: int,
                       result_type: str, content: str) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO study_results (material_id, user_id, result_type, content) "
        "VALUES (%s, %s, %s, %s)",
        (material_id, user_id, result_type, content),
    )


def get_study_results(user_id: int,
                      material_id: int | None = None) -> list:
    db = get_db()
    if material_id:
        return db.execute(
            "SELECT id, result_type, content, created_at "
            "FROM study_results WHERE user_id = %s AND material_id = %s "
            "ORDER BY created_at DESC",
            (user_id, material_id), fetch=True,
        )
    return db.execute(
        "SELECT sr.id, sr.result_type, sr.content, sr.created_at, "
        "sm.filename FROM study_results sr "
        "JOIN study_materials sm ON sr.material_id = sm.id "
        "WHERE sr.user_id = %s ORDER BY sr.created_at DESC",
        (user_id,), fetch=True,
    )


# ── Study Planner ──────────────────────────────────────

def create_study_plan(user_id: int, title: str,
                      subject: str | None = None,
                      exam_date: str | None = None,
                      available_hours: int | None = None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO study_plans (user_id, title, subject, exam_date, "
        "available_hours) VALUES (%s, %s, %s, %s, %s)",
        (user_id, title, subject, exam_date, available_hours),
    )


def get_user_study_plans(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, title, subject, exam_date, available_hours, created_at "
        "FROM study_plans WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,), fetch=True,
    )


def create_study_task(plan_id: int, title: str,
                      description: str | None = None,
                      due_date: str | None = None,
                      week_number: int | None = None,
                      day_of_week: str | None = None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO study_tasks (plan_id, title, description, due_date, "
        "week_number, day_of_week) VALUES (%s, %s, %s, %s, %s, %s)",
        (plan_id, title, description, due_date, week_number, day_of_week),
    )


def get_study_tasks(plan_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, title, description, due_date, is_completed, "
        "week_number, day_of_week FROM study_tasks "
        "WHERE plan_id = %s ORDER BY week_number, day_of_week",
        (plan_id,), fetch=True,
    )


def toggle_study_task(task_id: int, completed: bool):
    db = get_db()
    db.execute(
        "UPDATE study_tasks SET is_completed = %s WHERE id = %s",
        (completed, task_id),
    )


# ── Career Recommendations ────────────────────────────

def save_career_recommendation(user_id: int, career_title: str,
                               match_score: int | None = None,
                               explanation: str | None = None,
                               skill_gaps: str | None = None,
                               roadmap: str | None = None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO career_recommendations "
        "(user_id, career_title, match_score, explanation, skill_gaps, roadmap) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, career_title, match_score, explanation, skill_gaps, roadmap),
    )


def get_user_career_recommendations(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, career_title, match_score, explanation, skill_gaps, "
        "roadmap, created_at FROM career_recommendations "
        "WHERE user_id = %s ORDER BY match_score DESC",
        (user_id,), fetch=True,
    )


def clear_career_recommendations(user_id: int):
    db = get_db()
    db.execute(
        "DELETE FROM career_recommendations WHERE user_id = %s",
        (user_id,),
    )


# ── Resume Analyses ────────────────────────────────────

def save_resume_analysis(user_id: int, filename: str | None,
                         target_role: str | None,
                         strengths: str | None, weaknesses: str | None,
                         detected_skills: str | None,
                         missing_keywords: str | None,
                         ats_score: int | None,
                         ats_notes: str | None) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO resume_analyses "
        "(user_id, filename, target_role, strengths, weaknesses, "
        "detected_skills, missing_keywords, ats_score, ats_notes) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (user_id, filename, target_role, strengths, weaknesses,
         detected_skills, missing_keywords, ats_score, ats_notes),
    )


def get_user_resume_analyses(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, filename, target_role, strengths, weaknesses, "
        "detected_skills, missing_keywords, ats_score, ats_notes, created_at "
        "FROM resume_analyses WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,), fetch=True,
    )


def get_resume_analysis(analysis_id: int, user_id: int) -> dict | None:
    db = get_db()
    rows = db.execute(
        "SELECT id, filename, target_role, strengths, weaknesses, "
        "detected_skills, missing_keywords, ats_score, ats_notes, created_at "
        "FROM resume_analyses WHERE id = %s AND user_id = %s",
        (analysis_id, user_id), fetch=True,
    )
    return rows[0] if rows else None


# ── Interview Sessions ─────────────────────────────────

def create_interview_session(user_id: int, role_title: str,
                             difficulty: str,
                             interview_type: str) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO interview_sessions "
        "(user_id, role_title, difficulty, interview_type) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, role_title, difficulty, interview_type),
    )


def get_user_interview_sessions(user_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, role_title, difficulty, interview_type, status, "
        "created_at, finished_at FROM interview_sessions "
        "WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,), fetch=True,
    )


def finish_interview_session(session_id: int, user_id: int):
    db = get_db()
    db.execute(
        "UPDATE interview_sessions SET status = 'finished', "
        "finished_at = NOW() WHERE id = %s AND user_id = %s",
        (session_id, user_id),
    )


def save_interview_question(session_id: int, question: str,
                            question_order: int) -> int:
    db = get_db()
    return db.execute(
        "INSERT INTO interview_questions "
        "(session_id, question, question_order) VALUES (%s, %s, %s)",
        (session_id, question, question_order),
    )


def update_question_answer(question_id: int, answer: str):
    db = get_db()
    db.execute(
        "UPDATE interview_questions SET user_answer = %s WHERE id = %s",
        (answer, question_id),
    )


def update_question_feedback(question_id: int, feedback: str):
    db = get_db()
    db.execute(
        "UPDATE interview_questions SET feedback = %s WHERE id = %s",
        (feedback, question_id),
    )


def get_interview_questions(session_id: int) -> list:
    db = get_db()
    return db.execute(
        "SELECT id, question, user_answer, feedback, question_order "
        "FROM interview_questions WHERE session_id = %s "
        "ORDER BY question_order",
        (session_id,), fetch=True,
    )
