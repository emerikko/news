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
    """Decorator to automatically manage session lifecycle.
    
    Creates a session, passes it to the decorated function, and ensures it's closed afterward.
    """
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
    """Create a new category.
    
    Args:
        slug: URL-friendly identifier
        title: Display name of the category
        description: Detailed description
        session: Database session (injected by decorator)
        
    Returns:
        The created Category object
    """
    category = Category(slug=slug, title=title, description=description)
    session.add(category)
    session.commit()
    return category


@with_session
def delete_category(category_id, session):
    """Delete a category by ID.
    
    Args:
        category_id: ID of the category to delete
        session: Database session (injected by decorator)
        
    Returns:
        True if successful, False if category not found
    """
    category = session.query(Category).get(category_id)
    if not category:
        return False

    session.delete(category)
    session.commit()
    return True


# --- User Utilities ---


def get_users_by_usernames(usernames, db_sess):
    """Find users by their usernames.
    
    Args:
        usernames: List or comma-separated string of usernames
        db_sess: Database session
        
    Returns:
        Tuple of (found_users, missing_usernames)
    """
    editors, missing = [], []

    for username in map(str.strip, usernames):
        user = db_sess.query(User).filter_by(username=username).first()
        (editors if user else missing).append(user or username)

    return [e for e in editors if isinstance(e, User)], missing


@with_session
def get_user_comment_karma(user_id, session):
    """Returns the total karma (sum of votes) for all comments authored by a user.
    
    Args:
        user_id: ID of the user
        session: Database session (injected by decorator)
        
    Returns:
        Total karma score (integer)
    """
    return (
        session.query(func.coalesce(func.sum(CommentVote.vote), 0))
        .join(Comment, CommentVote.comment_id == Comment.id)
        .filter(Comment.author_id == user_id)
        .scalar()
    )


# --- Article Utilities ---


def hotness(article: Article):
    """Calculate the 'hotness' score of an article.
    
    The score is based on views, votes, comments, and time since publication.
    
    Args:
        article: Article object
        
    Returns:
        Hotness score as a float
    """
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
    """Calculate average hotness of all published articles.
    
    Args:
        session: Database session (injected by decorator)
        
    Returns:
        Average hotness score as a float, or 0 if no articles
    """
    articles = session.query(Article).filter_by(status='published').all()
    scores = [hotness(article) for article in articles]
    return sum(scores) / len(scores) if scores else 0


# --- Image Utilities ---


@with_session
def save_image(file, article_id, session):
    """Save an uploaded image file and associate it with an article.
    
    Args:
        file: Uploaded file object
        article_id: ID of the article to associate with
        session: Database session (injected by decorator)
        
    Returns:
        The created Image object
    """
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
    """Delete an image by ID, removing both database record and file.
    
    Args:
        image_id: ID of the image to delete
        session: Database session (injected by decorator)
        
    Returns:
        True if successful, False if image not found
    """
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
    """Set an image as the featured image for an article.
    
    Args:
        article_id: ID of the article
        image_id: ID of the image to set as featured
        session: Database session (injected by decorator)
        
    Returns:
        True if successful, False if article or image not found or not associated
    """
    article = session.query(Article).get(article_id)
    image = session.query(Image).get(image_id)

    if not article or not image or image.article_id != article_id:
        return False

    article.featured_image_url = image.url
    session.commit()
    return True
