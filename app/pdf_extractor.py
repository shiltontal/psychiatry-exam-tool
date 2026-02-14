import os
import fitz
import config


def parse_page_ranges(page_str):
    ranges = []
    if not page_str or not page_str.strip():
        return ranges
    for part in page_str.split(';'):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            try:
                ranges.append((int(start.strip()), int(end.strip())))
            except ValueError:
                continue
        elif part.isdigit():
            ranges.append((int(part), int(part)))
    return ranges


def extract_text_for_topic(pdf_path, page_ranges, max_chars=8000):
    if not page_ranges:
        return ""
    doc = fitz.open(pdf_path)
    texts = []
    total = 0
    for start, end in page_ranges:
        for page_num in range(start - 1, min(end, len(doc))):
            text = doc[page_num].get_text()
            texts.append(f"--- Page {page_num + 1} ---\n{text}")
            total += len(text)
            if total >= max_chars:
                break
        if total >= max_chars:
            break
    doc.close()
    return '\n'.join(texts)[:max_chars]


def get_topic_content(mapping):
    parts = []

    # Check if Synopsis PDF exists and extract content
    if mapping and mapping['synopsis_pages'] and os.path.exists(config.SYNOPSIS_PATH):
        ranges = parse_page_ranges(mapping['synopsis_pages'])
        text = extract_text_for_topic(config.SYNOPSIS_PATH, ranges, max_chars=8000)
        if text:
            parts.append(f"From Synopsis of Psychiatry:\n{text}")

    # Check if Dulcan PDF exists and extract content
    if mapping and mapping['dulcan_pages'] and os.path.exists(config.DULCAN_PATH):
        remaining = config.MAX_EXTRACT_CHARS - sum(len(p) for p in parts)
        if remaining > 2000:
            ranges = parse_page_ranges(mapping['dulcan_pages'])
            text = extract_text_for_topic(config.DULCAN_PATH, ranges, max_chars=min(7000, remaining))
            if text:
                parts.append(f"From Dulcan's Textbook:\n{text}")

    return '\n\n'.join(parts) if parts else ''


def check_files_status():
    """Return status of uploaded PDF files."""
    return {
        'synopsis': os.path.exists(config.SYNOPSIS_PATH),
        'dulcan': os.path.exists(config.DULCAN_PATH),
    }
