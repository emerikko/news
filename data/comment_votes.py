import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class CommentVote(SqlAlchemyBase):
    __tablename__ = 'comment_votes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    comment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('comments.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    vote = sqlalchemy.Column(sqlalchemy.Integer)

    comment = orm.relationship("Comment", back_populates="votes")
    user = orm.relationship("User")

    __table_args__ = (
        sqlalchemy.UniqueConstraint('comment_id', 'user_id', name='_user_comment_vote_uc'),
    )
