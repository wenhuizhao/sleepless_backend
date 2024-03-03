
from chat_history import chat_history
from prompt_base import first_prompt
from answer_post_process import process_answer
from db_service import find_guest_by_name, create_guest
from openai_chat import ask_question

def guest_ask(guest_name, question):
    history_messages = chat_history(guest_name=guest_name)
    guest = find_guest_by_name(guest_name)
    if not guest:
        guest = create_guest(guest_name)
    #for m in history_messages: print(m)
    new_session = False
    if len(history_messages) <= 2:
        new_session = True
    data = ask_question(question=question, guest=guest, new_session=new_session, history_messages=history_messages)
    answers = data["answers"]
    meta = data["meta"]
    processed_answer = process_answer(answers)
    print(f"guest_ask, answer:{processed_answer}")
    return { "answers": answers, "meta": meta}

