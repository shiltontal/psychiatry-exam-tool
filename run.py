"""
MCQ Exam Question Development Tool for Child Psychiatry
Run: python run.py
"""
import os
import sys
import webbrowser
import threading

def main():
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        try:
            key = input('Enter your Anthropic API key (or press Enter to skip AI generation): ').strip()
            if key:
                os.environ['ANTHROPIC_API_KEY'] = key
        except EOFError:
            pass  # Non-interactive mode, use key from config.py

    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from app import create_app
    app = create_app()

    port = 5000
    print(f'\n{"="*50}')
    print(f'  MCQ Exam Tool - Child Psychiatry')
    print(f'  http://localhost:{port}')
    print(f'{"="*50}\n')

    # Open browser after delay
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()

    app.run(host='127.0.0.1', port=port, debug=True)


if __name__ == '__main__':
    main()
