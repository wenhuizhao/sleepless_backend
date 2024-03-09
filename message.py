
import enum
from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from database import db 

class MessageType(enum.Enum):
    USER = 1
    BOT = 2

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    text = db.Column(db.String())
    guest = db.Column(db.String(), index=True)
    type = db.Column(Enum(MessageType))
    attributes = db.Column(JSONB)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user = db.relationship("User", backref="messages")
 
    def __init__(self, text, type, user_id=None, guest=None, attributes=None):
        self.user_id = user_id
        self.text = text
        self.guest = guest
        self.type = type
        self.attributes = attributes

    def with_sender(self):
        sender = "user:" if self.type == MessageType.USER else "chatbot:"
        return f"{sender} {self.text}"
    
    def __repr__(self):
        return '<id {}>'.format(self.id)