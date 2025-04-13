from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from data import db_session
from data.articles import Article
from forms import ArticleForm

article_bp = Blueprint('article', __name__)

# TODO all of this stuff
# @article_bp.route('/articles/create', methods=['GET', 'POST'])
# @login_required
# def create_article():
#
# @article_bp.route('/articles/edit', methods=['GET', 'POST'])
# @login_required
# def edit_article():
#
# @article_bp.route('/articles/delete', methods=['GET', 'POST'])
# @login_required
# def delete_article():
#
# @article_bp.route('/articles/<int:article_id>', methods=['GET', 'POST'])
# def article_detail(article_id):