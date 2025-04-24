from flask import Blueprint, render_template

error_bp = Blueprint('errors', __name__)


def render_error_template(code, message, description):
    return (
        render_template('errors/error.html',
                        error_code=code,
                        error_message=message,
                        error_description=description),
        code
    )


@error_bp.app_errorhandler(400)
def bad_request_error(error):
    return render_error_template(
        400,
        'Запрос не может быть обработан.',
        'Проверьте введённые данные или попробуйте ещё раз.'
    )


@error_bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401


@error_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_error_template(
        403,
        'Упс! У вас нет прав для доступа к этой странице.',
        'Пожалуйста, вернитесь на главную или поплачьте об этом.'
    )


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_error_template(
        404,
        'Упс! Мы не нашли такую страницу.',
        'Возможно, вы ошиблись в адресе или эта страница больше не существует.'
    )


@error_bp.app_errorhandler(500)
def internal_error(error):
    return render_error_template(
        500,
        'Что-то пошло не так с сервером.',
        'Мы уже работаем над решением. Попробуйте позже.'
    )
