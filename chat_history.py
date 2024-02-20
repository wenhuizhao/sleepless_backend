from db_service import messages_by_user_id, messages_by_guest, save_message
from message import MessageType
from welcome_message import guest_welcome_messages, user_welcome_message, anonymous_welcome_message

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

def message_avatar(message):
    if  message.type == MessageType.USER and message.user and message.user.avatar:
        return message.user.avatar
    

def transfer_message(message):
    return {
        "message": message.text,
        "sender": message_user_name(message),
        "direction": "outgoing" if message.type == MessageType.USER else "incoming",
        "avatar": message_avatar(message),
        "attributes": message.attributes
    }

def load_messages(user, guest_name, save_welcome=False, page=1):
    if user:
        messages_page = messages_by_user_id(user.id, page)
        print('load_messages')
        welcome_message = user_welcome_message(user, messages_page.items)
        print(f'welcome message, {welcome_message}')
    elif guest_name:
        messages_page = messages_by_guest(guest_name, page)
        welcome_message = guest_welcome_messages(guest_name, messages_page.items)
    else:
        messages_page = messages_by_guest("none", page)
        welcome_message = anonymous_welcome_message()
    #print(f"loadmessage, page={page}, message_page.len:{len(messages_page.items)}, welcome_message:{welcome_message}")
    if page == 1 and welcome_message:
        print ('append welcome message')
        messages_page.items.append(welcome_message)
        if user or guest_name:
            save_message(welcome_message)
    #print(f"messagePage:{len(messages_page.items)}")
    return messages_page

# return history message in format expected by front end
def history_messages(user=None, guest_name=None, page=1):
    messages_page = load_messages(user, guest_name, True, page)
    messages_page.items = list(map(transfer_message, messages_page.items))
    return messages_page

# return chat history in format expected by langchain chat_history 
def chat_history(user=None, guest_name=None):
    messages = load_messages(user, guest_name).items
    result = list(map(lambda m: m.with_sender(),  messages))
    return result

