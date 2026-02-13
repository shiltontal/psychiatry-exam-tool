import os
print("Starting WSGI application...")
print(f"PORT: {os.environ.get('PORT', 'not set')}")

from app import create_app

app = create_app()
print("App created successfully!")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
