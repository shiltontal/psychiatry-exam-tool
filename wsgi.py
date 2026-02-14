import os
import sys

print("=" * 50, flush=True)
print("Starting WSGI application...", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"PORT: {os.environ.get('PORT', 'not set')}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)
print("=" * 50, flush=True)

try:
    print("Step 1: Importing create_app...", flush=True)
    from app import create_app
    print("Step 2: create_app imported", flush=True)
    app = create_app()
    print("Step 3: App created successfully!", flush=True)
except Exception as e:
    print(f"ERROR creating app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    raise

print("WSGI app ready to serve", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask dev server on port {port}...", flush=True)
    app.run(host='0.0.0.0', port=port)
