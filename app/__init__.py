from flask import Flask, session, redirect, url_for, request
from datetime import timedelta
import config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Configure file uploads
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
    app.config['UPLOAD_FOLDER'] = config.DATA_DIR

    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    # Ensure data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)

    try:
        from app.db import init_db, close_db
        init_db(app)
        app.teardown_appcontext(close_db)
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Continue anyway - app can still run without pre-loaded data

    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.questions import bp as questions_bp
    from app.routes.exams import bp as exams_bp
    from app.routes.export import bp as export_bp
    from app.routes.api import bp as api_bp
    from app.routes.uploads import bp as uploads_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(exams_bp, url_prefix='/exams')
    app.register_blueprint(export_bp, url_prefix='/export')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp)

    @app.before_request
    def require_login():
        # Allow access to login page and static files
        allowed_endpoints = ['auth.login', 'static']
        if request.endpoint in allowed_endpoints:
            return None
        if not session.get('authenticated'):
            return redirect(url_for('auth.login'))

    return app
