import json
import sqlite3
import config


def import_syllabus_data():
    conn = sqlite3.connect(config.DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    if count > 0:
        conn.close()
        return

    with open(config.PHASE1_PATH, 'r', encoding='utf-8') as f:
        phase1 = json.load(f)
    with open(config.PHASE2_PATH, 'r', encoding='utf-8') as f:
        phase2 = json.load(f)

    for t in phase1['topics']:
        conn.execute(
            "INSERT INTO topics (id, chapter_code, chapter_en, chapter_he, level, hebrew, english, parent_id, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (t['id'], t['chapter'], t['chapter_en'], t['chapter_he'],
             t['level'], t['hebrew'], t['english'], t.get('parent_id'), t.get('notes', ''))
        )

    for m in phase2['results']:
        conn.execute(
            "INSERT INTO topic_mappings (topic_id, synopsis_pages, synopsis_titles, "
            "synopsis_page_count, synopsis_confidence, dulcan_pages, dulcan_titles, "
            "dulcan_page_count, dulcan_confidence, search_terms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (m['id'], m['synopsis_toc_pages'], m['synopsis_toc_titles'],
             m['synopsis_text_pages_count'], m['synopsis_confidence'],
             m['dulcan_toc_pages'], m['dulcan_toc_titles'],
             m['dulcan_text_pages_count'], m['dulcan_confidence'],
             m['search_terms_used'])
        )

    conn.commit()
    conn.close()
    print(f"Imported {len(phase1['topics'])} topics and {len(phase2['results'])} mappings.")
