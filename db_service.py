import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from database import db
from user import User
from message import Message

load_dotenv()
engine = db.create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

def create_user(name, email, avatar=None):
    user = User(name=name, email=email, avatar=avatar)
    session.add(user)
    session.commit()

def find_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    return user

def create_message(user, text, type, guest=None):
    if user:
        message = Message(user_id=user.id, text=text, type=type)
    elif guest:
        message = Message(text=text, type=type, guest=guest)

    session.add(message)
    session.commit()

def messages_by_user_id(user_id):
    messages = Message.query.filter_by(user_id=user_id).all()
    return messages

def messages_by_guest(guest):
    messages = Message.query.filter_by(guest=guest).all()
    return messages
