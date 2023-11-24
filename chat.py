from db_service import create_message, messages_by_user_id, messages_by_guest
from message import MessageType
from guest_chat import guest_ask
from user_chat import user_ask
from anonymous_chat import anonymous_ask

BOT_USER_NAME = "chatbot"

def ask(question, user, guest):
    create_message(user=user, text=question, guest=guest, type=MessageType.USER)
    if user:
        answer = user_ask(user, question)
    elif guest:
        answer = guest_ask(guest, question)
    else:
        answer = anonymous_ask(question)

    create_message(user=user, text=answer, guest=guest, type=MessageType.BOT)
    message = {"text": answer, "user": { "id": "BOT_USER", "name": BOT_USER_NAME }, "type": "incoming"}
    return message