from chat_history import chat_history
from answer_post_process import process_answer
from openai_chat import ask_question
from db_service import user_today_message_count

DAILY_MESSAGE_LIMIT = 18

def user_ask(user, question):
    if user_today_message_count(user) > DAILY_MESSAGE_LIMIT:
        return {"answers": "You have exceeded your daily limit. Please become a member to gain unlimited messages.", "meta": {}}
    
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


