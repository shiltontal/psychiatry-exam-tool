import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env file if it exists
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    with open(_env_path, encoding='utf-8') as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'exam_tool.db')

# PDF paths - use data directory for deployment
SYNOPSIS_PATH = os.environ.get('SYNOPSIS_PATH', os.path.join(DATA_DIR, 'Synopsis 2021.pdf'))
DULCAN_PATH = os.environ.get('DULCAN_PATH', os.path.join(DATA_DIR, 'Dulcan.pdf'))

# JSON data paths - use data directory
PHASE1_PATH = os.path.join(DATA_DIR, 'phase1_topics.json')
PHASE2_PATH = os.path.join(DATA_DIR, 'phase2_mapping.json')

CLAUDE_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
CLAUDE_MODEL = 'claude-sonnet-4-20250514'
MAX_EXTRACT_CHARS = 15000
DEFAULT_QUESTION_COUNT = 3
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
