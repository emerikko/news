from flask import Blueprint, render_template

error_bp = Blueprint('errors', __name__)


@error_bp.app_errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400


@error_bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401


@error_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# TODO: Remove individual error handlers and make one template for all errors
