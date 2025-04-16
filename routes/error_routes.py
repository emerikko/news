from flask import Blueprint, render_template

error_bp = Blueprint('errors', __name__)


@error_bp.app_errorhandler(400)
def bad_request_error(error):
    return (render_template('errors/error.html', error_code=400,
                            error_message='Запрос не может быть обработан.',
                            error_description='Проверьте введённые данные или попробуйте ещё раз.'),
            400)


@error_bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401


@error_bp.app_errorhandler(403)
def forbidden_error(error):
    return (render_template('errors/error.html', error_code=403,
                            error_message='Упс! У вас нет прав для доступа к этой странице.',
                            error_description='Пожалуйста, вернитесь на главную или поплачьте об этом.'),
            403)


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return (render_template('errors/error.html', error_code=404,
                            error_message='Упс! Мы не нашли такую страницу.',
                            error_description='Возможно, вы ошиблись в адресе или эта страница больше не существует.'),
            404)


@error_bp.app_errorhandler(500)
def internal_error(error):
    return (render_template('errors/error.html', error_code=500,
                            error_message='Что-то пошло не так с сервером.',
                            error_description='Мы уже работаем над решением. Попробуйте позже.'),
            500)
