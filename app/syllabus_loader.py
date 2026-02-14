import json
import sqlite3
import config


def import_syllabus_data():
    import os

    # Check if JSON files exist
    if not os.path.exists(config.PHASE1_PATH):
        print(f"Warning: {config.PHASE1_PATH} not found, skipping syllabus import")
        return
    if not os.path.exists(config.PHASE2_PATH):
        print(f"Warning: {config.PHASE2_PATH} not found, skipping syllabus import")
        return

    conn = sqlite3.connect(config.DB_PATH)

    topics_count = conn.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
    mappings_count = conn.execute("SELECT COUNT(*) FROM topic_mappings").fetchone()[0]

    try:
        with open(config.PHASE1_PATH, 'r', encoding='utf-8') as f:
            phase1 = json.load(f)
        with open(config.PHASE2_PATH, 'r', encoding='utf-8') as f:
            phase2 = json.load(f)
    except Exception as e:
        print(f"Error loading syllabus JSON files: {e}")
        conn.close()
        return

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

    # Always update all mappings from JSON (ensures latest page numbers are used)
    for m in phase2['results']:
        conn.execute(
            "INSERT OR REPLACE INTO topic_mappings (topic_id, synopsis_pages, synopsis_titles, "
            "synopsis_page_count, synopsis_confidence, dulcan_pages, dulcan_titles, "
            "dulcan_page_count, dulcan_confidence, search_terms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (m['id'], m.get('synopsis_toc_pages', ''), m.get('synopsis_toc_titles', ''),
             m.get('synopsis_text_pages_count', 0), m.get('synopsis_confidence', ''),
             m.get('dulcan_toc_pages', ''), m.get('dulcan_toc_titles', ''),
             m.get('dulcan_text_pages_count', 0), m.get('dulcan_confidence', ''),
             m.get('search_terms_used', ''))
        )
    print(f"Synced {len(phase2['results'])} topic mappings from JSON.")

    conn.commit()
    conn.close()
