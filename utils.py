from data import db_session
from data.categories import Category
from data.users import User
from data.articles import Article
from datetime import datetime

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
