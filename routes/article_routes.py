from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, abort, jsonify, current_app
)
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.orm import joinedload
import markdown

from data import db_session
from data.articles import Article
from data.article_votes import ArticleVote
from data.comments import Comment
from data.images import Image
from forms import ArticleCreateForm, ArticleEditForm, ImageUploadForm
from utils import get_users_by_usernames, save_image, delete_image, set_featured_image
from config import article_type_dict, article_type_color_dict

article_bp = Blueprint('article', __name__)

# --- Helpers ---


def get_article_or_abort(article_id):
    """Get an article by ID or abort with 404 if not found.
    
    Args:
        article_id: ID of the article to retrieve
        
    Returns:
        Tuple of (db_session, article)
    """
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        db_sess.close()
        abort(404)
    return db_sess, article


def user_can_edit(article):
    """Check if the current user has permission to edit the article.
    
    Args:
        article: Article object to check permissions for
        
    Returns:
        Boolean indicating if user can edit
    """
    return (current_user.id == article.author_id or 
            current_user.username in [e.username for e in article.editors or []])


# --- Routes ---


@article_bp.route('/articles/create', methods=['GET', 'POST'])
@login_required
def create_article():
    """Create a new article."""
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
            editors, missing = get_users_by_usernames(form.editors.data.split(','), db_sess)
            if missing:
                db_sess.close()
                flash(f"Editor(s) not found: {', '.join(missing)}", 'danger')
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
    """Edit an existing article."""
    db_sess, article = get_article_or_abort(article_id)

    if not user_can_edit(article):
        db_sess.close()
        flash("У вас нет прав для редактирования этой статьи.", "danger")
        return redirect(url_for('main.index'))

    form = ArticleEditForm(obj=article)

    if form.validate_on_submit():
        form.populate_obj(article)
        article.updated_date = datetime.now()

        if article.status == 'published' and not article.published_date:
            article.published_date = datetime.now()

        db_sess.commit()

        flash("Статья успешно обновлена.", "success")
        return redirect(url_for('article.article_detail', article_id=article.id))

    return render_template('articles/edit_article.html', form=form, article=article)


@article_bp.route('/articles/view/<int:article_id>')
def article_detail(article_id):
    """View an article's details."""
    db_sess, article = get_article_or_abort(article_id)

    if article.status == 'draft' and not user_can_edit(article):
        db_sess.close()
        return redirect(url_for('main.index'))

    article.view_count += 1
    db_sess.commit()
    
    # Convert markdown content to HTML
    article.content_html = markdown.markdown(
        article.content or '', 
        extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'nl2br']
    )

    return render_template(
        'articles/view_article.html',
        article=article,
        article_type_dict=article_type_dict
    )


@article_bp.route('/articles/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    """Add a comment to an article."""
    content = request.form.get('content')
    if content:
        db_sess = db_session.create_session()
        db_sess.add(Comment(content=content, author_id=current_user.id, article_id=article_id))
        db_sess.commit()
        db_sess.close()
    return redirect(url_for('article.article_detail', article_id=article_id))


@article_bp.route('/articles/<int:article_id>/vote', methods=['POST'])
@login_required
def vote_article(article_id):
    """Vote on an article (upvote or downvote)."""
    vote_type = request.form.get('vote_type')
    vote_value = 1 if vote_type == 'upvote' else -1

    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    vote = db_sess.query(ArticleVote).filter_by(user_id=current_user.id, article_id=article.id).first()

    if vote:
        # If same vote type, remove vote; otherwise change vote value
        if vote.vote == vote_value:
            db_sess.delete(vote)
        else:
            vote.vote = vote_value
    else:
        db_sess.add(ArticleVote(user_id=current_user.id, article_id=article.id, vote=vote_value))

    db_sess.commit()
    db_sess.close()
    return redirect(url_for('article.article_detail', article_id=article_id))


@article_bp.route('/articles/my')
@login_required
def my_articles():
    """View all articles authored by the current user."""
    db_sess = db_session.create_session()
    articles = db_sess.query(Article).filter_by(author_id=current_user.id).all()
    db_sess.close()
    
    return render_template(
        'articles/my_articles.html',
        articles=articles,
        article_type_dict=article_type_dict,
        article_type_color_dict=article_type_color_dict
    )


@article_bp.route('/articles/<int:article_id>/images', methods=['GET', 'POST'])
@login_required
def article_images(article_id):
    """Manage images for an article."""
    db_sess, article = get_article_or_abort(article_id)

    if not user_can_edit(article):
        db_sess.close()
        flash("Нет доступа к изображениям.", "danger")
        return redirect(url_for('main.index'))

    form = ImageUploadForm()

    if form.validate_on_submit() and 'image' in request.files:
        image = save_image(request.files['image'], article_id)
        if not article.featured_image_url and image:
            set_featured_image(article_id, image.id)
            flash("Изображение установлено как главное.", "success")
        else:
            flash("Изображение успешно загружено.", "success")
        return redirect(url_for('article.article_images', article_id=article_id))

    images = db_sess.query(Image).filter_by(article_id=article_id).all()
    db_sess.close()

    return render_template(
        'articles/article_images.html',
        article=article, 
        images=images, 
        form=form
    )


@article_bp.route('/articles/<int:article_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_article_image(article_id, image_id):
    """Delete an image from an article."""
    db_sess, article = get_article_or_abort(article_id)

    if not user_can_edit(article):
        db_sess.close()
        flash("Нет прав для удаления изображения.", "danger")
        return redirect(url_for('main.index'))

    is_featured = article.featured_image_url and str(image_id) in article.featured_image_url

    if delete_image(image_id):
        if is_featured:
            article.featured_image_url = None
            db_sess.commit()
        flash("Изображение удалено.", "success")
    else:
        flash("Ошибка при удалении изображения.", "danger")

    db_sess.close()
    return redirect(url_for('article.article_images', article_id=article_id))


@article_bp.route('/articles/<int:article_id>/images/<int:image_id>/set-featured', methods=['POST'])
@login_required
def set_featured_article_image(article_id, image_id):
    """Set an image as the featured image for an article."""
    db_sess, article = get_article_or_abort(article_id)

    if not user_can_edit(article):
        db_sess.close()
        flash("Нет прав для изменения изображения.", "danger")
        return redirect(url_for('main.index'))

    if set_featured_image(article_id, image_id):
        flash("Главное изображение обновлено.", "success")
    else:
        flash("Не удалось установить главное изображение.", "danger")

    db_sess.close()
    return redirect(url_for('article.article_images', article_id=article_id))
