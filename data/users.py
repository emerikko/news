import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    # --- Идентификация и аутентификация ---
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    # --- Отображаемые данные пользователя ---
    first_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pseudonym = sqlalchemy.Column(sqlalchemy.String, index=True)

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

    # --- Настройки пользователя (опционально) ---
    settings = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)  # Хранение различных настроек в формате JSON

    # --- Связи с другими моделями (ORM) ---
    articles = orm.relationship("Article", back_populates="author")  # Связь со статьями пользователя
    comments = orm.relationship("Comment", back_populates="author")  # Связь с комментариями пользователя
