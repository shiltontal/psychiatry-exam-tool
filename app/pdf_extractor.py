import os
import config

# Lazy load pypdf to save memory at startup
PdfReader = None
pypdf_available = True


def _get_pdf_reader():
    global PdfReader, pypdf_available
    if not pypdf_available:
        return None
    if PdfReader is None:
        try:
            from pypdf import PdfReader as _PdfReader
            PdfReader = _PdfReader
        except ImportError as e:
            print(f"Warning: pypdf not available - PDF extraction disabled. Error: {e}")
            pypdf_available = False
            return None
    return PdfReader


def parse_page_ranges(page_str):
    """Parse page range strings like '23-79; 286-293' into list of (start, end) tuples."""
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
    """Extract text from specified page ranges of a PDF."""
    if not page_ranges:
        return ""
    PdfReader = _get_pdf_reader()
    if PdfReader is None:
        return ""

    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        texts = []
        total = 0

        for start, end in page_ranges:
            for page_num in range(start - 1, min(end, num_pages)):
                page = reader.pages[page_num]
                text = page.extract_text() or ""
                texts.append(f"--- Page {page_num + 1} ---\n{text}")
                total += len(text)
                if total >= max_chars:
                    break
            if total >= max_chars:
                break

        return '\n'.join(texts)[:max_chars]
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def get_topic_content(mapping):
    """
    Extract relevant textbook content for a topic based on its page mappings.
    Returns combined text from Synopsis and Dulcan textbooks.
    """
    parts = []

    # Debug logging
    print(f"[PDF Extractor] Mapping: {mapping}")
    print(f"[PDF Extractor] Synopsis path: {config.SYNOPSIS_PATH}, exists: {os.path.exists(config.SYNOPSIS_PATH)}")
    print(f"[PDF Extractor] Dulcan path: {config.DULCAN_PATH}, exists: {os.path.exists(config.DULCAN_PATH)}")

    # Check if Synopsis PDF exists and extract content
    if mapping and mapping.get('synopsis_pages') and os.path.exists(config.SYNOPSIS_PATH):
        ranges = parse_page_ranges(mapping['synopsis_pages'])
        text = extract_text_for_topic(config.SYNOPSIS_PATH, ranges, max_chars=8000)
        if text:
            parts.append(f"From Synopsis of Psychiatry:\n{text}")

    # Check if Dulcan PDF exists and extract content
    if mapping and mapping.get('dulcan_pages') and os.path.exists(config.DULCAN_PATH):
        remaining = config.MAX_EXTRACT_CHARS - sum(len(p) for p in parts)
        if remaining > 2000:
            ranges = parse_page_ranges(mapping['dulcan_pages'])
            text = extract_text_for_topic(config.DULCAN_PATH, ranges, max_chars=min(7000, remaining))
            if text:
                parts.append(f"From Dulcan's Textbook:\n{text}")

    result = '\n\n'.join(parts) if parts else ''
    print(f"[PDF Extractor] Extracted {len(result)} chars from {len(parts)} sources")
    return result


def check_files_status():
    """Return status of uploaded PDF files."""
    return {
        'synopsis': os.path.exists(config.SYNOPSIS_PATH),
        'dulcan': os.path.exists(config.DULCAN_PATH),
    }
