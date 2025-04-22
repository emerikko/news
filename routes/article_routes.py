from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from data import db_session
from datetime import datetime
from forms import ArticleCreateForm, ArticleEditForm, ImageUploadForm
from flask_login import login_required, current_user

from data.articles import Article
from data.article_votes import ArticleVote
from data.comments import Comment
from data.images import Image
from utils import get_users_by_usernames, save_image, delete_image, set_featured_image
from config import article_type_dict, article_type_color_dict
import markdown

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
                db_sess.close()
                flash(f"Editor(s) not found: {', '.join(missing_editors)}", 'danger')
                return render_template('articles/create_article.html', form=form)
            article.editors.extend(editors)
        db_sess.add(article)
        db_sess.commit()
        article_id = article.id
        db_sess.close()

        flash('Article created successfully!', 'success')
        return redirect(url_for('article.edit_article', article_id=article_id))

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
        db_sess.close()
        flash("У вас нет прав для редактирования этой статьи.", "danger")
        return redirect(url_for('main.index'))

    form = ArticleEditForm(obj=article)

    if form.validate_on_submit():
        form.populate_obj(article)

        article.updated_date = datetime.now()

        if article.status == 'published' and article.published_date is None:
            article.published_date = datetime.now()

        db_sess.commit()
        article_id = article.id
        db_sess.close()

        flash("Статья успешно обновлена.", "success")
        return redirect(url_for('article.article_detail', article_id=article_id))

    return render_template('articles/edit_article.html', form=form, article=article)


@article_bp.route('/articles/view/<int:article_id>', methods=['GET', 'POST'])
def article_detail(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        db_sess.close()
        abort(404)
    if (article.status == 'draft' and
            (article.author_id != current_user.id or current_user.username not in article.editors)):
        db_sess.close()
        return redirect(url_for('main.index'))

    article.view_count += 1
    db_sess.commit()
    
    article.content_html = markdown.markdown(
        article.content or '',
        extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'nl2br']
    )
    return render_template('articles/view_article.html',
                           article=article, article_type_dict=article_type_dict)


@article_bp.route('/articles/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    content = request.form.get('content')
    db_sess = db_session.create_session()
    if content:
        comment = Comment(content=content, author_id=current_user.id, article_id=article_id)
        db_sess.add(comment)
        db_sess.commit()
        db_sess.close()
    else:
        db_sess.close()
    return redirect(url_for('article.article_detail', article_id=article_id))


@article_bp.route('/articles/<int:article_id>/vote', methods=['POST'])
@login_required
def vote_article(article_id):
    db_sess = db_session.create_session()
    vote_type = request.form.get('vote_type')  # 'upvote' or 'downvote'
    vote_value = 1 if vote_type == 'upvote' else -1

    article = db_sess.query(Article).get(article_id)

    existing_vote = db_sess.query(ArticleVote).filter_by(user_id=current_user.id, article_id=article.id).first()
    if existing_vote:
        if existing_vote.vote == vote_value:
            db_sess.delete(existing_vote)
        else:
            existing_vote.vote = vote_value
    else:
        new_vote = ArticleVote(article=article, user_id=current_user.id, vote=vote_value)
        db_sess.add(new_vote)
    db_sess.commit()
    article_id = article.id
    db_sess.close()
    return redirect(url_for('article.article_detail', article_id=article_id))


@article_bp.route('/articles/my', methods=['GET'])
@login_required
def my_articles():
    db_sess = db_session.create_session()
    articles = db_sess.query(Article).filter_by(author_id=current_user.id).all()
    return render_template(
        'articles/my_articles.html',
        articles=articles,
        article_type_dict=article_type_dict,
        article_type_color_dict=article_type_color_dict
    )

# Image handling routes
@article_bp.route('/articles/<int:article_id>/images', methods=['GET', 'POST'])
@login_required
def article_images(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not article or (article.author_id != current_user.id and current_user.username not in article.editors):
        db_sess.close()
        flash("У вас нет прав для редактирования изображений этой статьи.", "danger")
        return redirect(url_for('main.index'))
    
    form = ImageUploadForm()
    
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename:
            image = save_image(request.files['image'], article_id)
            if not article.featured_image_url and image:
                # Set as featured if this is the first image
                set_featured_image(article_id, image.id)
                flash("Изображение загружено и установлено как главное.", "success")
            else:
                flash("Изображение успешно загружено.", "success")
        else:
            flash("Пожалуйста, выберите файл для загрузки.", "warning")
        
        return redirect(url_for('article.article_images', article_id=article_id))

    images = db_sess.query(Image).filter_by(article_id=article_id).all()
    db_sess.close()
    
    return render_template('articles/article_images.html', 
                          article=article, 
                          images=images, 
                          form=form)


@article_bp.route('/articles/<int:article_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_article_image(article_id, image_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not article or (article.author_id != current_user.id and current_user.username not in article.editors):
        db_sess.close()
        flash("У вас нет прав для удаления изображений этой статьи.", "danger")
        return redirect(url_for('main.index'))

    is_featured = article.featured_image_url and article.featured_image_url.endswith(f"/{image_id}")

    if delete_image(image_id):
        if is_featured:
            article.featured_image_url = None
            db_sess.commit()
        db_sess.close()
        flash("Изображение успешно удалено.", "success")
    else:
        db_sess.close()
        flash("Не удалось удалить изображение.", "danger")
    
    return redirect(url_for('article.article_images', article_id=article_id))


@article_bp.route('/articles/<int:article_id>/images/<int:image_id>/set-featured', methods=['POST'])
@login_required
def set_featured_article_image(article_id, image_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not article or (article.author_id != current_user.id and current_user.username not in article.editors):
        db_sess.close()
        flash("У вас нет прав для изменения изображений этой статьи.", "danger")
        return redirect(url_for('main.index'))

    if set_featured_image(article_id, image_id):
        flash("Главное изображение статьи обновлено.", "success")
    else:
        flash("Не удалось установить изображение как главное.", "danger")
    
    return redirect(url_for('article.article_images', article_id=article_id))

# TODO: Add delete article route
