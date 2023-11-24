from gpt import get_qa_chain
from chat_history import chat_history

def user_ask(question):
    qa = get_qa_chain()
    result = qa({
        "question": question,
        "chat_history": chat_history(guest=guest)
    })
    return result["answer"]

