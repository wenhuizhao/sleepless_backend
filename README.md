## How to set up
clone the code
install postgres
create .env file with content
```
DB_NAME=sleeplesschat
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sleepless_chat
APP_SETTINGS=config.DevelopmentConfig
GOOGLE_CLIENT_ID=278046306620-mjbbfgrnug0cl80np6ak9u89siug6aol.apps.googleusercontent.com
SECRET_KEY=
ALGORITHM=HS256
PROJECT_ID=
BACKEND_URL=http://127.0.0.1:5000
FRONTEND_URL=http://localhost:3000
OPENAI_API_KEY=
```

## How to run
`pip3  install -r requirements.txt`
`python3 manager.py db migrate`
`python3 manager.py db upgrade`
`python3 app.py`

