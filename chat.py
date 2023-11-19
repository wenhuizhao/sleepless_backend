
BOT_USER = "chatbot"

def history_messages(user):
    messages = [
        {"text": "message one", "user": { "id": "user1", "name": "user1"}, "type": "incoming"},
        {"text": "message two", "user": { "id": "user2", "name": "user2"}, "type": "outgoing"}
    ]
    return messages

def ask(question, user):
    answer = f"answer to: {question}"
    message = {"text": answer, "user": { "id": "BOT_USER", "name": BOT_USER }, "type": "incoming"}
    return message