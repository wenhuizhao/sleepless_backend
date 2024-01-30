from message import Message, MessageType
from datetime import datetime, timezone, timedelta

SESSION_IN_HOURS = 4

def guest_welcome_messages(guest, messages):
    #if latest_message_in_session(messages):
    if len(messages) > 2:
        return None
        #return Message(text=guest_welcome_text(guest), type=MessageType.BOT, guest=guest)
    else:
        message = Message(
            text = base_welcome_text(),
            type = MessageType.BOT,
            guest = guest,
            attributes = base_welcome_attributes()
        )
        return message

def user_welcome_message(user, messages):
    if latest_message_in_session(messages):
        None
    else:
        message = Message(text = "welcome", type = MessageType.BOT, user_id = user.id)
        return message    

def anonymous_welcome_message():
    message = Message(text = base_welcome_text(), type = MessageType.BOT, attributes=base_welcome_attributes())
    return message


def latest_message_in_session(messages):
    if len(messages) == 0 or datetime.now(timezone.utc) - messages[0].time_created > timedelta(hours=SESSION_IN_HOURS):
        return False
    else:
        return True
    
def base_welcome_text():
    return """Hello, I am sleep assistant agent. Do you have sleep problem? You can click the following buttons"""

def base_welcome_attributes():
    return {
        "type": "picklist",
        "lists": [
            "I have trouble fall asleep",
            "I am afraid I can't hava good sleep tonight?",
            "How can I improve my sleep tonight?",
            "Will my health decline if I can't get good sleep?"
        ]
    }

def guest_welcome_text(guest):
    return """
    Welcome back. How is your sleep last night?
    """
def user_welcome_text(user):
    return """Welcome back. How is your sleep last night"""
