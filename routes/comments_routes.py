from flask import Blueprint, render_template, redirect, url_for, flash, request
from data import db_session
from flask_login import login_required, current_user

from data.comments import Comment
from data.comment_votes import CommentVote

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/comments/<int:comment_id>/vote', methods=['POST'])
@login_required
def vote_comment(comment_id):
    db_sess = db_session.create_session()
    vote_type = request.form.get('vote_type')  # 'upvote' or 'downvote'
    vote_value = 1 if vote_type == 'upvote' else -1

    comment = db_sess.query(Comment).get(comment_id)

    existing_vote = db_sess.query(CommentVote).filter_by(user_id=current_user.id, comment_id=comment.id).first()
    if existing_vote:
        if existing_vote.vote == vote_value:
            db_sess.delete(existing_vote)  # Toggle off
        else:
            existing_vote.vote = vote_value  # Change vote
    else:
        new_vote = CommentVote(comment=comment, user_id=current_user.id, vote=vote_value)
        db_sess.add(new_vote)

    db_sess.commit()
    db_sess.close()
    return redirect(url_for('article.article_detail', article_id=comment.article_id))
