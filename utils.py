import os
import uuid
from datetime import datetime

from flask import current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func

import config
from data import db_session
from data.categories import Category
from data.users import User
from data.articles import Article
from data.images import Image
from data.comments import Comment
from data.comment_votes import CommentVote


# --- DB Setup ---
db_session.global_init("db/site.db")


# --- Utility Functions ---


def with_session(func):
    """Decorator to automatically manage session lifecycle."""
    def wrapper(*args, **kwargs):
        session = db_session.create_session()
        try:
            return func(*args, session=session, **kwargs)
        finally:
            session.close()
    return wrapper


# --- Category Utilities ---


@with_session
def new_category(slug, title, description, session):
    category = Category(slug=slug, title=title, description=description)
    session.add(category)
    session.commit()
    return category


@with_session
def delete_category(category_id, session):
    category = session.query(Category).get(category_id)
    if not category:
        return False

    session.delete(category)
    session.commit()
    return True

# --- User Utilities ---


def get_users_by_usernames(usernames, db_sess):
    editors, missing = [], []

    for username in map(str.strip, usernames):
        user = db_sess.query(User).filter_by(username=username).first()
        (editors if user else missing).append(user or username)

    return [e for e in editors if isinstance(e, User)], missing


@with_session
def get_user_comment_karma(user_id, session):
    """Returns the total karma (sum of votes) for all comments authored by a user."""
    return (
        session.query(func.coalesce(func.sum(CommentVote.vote), 0))
        .join(Comment, CommentVote.comment_id == Comment.id)
        .filter(Comment.author_id == user_id)
        .scalar()
    )


# --- Article Utilities ---


def hotness(article: Article):
    """Calculate the 'hotness' score of an article."""
    if not article.published_date:
        return 0

    time_since_published = (datetime.now() - article.published_date).total_seconds()
    if time_since_published <= 0:
        return 0

    activity_score = (
        article.view_count * config.hotness_views_modifier +
        len(article.votes) * config.hotness_votes_modifier +
        len(article.comments) * config.hotness_comments_modifier
    )
    return activity_score / (time_since_published ** (1 / 7))


@with_session
def average_hotness(session):
    """Average hotness of all published articles."""
    articles = session.query(Article).filter_by(status='published').all()
    scores = [hotness(article) for article in articles]
    return sum(scores) / len(scores) if scores else 0


# --- Image Utilities ---


@with_session
def save_image(file, article_id, session):
    upload_dir = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    original_filename = secure_filename(file.filename)
    filename = Image.generate_unique_filename(original_filename)
    slug = uuid.uuid4().hex
    file_path = os.path.join(upload_dir, filename)

    file.save(file_path)

    image = Image(
        slug=slug,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        mime_type=file.content_type,
        article_id=article_id
    )
    session.add(image)
    session.commit()

    return session.query(Image).get(image.id)


@with_session
def delete_image(image_id, session):
    image = session.query(Image).get(image_id)
    if not image:
        return False

    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    session.delete(image)
    session.commit()
    return True


@with_session
def set_featured_image(article_id, image_id, session):
    article = session.query(Article).get(article_id)
    image = session.query(Image).get(image_id)

    if not article or not image or image.article_id != article_id:
        return False

    article.featured_image_url = image.url
    session.commit()
    return True
