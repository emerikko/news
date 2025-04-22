import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    # --- Идентификация и аутентификация ---
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    # --- Метаданные и статус аккаунта ---
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    last_seen_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now(datetime.timezone.utc),
                                       onupdate=datetime.datetime.now(datetime.timezone.utc))
    email_verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    account_status = sqlalchemy.Column(sqlalchemy.String, default='pending', nullable=False, index=True)
    # Возможные статусы: active, pending, suspended, deleted

    # --- Роль и права доступа ---
    role = sqlalchemy.Column(sqlalchemy.String, default='user', nullable=False, index=True)
    # Возможные роли: admin, editor, author, moderator, user

    # --- Дополнительная информация профиля (опционально) ---
    about_me = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    profile_picture_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    location = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    website_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # --- Персональные данные (опционально) ---
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pseudonym = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    # --- Настройки приватности ---
    show_first_name = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    show_last_name = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    show_email = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    show_phone = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    show_location = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    show_birthday = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)
    show_gender = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)

    # --- Связи с другими моделями (ORM) ---
    edited_articles = orm.relationship('Article', secondary='article_editors', back_populates='editors')
    # Связь с редактируемыми статьями
    articles = orm.relationship("Article", back_populates="author")  # Связь со статьями пользователя
    comments = orm.relationship("Comment", back_populates="author")  # Связь с комментариями пользователя
