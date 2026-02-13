from flask import Blueprint, render_template
from app.db import get_db

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    db = get_db()

    # Stats
    total_q = db.execute("SELECT COUNT(*) as c FROM questions").fetchone()['c']
    draft_q = db.execute("SELECT COUNT(*) as c FROM questions WHERE status='draft'").fetchone()['c']
    review_q = db.execute("SELECT COUNT(*) as c FROM questions WHERE status='review'").fetchone()['c']
    approved_q = db.execute("SELECT COUNT(*) as c FROM questions WHERE status='approved'").fetchone()['c']

    # Coverage per chapter
    chapters = db.execute("""
        SELECT t.chapter_he, t.chapter_en, t.chapter_code,
               COUNT(DISTINCT t.id) as topic_count,
               COUNT(DISTINCT q.id) as question_count,
               SUM(CASE WHEN q.status = 'approved' THEN 1 ELSE 0 END) as approved_count
        FROM topics t
        LEFT JOIN questions q ON q.topic_id = t.id
        WHERE t.level = 2
        GROUP BY t.chapter_code
        ORDER BY t.chapter_code
    """).fetchall()

    # Topics with zero questions (gaps)
    gaps = db.execute("""
        SELECT t.id, t.hebrew, t.english, t.chapter_he,
               COALESCE(tm.synopsis_confidence, '') as syn_conf,
               COALESCE(tm.dulcan_confidence, '') as dul_conf,
               COUNT(q.id) as q_count
        FROM topics t
        LEFT JOIN questions q ON q.topic_id = t.id
        LEFT JOIN topic_mappings tm ON tm.topic_id = t.id
        WHERE t.level = 2
        GROUP BY t.id
        HAVING q_count = 0
        ORDER BY t.chapter_code, t.id
    """).fetchall()

    return render_template('dashboard.html',
                           total_q=total_q, draft_q=draft_q,
                           review_q=review_q, approved_q=approved_q,
                           chapters=chapters, gaps=gaps)
