from db_service import create_message
from message import MessageType
from guest_chat import guest_ask
from user_chat import user_ask
from anonymous_chat import anonymous_ask

BOT_USER_NAME = "chatbot"

def ask(question, user, guest_name):
    create_message(user=user, text=question, guest=guest_name, type=MessageType.USER)
    if user:
        response = user_ask(user, question)
    elif guest_name:
        response = guest_ask(guest_name, question)
    else:
        response = anonymous_ask(question)
    answers = response["answers"]
    meta = response["meta"]
    create_message(user=user, text=answers, guest=guest_name, type=MessageType.BOT)
    if meta.get('type') == 'user_login':
        message = {"message": answers, "sender": BOT_USER_NAME, "direction": "incoming", 
                   "attributes": {"type": 'user_login'}}
    else:
        message = {"message": answers, "sender": BOT_USER_NAME, "direction": "incoming"}
    return message