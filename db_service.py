import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from database import db
from users import User
from users import User

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