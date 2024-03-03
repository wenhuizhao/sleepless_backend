import os
from app import create_app, db
from user import User
from guest import Guest
from message import Message
from sleep_diary import SleepDiary
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Guest=Guest, Message=Message,
                SleepDiary=SleepDiary)