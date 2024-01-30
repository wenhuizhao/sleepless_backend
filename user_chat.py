from gpt import get_qa_chain
from chat_history import chat_history
from answer_post_process import process_answer
from openai_chat import ask_question

def user_ask(user, question):
    history_messages = chat_history(user=user)
    new_session = False
    if len(history_messages) <= 2:
        new_session = True
    data = ask_question(question=question, user=user, new_session=new_session, history_messages=history_messages)
    answers = data["answers"]
    meta = data["meta"]
    processed_answer = process_answer(answers)
    #print(f"guest_ask, answer:{processed_answer}")
    return { "answers": answers, "meta": meta}


