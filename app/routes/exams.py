from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db import get_db

bp = Blueprint('exams', __name__)


@bp.route('/')
def list_exams():
    db = get_db()
    exams = db.execute("""
        SELECT e.*, COUNT(eq.id) as question_count
        FROM exams e
        LEFT JOIN exam_questions eq ON eq.exam_id = e.id
        GROUP BY e.id
        ORDER BY e.created_at DESC
    """).fetchall()
    return render_template('exam_list.html', exams=exams)


@bp.route('/new', methods=['GET'])
def new_exam():
    db = get_db()
    questions = db.execute("""
        SELECT q.id, q.stem_he, q.difficulty, q.status, t.hebrew as topic_he, t.chapter_he
        FROM questions q JOIN topics t ON t.id = q.topic_id
        WHERE q.status IN ('approved', 'review')
        ORDER BY t.chapter_code, t.id, q.id
    """).fetchall()

    chapters = db.execute(
        "SELECT DISTINCT chapter_code, chapter_he FROM topics WHERE level=2 ORDER BY chapter_code"
    ).fetchall()
    return render_template('exam_builder.html', exam=None, questions=questions,
                           exam_questions=[], chapters=chapters)


@bp.route('/create', methods=['POST'])
def create_exam():
    title = request.form.get('title', 'מבחן חדש')
    description = request.form.get('description', '')
    question_ids = request.form.getlist('question_ids')

    db = get_db()
    cursor = db.execute(
        "INSERT INTO exams (title, description) VALUES (?, ?)",
        (title, description)
    )
    exam_id = cursor.lastrowid

    for pos, qid in enumerate(question_ids, 1):
        db.execute(
            "INSERT INTO exam_questions (exam_id, question_id, position) VALUES (?, ?, ?)",
            (exam_id, int(qid), pos)
        )
    db.commit()
    flash(f'מבחן "{title}" נוצר עם {len(question_ids)} שאלות', 'success')
    return redirect(url_for('exams.view_exam', exam_id=exam_id))


@bp.route('/<int:exam_id>')
def view_exam(exam_id):
    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id=?", (exam_id,)).fetchone()
    if not exam:
        flash('מבחן לא נמצא', 'error')
        return redirect(url_for('exams.list_exams'))

    exam_qs = db.execute("""
        SELECT eq.position, q.*, t.hebrew as topic_he
        FROM exam_questions eq
        JOIN questions q ON q.id = eq.question_id
        JOIN topics t ON t.id = q.topic_id
        WHERE eq.exam_id = ?
        ORDER BY eq.position
    """, (exam_id,)).fetchall()

    # Available questions not in this exam
    available = db.execute("""
        SELECT q.id, q.stem_he, q.difficulty, t.hebrew as topic_he, t.chapter_he
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        WHERE q.status IN ('approved', 'review')
          AND q.id NOT IN (SELECT question_id FROM exam_questions WHERE exam_id=?)
        ORDER BY t.chapter_code, q.id
    """, (exam_id,)).fetchall()

    chapters = db.execute(
        "SELECT DISTINCT chapter_code, chapter_he FROM topics WHERE level=2 ORDER BY chapter_code"
    ).fetchall()

    return render_template('exam_builder.html', exam=exam, exam_questions=exam_qs,
                           questions=available, chapters=chapters)


@bp.route('/<int:exam_id>/add', methods=['POST'])
def add_questions(exam_id):
    question_ids = request.form.getlist('question_ids')
    db = get_db()
    max_pos = db.execute(
        "SELECT COALESCE(MAX(position), 0) as m FROM exam_questions WHERE exam_id=?",
        (exam_id,)
    ).fetchone()['m']

    for i, qid in enumerate(question_ids, 1):
        db.execute(
            "INSERT INTO exam_questions (exam_id, question_id, position) VALUES (?, ?, ?)",
            (exam_id, int(qid), max_pos + i)
        )
    db.commit()
    return redirect(url_for('exams.view_exam', exam_id=exam_id))


@bp.route('/<int:exam_id>/remove/<int:qid>', methods=['POST'])
def remove_question(exam_id, qid):
    db = get_db()
    db.execute("DELETE FROM exam_questions WHERE exam_id=? AND question_id=?", (exam_id, qid))
    # Re-number positions
    rows = db.execute(
        "SELECT id FROM exam_questions WHERE exam_id=? ORDER BY position", (exam_id,)
    ).fetchall()
    for i, row in enumerate(rows, 1):
        db.execute("UPDATE exam_questions SET position=? WHERE id=?", (i, row['id']))
    db.commit()
    return redirect(url_for('exams.view_exam', exam_id=exam_id))


@bp.route('/<int:exam_id>/preview')
def preview(exam_id):
    db = get_db()
    exam = db.execute("SELECT * FROM exams WHERE id=?", (exam_id,)).fetchone()
    questions = db.execute("""
        SELECT eq.position, q.*
        FROM exam_questions eq
        JOIN questions q ON q.id = eq.question_id
        WHERE eq.exam_id = ?
        ORDER BY eq.position
    """, (exam_id,)).fetchall()
    return render_template('exam_preview.html', exam=exam, questions=questions)


@bp.route('/<int:exam_id>/delete', methods=['POST'])
def delete_exam(exam_id):
    db = get_db()
    db.execute("DELETE FROM exam_questions WHERE exam_id=?", (exam_id,))
    db.execute("DELETE FROM exams WHERE id=?", (exam_id,))
    db.commit()
    flash('המבחן נמחק', 'success')
    return redirect(url_for('exams.list_exams'))
