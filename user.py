
#from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from database import db 
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    avatar = db.Column(db.String())
    timezone = db.Column(db.String())
    data = db.Column(JSONB)
    thread_id = db.Column(db.String())
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, name, email, avatar, data=None):
        self.name = name
        self.email = email
        self.avatar = avatar
        self.data = None

    def chronic_insomnia(self):
        if self.data and 'sleep_problem_duration' in self.datat:
            return self.data['sleep_problem_duration'] == 'long_term'
        else:
            return False

    def __repr__(self):
        return '<id {}>'.format(self.id)