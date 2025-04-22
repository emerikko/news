import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=datetime.datetime.now(timezone.utc))
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False, index=True)
    author = orm.relationship('User', back_populates='comments')
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'), nullable=False, index=True)
    article = orm.relationship('Article', back_populates='comments')
    votes = orm.relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")

    @property
    def vote_score(self):
        return sum(v.vote for v in self.votes)

    def get_user_vote(self, user_id):
        vote = next((v for v in self.votes if v.user_id == user_id), None)
        return vote.vote if vote else 0
