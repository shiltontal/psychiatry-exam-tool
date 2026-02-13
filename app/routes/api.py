from flask import Blueprint, jsonify, request
from app.db import get_db

bp = Blueprint('api', __name__)


@bp.route('/topics')
def topics():
    db = get_db()
    chapter = request.args.get('chapter', '')
    if chapter:
        rows = db.execute(
            "SELECT id, hebrew, english, chapter_code FROM topics WHERE level=2 AND chapter_code=? ORDER BY id",
            (chapter,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, hebrew, english, chapter_code FROM topics WHERE level=2 ORDER BY chapter_code, id"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.route('/subtopics/<int:topic_id>')
def subtopics(topic_id):
    db = get_db()
    rows = db.execute(
        "SELECT id, hebrew, english FROM topics WHERE parent_id=? ORDER BY id",
        (topic_id,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.route('/coverage')
def coverage():
    db = get_db()
    rows = db.execute("""
        SELECT t.id, t.hebrew, t.english, t.chapter_code, t.chapter_he,
               COUNT(q.id) as total,
               SUM(CASE WHEN q.status='approved' THEN 1 ELSE 0 END) as approved,
               SUM(CASE WHEN q.status='draft' THEN 1 ELSE 0 END) as drafts
        FROM topics t
        LEFT JOIN questions q ON q.topic_id = t.id
        WHERE t.level = 2
        GROUP BY t.id
        ORDER BY t.chapter_code, t.id
    """).fetchall()
    return jsonify([dict(r) for r in rows])
