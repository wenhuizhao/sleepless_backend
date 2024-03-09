
#from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from database import db 
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

class Blog(db.Model, SerializerMixin):
    __tablename__ = 'blogs'
    serialize_only = ('id', 'user_id', 'title', 'content', 'time_created')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, user_id, title, content):
        self.user_id = user_id
        self.title = title
        self.content = content

    def __repr__(self):
        return '<id {}>'.format(self.id)