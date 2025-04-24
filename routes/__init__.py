from .main_routes import main_bp
from .auth_routes import auth_bp
from .profile_routes import profile_bp
from .article_routes import article_bp
from .error_routes import error_bp
from .comments_routes import comments_bp


def register_blueprints(app):
    blueprints = [
        main_bp,
        auth_bp,
        profile_bp,
        article_bp,
        error_bp,
        comments_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)
