import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    # --- Основные идентификаторы ---
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    # --- Содержимое статьи ---
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)  # Заголовок
    subtitle = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Подзаголовок
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=True)  # Основной текст статьи
    summary = sqlalchemy.Column(sqlalchemy.Text, nullable=True)  # Краткое содержание
    featured_image_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # URL главного изображения

    # --- Авторство и связи ---
    # Связь с моделью User.
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    author = orm.relationship('User', back_populates='articles')
    editors = orm.relationship('User', secondary='article_editors', back_populates='edited_articles')
    # Связь с комментариями к этой статье.
    comments = orm.relationship('Comment', back_populates='article', cascade='all, delete-orphan')
    # Связь с категориями.
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'), nullable=False)
    category = orm.relationship('Category', back_populates='articles')

    # --- Метаданные и статус ---
    created_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True),
                                     default=lambda: datetime.datetime.now(timezone.utc))
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True),
                                     default=lambda: datetime.datetime.now(timezone.utc),
                                     onupdate=lambda: datetime.datetime.now(timezone.utc))
    # Дата фактической публикации (может отличаться от created_date, если есть черновики/отложенная публикация)
    published_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)

    # 'draft', 'published', 'archived', 'pending_review'
    status = sqlalchemy.Column(sqlalchemy.String, default='draft', nullable=False)
    # 'article', 'blog_post'
    content_type = sqlalchemy.Column(sqlalchemy.String, default='article', nullable=False)
    # any
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # --- Дополнительные поля ---
    view_count = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    votes = orm.relationship("ArticleVote", back_populates="article", cascade="all, delete-orphan")

    # TODO add view counter

    @property
    def vote_score(self):
        return sum(v.vote for v in self.votes)

    def get_user_vote(self, user_id):
        vote = next((v for v in self.votes if v.user_id == user_id), None)
        return vote.vote if vote else 0