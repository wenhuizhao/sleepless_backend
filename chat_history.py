from db_service import messages_by_user_id, messages_by_guest
from message import MessageType

BOT_USER_ID = "001"
BOT_USER_NAME = "chatbot"

def message_user_id(message):
    if message.type == MessageType.BOT:
        return BOT_USER_ID
    else:
        if message.user:
            return message.user.id
        elif message.guest:
            return message.guest
        else:
            return ""

def message_user_name(message):
    if message.type == MessageType.BOT:
        return BOT_USER_NAME
    else:
        if message.user:
            return message.user.name
        elif message.guest:
            return message.guest
        else:
            return ""

def transfer_message(message):
    return {
        "text": message.text,
        "user": {
            "id": message_user_id(message),
            "name": message_user_name(message)
        },
        "type": "outgoing" if message.type == MessageType.USER else "incoming"
    }


def chat_messages(user, guest):
    if user:
        messages = messages_by_user_id(user.id)
    elif guest:
        messages = messages_by_guest(guest)
    else:
        messages = []
    return messages

# return history message in format expected by front end
def history_messages(user=None, guest=None):
    messages = chat_messages(user, guest)
    return list(map(transfer_message, messages))

# return chat history in format expected by langchain chat_history 
def chat_history(user=None, guest=None):
    messages = chat_messages(user, guest)
    return list(map(lambda m: m.with_sender(),  messages))

