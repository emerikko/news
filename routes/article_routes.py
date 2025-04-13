from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from data import db_session
# from data.articles import Article
# from forms import ArticleForm

article_bp = Blueprint('article', __name__)


@article_bp.route('/articles/create', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        article = Article(
            title=form.title.data,
            body=form.body.data,
            category_id=form.category.data,
            author_id=current_user.id
        )
        db_sess.add(article)
        db_sess.commit()
        flash('Статья создана!', 'success')
        return redirect(url_for('main.index'))
    return render_template('articles/create_article.html', form=form)
