import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ""))#from flask_script import Manager

#from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app
from database import db 

from user import User
from message import Message
from guest import Guest
from sleep_diary import SleepDiary

# app.config.from_object(os.environ['APP_SETTINGS'])
# #db.init_app(app)

# migrate = Migrate(app, db)
# manager = Manager(app)

# manager.add_command('db', MigrateCommand)


# if __name__ == '__main__':
#     manager.run()

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Message=Message, Guest=Guest,
                SleepDiary=SleepDiary)