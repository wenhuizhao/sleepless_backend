
from gpt import get_qa_chain

def anonymous_ask(question):
    qa = get_qa_chain()
    result = qa({
        "question": question,
        "chat_history": []
    })
    return result["answer"]
