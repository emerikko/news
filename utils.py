import config
from data import db_session
from data.categories import Category
from data.users import User
from data.articles import Article
from data.images import Image
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

db_session.global_init("db/site.db")


def new_category(slug, title, description):
    db_sess = db_session.create_session()
    category = Category(slug=slug, title=title, description=description)
    db_sess.add(category)
    db_sess.commit()
    db_sess.close()
    return category


def get_users_by_usernames(usernames, db_sess):
    """Helper function to fetch users by their usernames."""
    editors = []
    missing_editors = []

    for username in usernames:
        user = db_sess.query(User).filter(User.username == username.strip()).first()
        if user:
            editors.append(user)
        else:
            missing_editors.append(username.strip())

    return editors, missing_editors


def hotness(article: Article):
    if not article.published_date:
        return 0
    time_from_publish = (datetime.now() - article.published_date).total_seconds() // 60
    return article.view_count / time_from_publish if time_from_publish > 0 else 0


def average_hotness():
    db_sess = db_session.create_session()
    ans = 0
    hots = [hotness(q) if q.status == 'published' else None for q in db_sess.query(Article).all()]
    db_sess.close()
    for i in hots:
        if i:
            ans += i
    if len(hots) == 0:
        return 0
    return ans / len(hots)


def get_user_comment_karma(user_id, session):
    """Returns the total karma (sum of votes) for all comments authored by a user."""
    from sqlalchemy import func
    from data.comments import Comment
    from data.comment_votes import CommentVote

    return (
        session.query(func.coalesce(func.sum(CommentVote.vote), 0))
        .join(Comment, CommentVote.comment_id == Comment.id)
        .filter(Comment.author_id == user_id)
        .scalar()
    )


# TODO: Add more useful/admin functions

def save_image(file, article_id):
    upload_folder = os.path.join(current_app.static_folder, 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    original_filename = secure_filename(file.filename)
    filename = Image.generate_unique_filename(original_filename)
    slug = uuid.uuid4().hex
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    db_sess = db_session.create_session()
    image = Image(
        slug=slug,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        mime_type=file.content_type,
        article_id=article_id
    )
    db_sess.add(image)
    db_sess.commit()
    
    image_id = image.id
    db_sess.close()
    
    db_sess = db_session.create_session()
    image = db_sess.query(Image).get(image_id)
    db_sess.close()
    
    return image


def delete_image(image_id):
    db_sess = db_session.create_session()
    image = db_sess.query(Image).get(image_id)
    
    if not image:
        db_sess.close()
        return False
    
    try:
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    db_sess.delete(image)
    db_sess.commit()
    db_sess.close()
    
    return True

def set_featured_image(article_id, image_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    image = db_sess.query(Image).get(image_id)
    
    if not article or not image or image.article_id != article_id:
        db_sess.close()
        return False
    
    article.featured_image_url = image.url
    db_sess.commit()
    db_sess.close()
    
    return True
