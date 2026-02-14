import json
import sqlite3
import config


def import_syllabus_data():
    conn = sqlite3.connect(config.DB_PATH)

    topics_count = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    mappings_count = conn.execute("SELECT COUNT(*) FROM topic_mappings").fetchone()[0]

    with open(config.PHASE1_PATH, 'r', encoding='utf-8') as f:
        phase1 = json.load(f)
    with open(config.PHASE2_PATH, 'r', encoding='utf-8') as f:
        phase2 = json.load(f)

    # Import topics if empty
    if topics_count == 0:
        for t in phase1['topics']:
            conn.execute(
                "INSERT INTO topics (id, chapter_code, chapter_en, chapter_he, level, hebrew, english, parent_id, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (t['id'], t['chapter'], t['chapter_en'], t['chapter_he'],
                 t['level'], t['hebrew'], t['english'], t.get('parent_id'), t.get('notes', ''))
            )
        print(f"Imported {len(phase1['topics'])} topics.")

    # Import mappings if empty (even if topics exist)
    if mappings_count == 0:
        for m in phase2['results']:
            conn.execute(
                "INSERT OR REPLACE INTO topic_mappings (topic_id, synopsis_pages, synopsis_titles, "
                "synopsis_page_count, synopsis_confidence, dulcan_pages, dulcan_titles, "
                "dulcan_page_count, dulcan_confidence, search_terms) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (m['id'], m['synopsis_toc_pages'], m['synopsis_toc_titles'],
                 m['synopsis_text_pages_count'], m['synopsis_confidence'],
                 m['dulcan_toc_pages'], m['dulcan_toc_titles'],
                 m['dulcan_text_pages_count'], m['dulcan_confidence'],
                 m['search_terms_used'])
            )
        print(f"Imported {len(phase2['results'])} topic mappings.")

    conn.commit()
    conn.close()
