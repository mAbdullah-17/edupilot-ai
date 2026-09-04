-- EduPilot AI — Complete MySQL 8.x Database Schema
-- Day 1 Foundation
-- Day 2 Opportunity Discovery
-- Day 3 Application Tracking
-- Day 4 AI Student Tools
-- Day 5 Notifications & Audit Logs

CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('STUDENT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS user_preferences (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    user_id               INT NOT NULL,
    notification_enabled  BOOLEAN NOT NULL DEFAULT TRUE,
    email_enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    preferred_language    VARCHAR(10) NOT NULL DEFAULT 'en',
    preferred_location    VARCHAR(255) DEFAULT NULL,

    CONSTRAINT fk_prefs_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_user_prefs (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS profiles (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE,

    date_of_birth       DATE DEFAULT NULL,
    nationality         VARCHAR(100) DEFAULT NULL,
    country             VARCHAR(100) DEFAULT NULL,
    province            VARCHAR(100) DEFAULT NULL,
    city                VARCHAR(100) DEFAULT NULL,

    education_level     VARCHAR(100) DEFAULT NULL,
    current_institution VARCHAR(255) DEFAULT NULL,
    current_field      VARCHAR(255) DEFAULT NULL,
    current_cgpa       DECIMAL(3,2) DEFAULT NULL,

    profile_image_path  VARCHAR(500) DEFAULT NULL,

    -- Contact / Professional fields
    phone               VARCHAR(30) DEFAULT NULL,
    linkedin_url        VARCHAR(500) DEFAULT NULL,
    github_url          VARCHAR(500) DEFAULT NULL,
    website             VARCHAR(500) DEFAULT NULL,

    -- Profile sections
    experience          TEXT DEFAULT NULL,
    skills              TEXT DEFAULT NULL,
    career_preferences  TEXT DEFAULT NULL,

    profile_completion  TINYINT UNSIGNED NOT NULL DEFAULT 0,

    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_profile_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    token_hash  VARCHAR(255) NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    used_at     TIMESTAMP NULL DEFAULT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prt_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_prt_hash (token_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Day 2: Opportunity Discovery ────────────────────────

CREATE TABLE IF NOT EXISTS opportunities (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    organization      VARCHAR(255) NOT NULL,
    description       TEXT NOT NULL,
    category          VARCHAR(100) NOT NULL,
    opportunity_type  VARCHAR(100) NOT NULL,
    location          VARCHAR(255) DEFAULT NULL,
    city              VARCHAR(100) DEFAULT NULL,
    province          VARCHAR(100) DEFAULT NULL,
    country           VARCHAR(100) DEFAULT NULL,
    region            VARCHAR(100) DEFAULT NULL,
    deadline          DATE DEFAULT NULL,
    external_url      VARCHAR(500) DEFAULT NULL,
    eligibility_summary TEXT DEFAULT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                      ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_opp_status (status),
    INDEX idx_opp_category (category),
    INDEX idx_opp_type (opportunity_type),
    INDEX idx_opp_deadline (deadline),
    INDEX idx_opp_city (city),
    INDEX idx_opp_province (province),
    INDEX idx_opp_country (country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS opportunity_requirements (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    opportunity_id    INT NOT NULL,
    requirement_type  VARCHAR(100) NOT NULL,
    description       TEXT NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_oppreq_opp
        FOREIGN KEY (opportunity_id)
        REFERENCES opportunities(id)
        ON DELETE CASCADE,

    INDEX idx_oppreq_opp (opportunity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS saved_opportunities (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    user_id           INT NOT NULL,
    opportunity_id    INT NOT NULL,
    saved_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_saved_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_saved_opp
        FOREIGN KEY (opportunity_id)
        REFERENCES opportunities(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_user_opp (user_id, opportunity_id),
    INDEX idx_saved_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Day 3: Application Tracking ──────────────────────────

CREATE TABLE IF NOT EXISTS applications (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT NOT NULL,
    opportunity_id   INT NOT NULL,

    status           ENUM(
        'applied',
        'in_review',
        'shortlisted',
        'rejected'
    ) NOT NULL DEFAULT 'applied',

    applied_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                     ON UPDATE CURRENT_TIMESTAMP,

    notes            TEXT DEFAULT NULL,

    CONSTRAINT fk_app_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_app_opp
        FOREIGN KEY (opportunity_id)
        REFERENCES opportunities(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_user_app (user_id, opportunity_id),
    INDEX idx_app_user (user_id),
    INDEX idx_app_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Day 4: AI Student Tools ──────────────────────────────

CREATE TABLE IF NOT EXISTS chat_sessions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(255) DEFAULT 'New Chat',
    context_type    VARCHAR(50) NOT NULL DEFAULT 'General',
    context_id      INT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_chat_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_chat_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS chat_messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      INT NOT NULL,
    role            ENUM('user','assistant') NOT NULL,
    content         TEXT NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chatmsg_session
        FOREIGN KEY (session_id)
        REFERENCES chat_sessions(id)
        ON DELETE CASCADE,

    INDEX idx_chatmsg_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS study_materials (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    filename        VARCHAR(255) NOT NULL,
    file_type       VARCHAR(50) DEFAULT NULL,
    file_path       VARCHAR(500) DEFAULT NULL,
    uploaded_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_study_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_study_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS study_results (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    material_id     INT NOT NULL,
    user_id         INT NOT NULL,
    result_type     VARCHAR(50) NOT NULL,
    content         LONGTEXT NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_studyres_mat
        FOREIGN KEY (material_id)
        REFERENCES study_materials(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_studyres_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_studyres_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS study_plans (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(255) NOT NULL,
    subject         VARCHAR(255) DEFAULT NULL,
    exam_date       DATE DEFAULT NULL,
    available_hours INT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_studyplan_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_studyplan_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS study_tasks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    plan_id         INT NOT NULL,
    title           VARCHAR(255) NOT NULL,
    description     TEXT DEFAULT NULL,
    due_date        DATE DEFAULT NULL,
    is_completed    BOOLEAN NOT NULL DEFAULT FALSE,
    week_number     INT DEFAULT NULL,
    day_of_week     VARCHAR(20) DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_studytask_plan
        FOREIGN KEY (plan_id)
        REFERENCES study_plans(id)
        ON DELETE CASCADE,

    INDEX idx_studytask_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS career_recommendations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    career_title    VARCHAR(255) NOT NULL,
    match_score     INT DEFAULT NULL,
    explanation     TEXT DEFAULT NULL,
    skill_gaps      TEXT DEFAULT NULL,
    roadmap         TEXT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_career_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_career_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS resume_analyses (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    filename        VARCHAR(255) DEFAULT NULL,
    target_role     VARCHAR(255) DEFAULT NULL,
    strengths       TEXT DEFAULT NULL,
    weaknesses      TEXT DEFAULT NULL,
    detected_skills TEXT DEFAULT NULL,
    missing_keywords TEXT DEFAULT NULL,
    ats_score       INT DEFAULT NULL,
    ats_notes       TEXT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_resume_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_resume_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS interview_sessions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    role_title      VARCHAR(255) NOT NULL,
    difficulty      VARCHAR(50) NOT NULL DEFAULT 'Beginner',
    interview_type  VARCHAR(50) NOT NULL DEFAULT 'Mixed',
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at     TIMESTAMP NULL DEFAULT NULL,

    CONSTRAINT fk_interview_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_interview_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS interview_questions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    session_id      INT NOT NULL,
    question        TEXT NOT NULL,
    user_answer     TEXT DEFAULT NULL,
    feedback        TEXT DEFAULT NULL,
    question_order  INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_intq_session
        FOREIGN KEY (session_id)
        REFERENCES interview_sessions(id)
        ON DELETE CASCADE,

    INDEX idx_intq_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Day 5: Notifications ──────────────────────────────

CREATE TABLE IF NOT EXISTS notifications (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    notif_type      VARCHAR(50) NOT NULL DEFAULT 'info',
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notif_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_notif_user (user_id),
    INDEX idx_notif_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── Day 5: Audit Logs ────────────────────────────────

CREATE TABLE IF NOT EXISTS audit_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    actor_id        INT NOT NULL,
    actor_email     VARCHAR(255) NOT NULL,
    action          VARCHAR(100) NOT NULL,
    entity_type     VARCHAR(100) DEFAULT NULL,
    entity_id       INT DEFAULT NULL,
    details         TEXT DEFAULT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_audit_actor (actor_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;