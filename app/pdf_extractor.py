import os
import config


def get_topic_content(mapping):
    """
    PDF extraction disabled to reduce memory usage on free hosting.
    The AI will generate questions based on its own knowledge.
    """
    return ''


def check_files_status():
    """Return status of uploaded PDF files."""
    return {
        'synopsis': os.path.exists(config.SYNOPSIS_PATH),
        'dulcan': os.path.exists(config.DULCAN_PATH),
    }
