import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class ArticleVote(SqlAlchemyBase):
    __tablename__ = 'article_votes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'), nullable=False)
    vote = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # +1 or -1

    user = orm.relationship("User")
    article = orm.relationship("Article", back_populates="votes")

    __table_args__ = (
        sqlalchemy.UniqueConstraint('user_id', 'article_id', name='uix_user_article_vote'),
    )
