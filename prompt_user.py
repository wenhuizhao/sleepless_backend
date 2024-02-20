from datetime import datetime, timezone
import dateutil.parser
from prompt_base import unknown_sleep_problem_duration_prompt, short_term_sleep_problem_prompt, long_term_sleep_problem_unknown_habit_prompt, \
    long_term_sleep_problem_fixed_habit_prompt, long_term_sleep_problem_nofixed_habit_prompt
from db_service import find_sleep_diary_by_user_id_day, find_sleep_diaries_by_user_id
from prompt_helper import add_question_chat_history
from functools import reduce
from date_util import days_in_program

def get_user_prompt(question, user, history_messages=[]):
    chat_history = "\n".join(history_messages)
    print(f"get_user_prompt user.data: {user.data}")

    if user.data and user.data.get('six_week_program_start_time'):
        prompt = get_user_prompt_in_six_week_program(user, question, history_messages)

    elif user.data and  user.data.get('sleep_problem_duration') == 'long_term':
        print("long term")
        if user.data and user.data.get('sleep_habit') == 'same_time_everyday':
            prompt = long_term_sleep_problem_fixed_habit_prompt()
        elif user.data and user.data.get('sleep_habit') == 'not_fixed':
            prompt = long_term_sleep_problem_nofixed_habit_prompt()
        else:
            prompt = long_term_sleep_problem_unknown_habit_prompt()

    elif user.data and  user.data.get('sleep_problem_duration') == 'short_term':
        print("shortterm")
        prompt = short_term_sleep_problem_prompt()
    else:
        prompt = unknown_sleep_problem_duration_prompt()

    print(f"user prompt: {prompt}")
    return add_question_chat_history(prompt, question, history_messages)

def get_user_prompt_in_six_week_program(user, question, history_messages=[]):
    program_start_time_str = user.data['six_week_program_start_time']
    print(f"user progam start at:{program_start_time_str}")
    program_start_time = dateutil.parser.isoparse(program_start_time_str)
    days = days_in_program(user, program_start_time)
    #days = (datetime.now(timezone.utc) - program_start_time).days
    sleep_diary = find_sleep_diary_by_user_id_day(user.id, days)
    sleep_diary_history = user_sleep_diary_history(user)
    if sleep_diary:
        prompt = f"""
        The user is in the six week program. Today is the number {days} days in the program.
        You already collected users sleep diary for yesterday. Here is user's sleep diary for yesterday:
        {sleep_diary.to_s()}
        Answer user's questions based on his sleep diary history:
        {sleep_diary_history}
        """
    else:
        prompt = user_sleep_program_day_prompt(days)
    return add_question_chat_history(prompt, question, history_messages)

def user_welcome_message_content(user):
    sleep_diaries = find_sleep_diaries_by_user_id(user.id).items
    program_start_time_str = user.data['six_week_program_start_time']
    program_start_time = dateutil.parser.isoparse(program_start_time_str)
    days = days_in_program(user, program_start_time)
    welcome_message = f"""Welcome back, {user.name}. This is Day {days} of your sleep improvement program. """

    diary_entry = list(filter(lambda x: x.day == days, sleep_diaries))
    if diary_entry:
        return welcome_message
    else:
        print ('hello fatso 2')
        return welcome_message + f"""As part of the program, I'd like to hear about how you slept yesterday. Is that okay?"""

def user_sleep_program_day_prompt(days):
    return f"""
        The user is in the six week program. Today is the number {days} days in the program. 
        Collect the following information from the user:
        1. time the user get into bed last night,
        2. time the user turned off light last night,
        3. time it takes for the user to fall asleep last night,
        4. number of times the user wake up last night,
        5. time lasted for each wakeup last night,
        6. time the user wakeup this morning,
        7. time the user get off bed this morning,
        8. sleep quality last night on a 0-10 scale (10 being the best, 0 being the worst).
        9. negative sleep thought last night. for example: I'm stressed that if don't fall asleep, tomorrow will be terrible.
        10. positive sleep thought last night for example: I feel good today. I will sleep well.
        Ask the user one question at a time and collect all the answers. When all the answers are collected,
        call function update_sleep_diary with arguments last_night_get_into_bed_time,  last_night_turn_off_light_time,
        last_night_time_to_fall_asleep_in_minutes, last_night_number_of_times_wakeup,
        last_night_each_wakeup_time_in_minutes, this_morning_wakeup_time, this_morning_get_out_of_bed_time,
        last_night_sleep_quality, negative_sleep_thought, positive_sleep_thought
        """

def wakeup_time_to_string(diary):
    if diary.last_night_each_wakeup_time_in_minutes:
        return ",".join(map(str, diary.last_night_each_wakeup_time_in_minutes))
    else:
       return ''

def combine_string(x, y):
    if (x and y):
      return x + ", " + y
    elif (x):
        return x
    elif (y):
        return y
    else:
        return ''

def user_sleep_diary_history(user):
    sleep_diaries = find_sleep_diaries_by_user_id(user.id)
    print(f"sleep_diaries: {sleep_diaries.items}")
    if not sleep_diaries:
        return "This user has no records in their sleep diary history."
    days = reduce(combine_string, list(map(lambda s: str(s.day), sleep_diaries.items)), '')
    last_night_get_into_bed_time =  reduce(combine_string, list(map(lambda s: s.last_night_get_into_bed_time, sleep_diaries.items)), '')
    last_night_turn_off_light_time =  reduce(combine_string, list(map(lambda s: s.last_night_turn_off_light_time, sleep_diaries.items)), '')
    last_night_time_to_fall_asleep_in_minutes =  reduce(combine_string, list(map(lambda s: str(s.last_night_time_to_fall_asleep_in_minutes), sleep_diaries.items)), '')
    last_night_number_of_times_wakeup =  reduce(combine_string, list(map(lambda s: str(s.last_night_number_of_times_wakeup), sleep_diaries.items)), '')
    last_night_each_wakeup_time_in_minutes =  reduce(combine_string, list(map(lambda s: wakeup_time_to_string(s), sleep_diaries.items)), '')
    this_morning_wakeup_time =  reduce(combine_string, list(map(lambda s: s.this_morning_wakeup_time, sleep_diaries.items)), '')
    this_morning_get_out_of_bed_time =  reduce(combine_string, list(map(lambda s: s.this_morning_get_out_of_bed_time, sleep_diaries.items)), '')
    last_night_sleep_quality =  reduce(combine_string, list(map(lambda s: str(s.last_night_sleep_quality), sleep_diaries.items)), '')
    negative_sleep_thought =  reduce(combine_string, list(map(lambda s: s.negative_sleep_thought, sleep_diaries.items)), '')
    positive_sleep_thought =  reduce(combine_string, list(map(lambda s: s.positive_sleep_thought, sleep_diaries.items)), '')

    return f"""
    Following are the sleep diary history for days: {days} :
    The time get into bed previous night for those days: {last_night_get_into_bed_time},
    The time turned off light previous night for those days: {last_night_turn_off_light_time},
    The time spent to fall asleep previous night for those days: {last_night_time_to_fall_asleep_in_minutes},
    The number of times woke up previous night for those days: {last_night_number_of_times_wakeup},
    Time lasted for each wake up previous night for those days: {last_night_each_wakeup_time_in_minutes},
    The time wake up in the morning for those days: {this_morning_wakeup_time},
    The time get out of bed in the morning for those days: {this_morning_get_out_of_bed_time},
    The sleep quality of previous night for those days: {last_night_sleep_quality},
    Negative sleep thought previous night for those days: {negative_sleep_thought},
    Positie sleep thought previous night for those days: {positive_sleep_thought}
    """