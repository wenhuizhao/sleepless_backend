from prompt_base import unknown_sleep_problem_duration_prompt, short_term_sleep_problem_prompt, long_term_sleep_problem_unknown_habit_prompt, \
    long_term_sleep_problem_fixed_habit_prompt, long_term_sleep_problem_nofixed_habit_prompt
from prompt_helper import add_question_chat_history

def get_guest_prompt(question, guest, history_messages=[]):
    print(f"get_prompt guest.data: {guest.data}")

    if guest and guest.data and guest.data.get('sleep_problem_duration') == 'long_term':
        print("long term")
        if guest.data and guest.data.get('sleep_habit') == 'same_time_every_day':
            prompt = long_term_sleep_problem_fixed_habit_prompt()
            prompt += f"""
            Ask he user if he want to try the six week sleep program. From user's answer if you know
            user agree to try the six week program, tell the user he need to login so that we can
            remember his progress when he come back to chat. Call function user_login with no arguments to show login button.
            """
        elif guest.data and guest.data.get('sleep_habit') == 'not_fixed':
            prompt =  long_term_sleep_problem_nofixed_habit_prompt()
            prompt += f"""
            Ask he user if he want to try the six week sleep program. From user's answer if you know
            user agree to try the six week program, tell the user he need to login so that we can
            remember his progress when he come back to chat. Call function user_login with no arguments to show login button.
            """

        else:
            prompt = long_term_sleep_problem_unknown_habit_prompt()

    elif guest.data and guest.data.get('sleep_problem_duration') == 'short_term':
        print("shortterm")
        prompt = short_term_sleep_problem_prompt()
    else:
        prompt = unknown_sleep_problem_duration_prompt()    

    prompt += f"""
    if the user agrees to join the six-week program, ask them to log in
    """
    print(f"guest prompt: {prompt}")
    return add_question_chat_history(prompt, question, history_messages)

