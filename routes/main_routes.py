from flask import Blueprint, render_template
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
    articles = sorted(
        [article for article in db_sess.query(Article).all() if article.published_date],
        key=lambda x: x.published_date,
        reverse=True
    )
    db_sess.close()
    return render_template('user/index.html', categories=categories, articles=articles,
                           now=datetime.now(), average_hotness=average_hotness(), hotness=hotness,
                           article_type_color_dict=article_type_color_dict, article_type_dict=article_type_dict)
