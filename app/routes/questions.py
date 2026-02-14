from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db import get_db

bp = Blueprint('questions', __name__)


@bp.route('/')
def bank():
    db = get_db()
    filters = []
    params = []

    chapter = request.args.get('chapter', '')
    if chapter:
        filters.append("t.chapter_code = ?")
        params.append(chapter)

    topic_id = request.args.get('topic_id', '')
    if topic_id:
        filters.append("q.topic_id = ?")
        params.append(int(topic_id))

    status = request.args.get('status', '')
    if status:
        filters.append("q.status = ?")
        params.append(status)

    difficulty = request.args.get('difficulty', '')
    if difficulty:
        filters.append("q.difficulty = ?")
        params.append(difficulty)

    search = request.args.get('search', '')
    if search:
        filters.append("q.stem_he LIKE ?")
        params.append(f'%{search}%')

    where = " AND ".join(filters) if filters else "1=1"
    questions = db.execute(f"""
        SELECT q.*, t.hebrew as topic_he, t.english as topic_en, t.chapter_he
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        WHERE {where}
        ORDER BY q.created_at DESC
    """, params).fetchall()

    chapters = db.execute(
        "SELECT DISTINCT chapter_code, chapter_he FROM topics WHERE level=2 ORDER BY chapter_code"
    ).fetchall()

    topics = db.execute(
        "SELECT id, hebrew, english, chapter_code FROM topics WHERE level=2 ORDER BY chapter_code, id"
    ).fetchall()

    return render_template('question_bank.html', questions=questions,
                           chapters=chapters, topics=topics,
                           f_chapter=chapter, f_topic=topic_id,
                           f_status=status, f_difficulty=difficulty, f_search=search)


@bp.route('/generate', methods=['GET'])
def generate_form():
    db = get_db()
    chapters = db.execute("""
        SELECT DISTINCT chapter_code, chapter_he, chapter_en
        FROM topics WHERE level=2
        ORDER BY chapter_code
    """).fetchall()

    topics = db.execute("""
        SELECT t.id, t.hebrew, t.english, t.chapter_code,
               COALESCE(tm.synopsis_confidence, '') as syn_conf,
               COALESCE(tm.dulcan_confidence, '') as dul_conf,
               tm.synopsis_pages, tm.dulcan_pages
        FROM topics t
        LEFT JOIN topic_mappings tm ON tm.topic_id = t.id
        WHERE t.level = 2
        ORDER BY t.chapter_code, t.id
    """).fetchall()

    subtopics = db.execute(
        "SELECT id, hebrew, english, parent_id FROM topics WHERE level=3 ORDER BY parent_id, id"
    ).fetchall()

    return render_template('generate.html', chapters=chapters, topics=topics, subtopics=subtopics)


@bp.route('/generate', methods=['POST'])
def generate_run():
    topic_id = int(request.form['topic_id'])
    count = int(request.form.get('count', 3))
    difficulty = request.form.get('difficulty', 'medium')
    clinical_task = request.form.get('clinical_task', 'mixed')
    subtopic_ids = request.form.getlist('subtopic_ids', type=int) or None
    bloom_level = request.form.get('bloom_level', 'application')
    category = request.form.get('category', 'diagnosis')

    try:
        from app.ai_generator import generate_questions
        created_ids = generate_questions(
            topic_id, count, difficulty, clinical_task, subtopic_ids,
            bloom_level=bloom_level, category=category
        )
        flash(f'נוצרו {len(created_ids)} שאלות חדשות בהצלחה!', 'success')
    except Exception as e:
        flash(f'שגיאה ביצירת שאלות: {str(e)}', 'error')
        return redirect(url_for('questions.generate_form'))

    return redirect(url_for('questions.bank', topic_id=topic_id, status='draft'))


@bp.route('/<int:qid>', methods=['GET'])
def edit(qid):
    db = get_db()
    q = db.execute("""
        SELECT q.*, t.hebrew as topic_he, t.english as topic_en
        FROM questions q JOIN topics t ON t.id = q.topic_id
        WHERE q.id = ?
    """, (qid,)).fetchone()
    if not q:
        flash('שאלה לא נמצאה', 'error')
        return redirect(url_for('questions.bank'))

    topics = db.execute(
        "SELECT id, hebrew, english FROM topics WHERE level=2 ORDER BY chapter_code, id"
    ).fetchall()
    return render_template('question_edit.html', q=q, topics=topics)


@bp.route('/<int:qid>', methods=['POST'])
def update(qid):
    db = get_db()
    db.execute("""
        UPDATE questions SET
            topic_id=?, stem_he=?, option_a=?, option_b=?, option_c=?, option_d=?, option_e=?,
            correct_answer=?, explanation_he=?, difficulty=?, bloom_level=?, status=?,
            updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (
        int(request.form['topic_id']),
        request.form['stem_he'],
        request.form['option_a'],
        request.form['option_b'],
        request.form['option_c'],
        request.form['option_d'],
        request.form.get('option_e', ''),
        request.form['correct_answer'],
        request.form.get('explanation_he', ''),
        request.form.get('difficulty', 'medium'),
        request.form.get('bloom_level', 'application'),
        request.form.get('status', 'draft'),
        qid
    ))
    db.commit()
    flash('השאלה עודכנה בהצלחה', 'success')
    return redirect(url_for('questions.edit', qid=qid))


@bp.route('/<int:qid>/delete', methods=['POST'])
def delete(qid):
    db = get_db()
    db.execute("DELETE FROM exam_questions WHERE question_id=?", (qid,))
    db.execute("DELETE FROM question_tags WHERE question_id=?", (qid,))
    db.execute("DELETE FROM questions WHERE id=?", (qid,))
    db.commit()
    flash('השאלה נמחקה', 'success')
    return redirect(url_for('questions.bank'))


@bp.route('/<int:qid>/status/<status>', methods=['POST'])
def set_status(qid, status):
    if status not in ('draft', 'review', 'approved', 'rejected'):
        flash('סטטוס לא חוקי', 'error')
        return redirect(url_for('questions.bank'))
    db = get_db()
    db.execute("UPDATE questions SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, qid))
    db.commit()
    return redirect(request.referrer or url_for('questions.bank'))
