from .main_routes import main_bp
from .auth_routes import auth_bp
from .profile_routes import profile_bp
from .article_routes import article_bp
from .error_routes import error_bp
from .comments_routes import comments_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(comments_bp)
