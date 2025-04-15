from flask import Blueprint, render_template, redirect, url_for, flash, request
from data import db_session
from data.articles import Article
from datetime import datetime
from forms import ArticleCreateForm, ArticleEditForm
from flask_login import login_required, current_user
from utils import get_users_by_usernames

article_bp = Blueprint('article', __name__)


@article_bp.route('/articles/create', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleCreateForm()

    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            category_id=form.category.data,
            content_type=form.content_type.data,
            author_id=current_user.id
        )
        db_sess = db_session.create_session()

        if form.editors.data:
            editors, missing_editors = get_users_by_usernames(form.editors.data.split(','), db_sess)

            if missing_editors:
                flash(f"Editor(s) not found: {', '.join(missing_editors)}", 'danger')
                return render_template('articles/create_article.html', form=form)
            article.editors.extend(editors)

        db_sess.add(article)
        db_sess.commit()

        flash('Article created successfully!', 'success')
        return redirect(url_for('article.edit_article', article_id=article.id))

    return render_template('articles/create_article.html', form=form)


@article_bp.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    db_sess = db_session.create_session()

    article = db_sess.query(Article).get(article_id)
    # Ensure the current user is either the author or in the editors list
    is_author = current_user == article.author
    is_editor = current_user.username in (article.editors or [])
    if not (is_author or is_editor):
        flash("У вас нет прав для редактирования этой статьи.", "danger")
        return redirect(url_for('main.index'))

    form = ArticleEditForm(obj=article)

    if form.validate_on_submit():
        form.populate_obj(article)

        article.updated_date = datetime.now()

        if article.status == 'published' and article.published_date is None:
            article.published_date = datetime.now()

        db_sess.commit()
        flash("Статья успешно обновлена.", "success")
        return redirect(url_for('main.index', article_id=article.id))

    # On GET, prefill the editors field with a comma-separated string
    if request.method == 'GET' and article.editors:
        form.editors.data = ', '.join(article.editors)

    return render_template('articles/edit_article.html', form=form, article=article)


# TODO: Add delete article route
# TODO: Add view article route


@article_bp.route('/articles/<int:article_id>', methods=['GET', 'POST'])
def article_detail(article_id):
    return render_template('404.html'), 404
