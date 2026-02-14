import os
import sys

print("=" * 50)
print("Starting WSGI application...")
print(f"Python version: {sys.version}")
print(f"PORT: {os.environ.get('PORT', 'not set')}")
print(f"Working directory: {os.getcwd()}")
print("=" * 50)

try:
    from app import create_app
    print("Imported create_app successfully")
    app = create_app()
    print("App created successfully!")
except Exception as e:
    print(f"ERROR creating app: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
