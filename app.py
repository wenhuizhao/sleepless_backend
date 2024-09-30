import json
from flask import Flask, jsonify 
from flask.wrappers import Response
from flask.globals import request, session
import requests
from dotenv import load_dotenv
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os, pathlib
import stripe
import google
import jwt
from flask_cors import CORS
from chat import ask
from chat_history import history_messages
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database import db
from db_service import alchemyencoder, create_user, find_user_by_email, all_blogs, create_blog, blog_by_id, \
    sync_guest_data_to_user, update_user_timezone, create_podcast_item, all_podcasts, podcast_by_id
from stripe_service import create_intent, handle_webhooks, create_subscription
from s3_util import upload_file_to_s3

app = Flask(__name__)
load_dotenv()
CORS(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['Access-Control-Allow-Origin'] = '*'
app.config["Access-Control-Allow-Headers"]="Content-Type"
db.init_app(app)
migrate = Migrate(app, db)

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


@app.route("/callback", methods=["GET"])
def callback():
    print ("callback")
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
    current_user = find_user_by_email(id_info.get('email'))
    new_user = "false"
    if not current_user:
        create_user(
            name = id_info.get('name'),
            email = id_info.get('email'),
            avatar = id_info.get('picture')
        )
        new_user = "true"
    return redirect(f"{FRONTEND_URL}?jwt={jwt_token}&new_user={new_user}")
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

@app.route("/sync_guest_user", methods=["POST"])
def sync_guest_user():
    body = request.json
    guest_name = body.get("guest")
    current_user = get_current_user(request)
    if (current_user and guest_name):
        sync_guest_data_to_user(guest_name, current_user)
    return Response(
        response=json.dumps({}),
        status=200,
        mimetype='application/json'
    )

@app.route("/sync_timezone_user", methods=["POST"])
def sync_timezone_user():
    body = request.json
    timezone = body.get("timezone")
    current_user = get_current_user(request)
    print(f"current_user {current_user}")
    update_user_timezone(timezone, current_user.email)
    return Response(
        response=json.dumps({}),
        status=200,
        mimetype='application/json'
    )

@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        body = request.json
        amount = body.get("amount")
        customer = body.get("customer")
        intent = create_intent(amount, customer)
        print(f"return intent:{intent}")
        return({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error = str(e)), 403
        
@app.route('/webhooks', methods=['POST'])
def check_payment():
    print("check payment")
    event = handle_webhooks(request)
      
    return jsonify(success=True)

@app.route("/prepare-subscription", methods=['POST'])
def prepare_subscription():
    current_user = get_current_user(request)
    if (current_user == None):
         return "permission denied", 401
    try:
        subscription = create_subscription(current_user)
        return jsonify(subscriptionId=subscription.id, clientSecret=subscription.latest_invoice.payment_intent.client_secret)
    except Exception as e:
        return jsonify(error = {'message': e.user_message}), 400

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
    page = args.get('page', 1, type=int)
    guest = args.get("guest")
    messages_page = history_messages(current_user, guest, page)
    #if current_user: print(current_user.email)
    return Response (
        response=json.dumps({
            "page": messages_page.page,
            "per_page": messages_page.per_page,
            "items": messages_page.items,
            "total": messages_page.total,
            "has_next": messages_page.has_next
        }),
        status=200,
        mimetype='application/json'
    )

@app.route("/message", methods=["POST"])
def send_message():
    body = request.json
    guest_name = body.get("guest")
    user = get_current_user(request)
    answer = ask(body.get("question"), user, guest_name)
    return Response (
        response = json.dumps({"answer": answer})
    )

@app.route("/blogs", methods=["GET"])
def get_blogs():
    blogs_data = all_blogs()
    blogs = [r.to_dict(only=('id', 'title', 'time_created')) for r in blogs_data]
    return Response(
        response = json.dumps(blogs, default=alchemyencoder)
    )

@app.route("/blog/<blog_id>", methods=["GET"])
def get_blog(blog_id):
    blog_data = blog_by_id(blog_id)
    return Response(
        response = json.dumps(blog_data.to_dict())
    )

@app.route("/blog", methods=["POST"])
def add_blog():
    body = request.json
    user = get_current_user(request)
    if user and user.isAdmin():
        create_blog(user, body.get("title"), body.get("content"))
        return Response (
            response = json.dumps({})
        )
    else:
        return "permissoin denied", 401

@app.route("/podcast_item", methods=["POST"])
def add_podcast():
    body = request.json
    user = get_current_user(request)
    if user and user.isAdmin():
        create_podcast_item(user=user, podcast_id=body.get("podcast_id"), title=body.get("title"),
                             description=body.get("description"), url=body.get("url"), duration=body.get("duration"),
                             type=body.get('type'))
        return Response (
            response = json.dumps({})
        )
    else:
        return "permissoin denied", 401

@app.route("/podcasts", methods=["GET"])
def get_podcasts():
    podcasts_data = all_podcasts()
    podcasts = [r.to_dict(only=('id', 'title', 'subtitle', 'description', 'link', 'items')) for r in podcasts_data]
    return Response(
        response = json.dumps(podcasts, default=alchemyencoder)
    )

@app.route("/rss", methods=["GET"])
def rss():
    podcasts_data = all_podcasts()
    podcast_id = [r.to_dict(only=('id', 'title', 'time_created')) for r in podcasts_data][0]["id"]
    podcast = podcast_by_id(podcast_id)
    return Response(podcast.rss(), mimetype='application/rss+xml')

@app.route("/upload_file", methods=["POST"])
def upload_file():
    user = get_current_user(request)
    if not user or not user.isAdmin():
        return "permission denied", 401
    
    if 'file' not in request.files:
        return "empty file", 400
    file = request.files['file']

    # check whether a file is selected
    if file.filename == '':
        return "no file chosen", 400

    # check whether the file extension is allowed (eg. png,jpeg,jpg,gif)
    if file and allowed_file(file.filename):
        output = upload_file_to_s3(file) 
        
        # if upload success,will return file name of uploaded file
        if output:
            return Response (
                response=json.dumps({
                    "file": output
                }),
                status=200,
                mimetype='application/json'
            )
        else:
            return "error", 500       
    # if file extension not allowed
    else:
        return "wrong file format", 400

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
            print(decoded_jwt)
            current_user = find_user_by_email(decoded_jwt['email'])
            #print(current_user)
            return current_user
        return None
    except jwt.ExpiredSignatureError as e:
        raise e
    except Exception as e:
        print(e)
        return None

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'}
# function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True, port=4000, host="0.0.0.0")
