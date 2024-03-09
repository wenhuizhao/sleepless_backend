import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ""))#from flask_script import Manager

from app import app

if __name__ == "__main__":
    app.run()
