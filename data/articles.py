import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    # --- Основные идентификаторы ---
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # URL-дружественная строка (слаг)
    slug = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)

    # --- Содержимое статьи ---
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)  # Заголовок
    subtitle = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)  # Подзаголовок
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # Основной текст статьи
    featured_image_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # URL главного изображения

    # --- Авторство и связи ---
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False, index=True)
    # Связь с моделью User.
    author = orm.relationship('User', back_populates='articles')
    # Связь с комментариями к этой статье.
    comments = orm.relationship('Comment', back_populates='article', cascade='all, delete-orphan')

    # --- Метаданные и статус ---
    created_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True),
                                     default=lambda: datetime.datetime.now(timezone.utc))
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True),
                                     default=lambda: datetime.datetime.now(timezone.utc),
                                     onupdate=lambda: datetime.datetime.now(timezone.utc))
    # Дата фактической публикации (может отличаться от created_date, если есть черновики/отложенная публикация)
    published_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True, index=True)

    # 'draft', 'published', 'archived', 'pending_review'
    status = sqlalchemy.Column(sqlalchemy.String, default='draft', nullable=False, index=True)
    content_type = sqlalchemy.Column(sqlalchemy.String, default='article', nullable=False, index=True)
    # 'article', 'blog_post'

    # --- Дополнительные поля ---
    view_count = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)  # Счетчик просмотров
    tags = orm.relationship('Tag', back_populates='articles')

    def __repr__(self):
        return f'<Article id={self.id} title="{self.title}" slug="{self.slug}">'