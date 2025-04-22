from .db_session import SqlAlchemyBase
import datetime
from datetime import timezone
import sqlalchemy
from sqlalchemy import orm
import os
import uuid


class Image(SqlAlchemyBase):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    slug = sqlalchemy.Column(sqlalchemy.String(120), unique=True, nullable=False)
    filename = sqlalchemy.Column(sqlalchemy.String(120), unique=True, nullable=False)
    original_filename = sqlalchemy.Column(sqlalchemy.String(120), nullable=False)
    file_path = sqlalchemy.Column(sqlalchemy.String(255), nullable=False) 
    mime_type = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)

    uploaded_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=datetime.datetime.now(timezone.utc))

    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'), nullable=False)
    article = orm.relationship('Article', back_populates='images')
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate a unique filename for storing the image."""
        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4().hex}{ext}"
    
    @property
    def url(self):
        """Return the URL to access this image."""
        return f"/static/uploads/{self.filename}"
