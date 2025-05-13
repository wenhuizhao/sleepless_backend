
#from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from database import db 
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

class PodcastItem(db.Model, SerializerMixin):
    __tablename__ = 'podcast_items'
    serialize_only = ('id', 'user_id', 'podcast_id', 'title',  'description', 'url', 'duration', 'type', 'guid', 'time_created')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    podcast_id = db.Column(db.Integer, db.ForeignKey("podcasts.id"), index=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    url = db.Column(db.String())
    duration = db.Column(db.Integer)
    type = db.Column(db.String())
    guid = db.Column(db.String(), index=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    podcast = db.relationship("Podcast", back_populates="items")

    def __init__(self, user_id, podcast_id, title, description, url, duration, type):
        self.user_id = user_id
        self.podcast_id = podcast_id
        self.title = title
        self.description  = description 
        self.url = url
        self.duration = duration
        self.type = type

    def __repr__(self):
        return '<id {}>'.format(self.id)