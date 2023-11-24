import json
from flask import Flask 
from flask.wrappers import Response
from flask.globals import request, session
import requests
from dotenv import load_dotenv
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os, pathlib
import google
import jwt
from flask_cors import CORS
from chat import ask
from chat_history import history_messages
from flask_sqlalchemy import SQLAlchemy
from database import db
from db_service import create_user, find_user_by_email

app = Flask(__name__)
load_dotenv()
CORS(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['Access-Control-Allow-Origin'] = '*'
app.config["Access-Control-Allow-Headers"]="Content-Type"
db.init_app(app)

# bypass http
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.secret_key = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client-secret.json")
algorithm = os.getenv("ALGORITHM")
BACKEND_URL=os.getenv("BACKEND_URL")
FRONTEND_URL=os.getenv("FRONTEND_URL")


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri=BACKEND_URL+"/callback",
)


# wrapper
def login_required(function):
    def wrapper(*args, **kwargs):
        encoded_jwt=request.headers.get("Authorization").split("Bearer ")[1]
        if encoded_jwt==None:
            return abort(401)
        else:
            return function()
    return wrapper


def Generate_JWT(payload):
    encoded_jwt = jwt.encode(payload, app.secret_key, algorithm=algorithm)
    return encoded_jwt


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request,
        audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")
    
    # removing the specific audience, as it is throwing error
    del id_info['aud']
    jwt_token=Generate_JWT(id_info)
    create_user(
        name = id_info.get('name'),
        email = id_info.get('email'),
        avatar = id_info.get('picture')
    )
    return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")
    """ return Response(
        response=json.dumps({'JWT':jwt_token}),
        status=200,
        mimetype='application/json'
    ) """


@app.route("/auth/google")
def login():
    authorization_url, state = flow.authorization_url()
    # Store the state so the callback can verify the auth server response.
    session["state"] = state
    return Response(
        response=json.dumps({'auth_url':authorization_url}),
        status=200,
        mimetype='application/json'
    )

@app.route("/logout", methods=["POST"])
def logout():
    #clear the local storage from frontend
    session.clear()
    return Response(
        response=json.dumps({"message":"Logged out"}),
        status=202,
        mimetype='application/json'
    )


@app.route("/home")
@login_required
def home_page_user():
    encoded_jwt=request.headers.get("Authorization").split("Bearer ")[1]
    try:
        decoded_jwt=jwt.decode(encoded_jwt, app.secret_key, algorithms=[algorithm,])
        #print(decoded_jwt)
    except Exception as e: 
        return Response(
            response=json.dumps({"message":"Decoding JWT Failed", "exception":e.args}),
            status=500,
            mimetype='application/json'
        )
    return Response(
        response=json.dumps(decoded_jwt),
        status=200,
        mimetype='application/json'
    )


@app.route("/chat_messages", methods=["GET"])
def chat_messages():
    current_user = get_current_user(request)
    args = request.args
    guest = args.get("guest")
    chat_messages = history_messages(current_user, guest)
    if current_user: print(current_user.email)
    return Response (
        response=json.dumps({"messages": chat_messages}),
        status=200,
        mimetype='application/json'
    )

@app.route("/message", methods=["POST"])
def send_message():
    body = request.json
    guest = body.get("guest")
    user = get_current_user(request)
    answer = ask(body.get("question"), user, guest)
    return Response (
        response = json.dumps({"answer": answer})
    )


@app.errorhandler(jwt.ExpiredSignatureError)
def special_exception_handler(error):
    return 'Token expired', 401

@app.errorhandler(Exception)
def all_exception_handler(error):
   print(error)
   return 'Error', 500

def get_current_user(request):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            encoded_jwt=request.headers.get("Authorization").split("Bearer ")[1]
            decoded_jwt=jwt.decode(encoded_jwt, app.secret_key, algorithms=[algorithm,])
            #print(decoded_jwt)
            current_user = find_user_by_email(decoded_jwt['email'])
            #print(current_user)
            return current_user
        return None
    except jwt.ExpiredSignatureError as e:
        raise e
    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
