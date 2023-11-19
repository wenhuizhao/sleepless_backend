import os
from dotenv import load_dotenv
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

load_dotenv()
engine = db.create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

def create_user(name, email, avatar=None):
    from users import User
    user = User(name=name, email=email, avatar=avatar)
    session.add(user)
    session.commit()

def find_user_by_email(email):
    from users import User
    user = User.query.filter_by(email=email).first()
    return user