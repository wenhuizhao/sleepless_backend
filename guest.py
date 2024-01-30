
#from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from database import db 
from sqlalchemy.sql import func

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    thread_id = db.Column(db.String())
    data = db.Column(JSONB)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, name, data=None):
        self.name = name
        self.data = None

    def chronic_insomnia(self):
        if self.data and 'sleep_problem_duration' in self.data:
            return self.data['sleep_problem_duration'] == 'long_term'
        else:
            return False

    def __repr__(self):
        return '<id {}>'.format(self.id)