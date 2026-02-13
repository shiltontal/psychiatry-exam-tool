import sqlite3
import os
import config
from app.syllabus_loader import import_syllabus_data

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    chapter_code TEXT NOT NULL,
    chapter_en TEXT NOT NULL,
    chapter_he TEXT NOT NULL,
    level INTEGER NOT NULL,
    hebrew TEXT NOT NULL,
    english TEXT NOT NULL,
    parent_id INTEGER,
    notes TEXT DEFAULT '',
    FOREIGN KEY (parent_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS topic_mappings (
    topic_id INTEGER PRIMARY KEY,
    synopsis_pages TEXT,
    synopsis_titles TEXT,
    synopsis_page_count INTEGER,
    synopsis_confidence TEXT,
    dulcan_pages TEXT,
    dulcan_titles TEXT,
    dulcan_page_count INTEGER,
    dulcan_confidence TEXT,
    search_terms TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    stem_he TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    option_e TEXT DEFAULT '',
    correct_answer TEXT NOT NULL,
    explanation_he TEXT DEFAULT '',
    difficulty TEXT DEFAULT 'medium',
    bloom_level TEXT DEFAULT 'application',
    question_type TEXT DEFAULT '',
    status TEXT DEFAULT 'draft',
    source_info TEXT DEFAULT '',
    ai_generated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS question_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exam_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS generation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    prompt_used TEXT,
    raw_response TEXT,
    questions_created INTEGER DEFAULT 0,
    model_used TEXT DEFAULT '',
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_questions_status ON questions(status);
CREATE INDEX IF NOT EXISTS idx_exam_questions_exam ON exam_questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_question_tags_qid ON question_tags(question_id);
"""


def get_db():
    """Get a database connection, reusing one from Flask's g if available."""
    try:
        from flask import g
        if 'db' not in g:
            g.db = sqlite3.connect(config.DB_PATH)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db
    except RuntimeError:
        # Outside Flask request context (e.g., CLI scripts, init)
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def close_db(e=None):
    """Close the database connection at the end of a request."""
    try:
        from flask import g
        db = g.pop('db', None)
        if db is not None:
            db.close()
    except RuntimeError:
        pass


def _migrate_db(conn):
    """Add columns that may not exist in older databases."""
    cursor = conn.execute("PRAGMA table_info(questions)")
    columns = {row[1] for row in cursor.fetchall()}
    if 'question_type' not in columns:
        conn.execute("ALTER TABLE questions ADD COLUMN question_type TEXT DEFAULT ''")
        conn.commit()


def init_db(app):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.executescript(SCHEMA)
    _migrate_db(conn)
    conn.close()
    import_syllabus_data()
