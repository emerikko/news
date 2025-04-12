import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    # --- Основные идентификаторы ---
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    slug = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True, nullable=False)

    # --- Данные ---
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    # --- Связи ---
    # Связь с моделью Article
    articles = orm.relationship('Article', back_populates='category', cascade='all, delete-orphan')


