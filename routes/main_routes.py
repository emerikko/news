from flask import Blueprint, render_template, abort
from config import article_type_color_dict, article_type_dict
from data import db_session
from data.categories import Category
from data.articles import Article
from datetime import datetime
from utils import average_hotness, hotness

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    articles = (db_sess.query(Article).filter_by(status='published').
                order_by(Article.created_date.desc()).all())
    return render_template('user/index.html', categories=categories, articles=articles,
                           now=datetime.now(), average_hotness=average_hotness(), hotness=hotness,
                           article_type_color_dict=article_type_color_dict, article_type_dict=article_type_dict)


@main_bp.route('/category/<slug>')
def category(slug):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.slug == slug).first()
    articles = (db_sess.query(Article).filter_by(category_id=category.id, status='published').
                order_by(Article.created_date.desc()).all())
    if not category:
        db_sess.close()
        abort(404)
    return render_template('user/category.html', category=category, now=datetime.now(),
                           average_hotness=average_hotness(), hotness=hotness,
                           article_type_color_dict=article_type_color_dict, article_type_dict=article_type_dict,
                           articles=articles)
