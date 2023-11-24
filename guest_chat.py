
from gpt import get_qa_chain
from chat_history import chat_history

def guest_ask(guest, question):
    qa = get_qa_chain()
    result = qa({
        "question": question,
        "chat_history": chat_history(guest=guest)
    })
#    for h in chat_history(guest=guest):
#        print(f"chat_history:{h}")
    return result["answer"]
