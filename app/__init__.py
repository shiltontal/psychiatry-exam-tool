from flask import Flask
import config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Ensure data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)

    try:
        from app.db import init_db, close_db
        init_db(app)
        app.teardown_appcontext(close_db)
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Continue anyway - app can still run without pre-loaded data

    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.questions import bp as questions_bp
    from app.routes.exams import bp as exams_bp
    from app.routes.export import bp as export_bp
    from app.routes.api import bp as api_bp
    from app.routes.uploads import bp as uploads_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(exams_bp, url_prefix='/exams')
    app.register_blueprint(export_bp, url_prefix='/export')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(uploads_bp)

    return app
