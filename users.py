
from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
 
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    avatar = db.Column(db.String())

    def __init__(self, name, email, avatar):
        self.name = name
        self.email = email
        self.avatar = avatar

    def __repr__(self):
        return '<id {}>'.format(self.id)