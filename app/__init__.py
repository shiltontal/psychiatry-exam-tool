from flask import Flask
import config


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    from app.db import init_db, close_db
    init_db(app)
    app.teardown_appcontext(close_db)

    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.questions import bp as questions_bp
    from app.routes.exams import bp as exams_bp
    from app.routes.export import bp as export_bp
    from app.routes.api import bp as api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(exams_bp, url_prefix='/exams')
    app.register_blueprint(export_bp, url_prefix='/export')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
