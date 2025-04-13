from flask import Blueprint, render_template
from data import db_session
from data.categories import Category

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    return render_template('user/index.html', categories=categories)


@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
