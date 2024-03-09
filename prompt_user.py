from datetime import datetime, timezone
import dateutil.parser
from prompt_base import unknown_sleep_problem_duration_prompt, short_term_sleep_problem_prompt, long_term_sleep_problem_unknown_habit_prompt, \
    long_term_sleep_problem_fixed_habit_prompt, long_term_sleep_problem_nofixed_habit_prompt
from db_service import find_sleep_diary_by_user_id_day, find_sleep_diaries_by_user_id
from prompt_helper import add_question_chat_history
from functools import reduce
from date_util import days_in_program, time_difference
from misc_util import average

CORE_SLEEP_TIME = 530

def get_user_prompt(question, user, history_messages=[]):
    print("14 fellas")
    chat_history = "\n".join(history_messages)
    print(f"get_user_prompt user.data: {user.data}")

    if user.data and user.data.get('six_week_program_start_time'):
        prompt = get_user_prompt_in_six_week_program(user, question, history_messages)

    elif user.data and  user.data.get('sleep_problem_duration') == 'long_term':
        if user.data and user.data.get('sleep_habit') == 'same_time_everyday':
            prompt = long_term_sleep_problem_fixed_habit_prompt()
        elif user.data and user.data.get('sleep_habit') == 'not_fixed':
            prompt = long_term_sleep_problem_nofixed_habit_prompt()
        else:
            prompt = long_term_sleep_problem_unknown_habit_prompt()

    elif user.data and  user.data.get('sleep_problem_duration') == 'short_term':
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
    #sleep_diary_history = user_sleep_diary_history(user)
    if sleep_diary:
        prompt = f"""
        The user is in the six week program. Today is the number {days} days in the program.
        You already collected users sleep diary for yesterday. Here is user's sleep diary for yesterday:
        {sleep_diary.to_s()}
        """ + prompt_in_program(days, user)
        # Answer user's questions based on his sleep diary history:
        # {sleep_diary_history}
    else:
        prompt = user_sleep_program_day_prompt(days, sleep_diary)
    return add_question_chat_history(prompt, question, history_messages)

def user_welcome_message_content(user):
    if (user.data == None or user.data.get('six_week_program_start_time') == None):
        return f"""
        Welcome, {user.name}. How was your sleep last night? 
        """
    sleep_diaries = find_sleep_diaries_by_user_id(user.id).items
    program_start_time_str = user.data['six_week_program_start_time']
    program_start_time = dateutil.parser.isoparse(program_start_time_str)
    days = days_in_program(user, program_start_time)
    welcome_message = f"""Welcome back, {user.name}. This is Day {days} of your sleep improvement program. """

    diary_entry = list(filter(lambda x: x.day == days, sleep_diaries))
    if diary_entry:
        return welcome_message
    else:
        return welcome_message + f"""As part of the program, I'd like to hear about how you slept yesterday. Is that okay?"""

def has_positive_thought(sleep_diary):
    if sleep_diary.positive_sleep_thought and sleep_diary.positive_sleep_thought.lower() != 'no' and  sleep_diary.positive_sleep_thought.lower() != 'none':
        return True
    else:
        return False

def sleep_time(sleep_diary):
    if (sleep_diary.last_night_turn_off_light_time == None or sleep_diary.last_night_time_to_fall_asleep_in_minutes == None or sleep_diary.this_morning_wakeup_time == None):
        return
    fall_asleep_time = (sleep_diary.last_night_turn_off_light_time + sleep_diary.last_night_time_to_fall_asleep_in_minutes) % 2360
    return time_difference(fall_asleep_time, sleep_diary.this_morning_wakeup_time)

def average_sleep_time(sleep_diaries):
     sleep_diaries_with_sleep_time = list(filter(lambda x: (sleep_time(x) != None), sleep_diaries))
     count = len(sleep_diaries_with_sleep_time)
     if (count == 0):
        return None
     average_sleep = round(sum(sleep_time(sleep_diary) for sleep_diary in sleep_diaries_with_sleep_time) / count, 2)
     return average_sleep

def time_in_bed(sleep_diary):
    if (not sleep_diary.last_night_get_into_bed_time or not sleep_diary.this_morning_get_out_of_bed_time):
      return
    return time_difference(sleep_diary.last_night_get_into_bed_time, sleep_diary.this_morning_get_out_of_bed_time)

def average_time_in_bed(sleep_diaries):
    sleep_diaries_with_time_in_bed = list(filter(lambda x: (time_in_bed(x) != None), sleep_diaries))
    count = len(sleep_diaries_with_time_in_bed)
    if (count == 0):
        return None
    average_in_bed = round(sum(time_in_bed(sleep_diary) for sleep_diary in sleep_diaries_with_time_in_bed) / count, 2)
    return average_in_bed

def average_sleep_quality(sleep_diaries):
    sleep_diaries_with_rating = list(filter(lambda x: ((x.last_night_sleep_quality) != None), sleep_diaries))
    count = len(sleep_diaries_with_rating)
    if (count == 0):
        return None
    average_rating = round(sum(sleep_diary.last_night_sleep_quality for sleep_diary in sleep_diaries_with_rating) / count, 2)
    return average_rating

def sleep_summary(user, week):
    adjusted_week = week - 1
    if week == 0:
        return ''
    else:
      sleep_diaries = find_sleep_diaries_by_user_id(user_id=user.id, week=adjusted_week).items
      diary_count = sum(1 for sleep_diary in sleep_diaries)
      good_nights = sum(1 for sleep_diary in sleep_diaries if sleep_diary.last_night_sleep_quality and sleep_diary.last_night_sleep_quality >= 6)
      core_sleeps = sum(1 for sleep_diary in sleep_diaries if sleep_time(sleep_diary) and sleep_time(sleep_diary) > CORE_SLEEP_TIME)
      insomnia_nights = sum(1 for sleep_diary in sleep_diaries if sleep_diary.last_night_sleep_quality and sleep_diary.last_night_sleep_quality <= 3)
      positive_thoughts = sum(1 for sleep_diary in sleep_diaries if has_positive_thought(sleep_diary))
      
      summary_prompt = f"""
      Give the user a week one progress summary using their sleep diaries.
      Include:
      1) the number of sleep diaries recorded by the user, {diary_count}
      2) the number of good nights of sleep, {good_nights}
      3) the number of nights where the user obtained their core sleep of 5 and a half hours, {core_sleeps}
      4) the number of nights of insomnia, {insomnia_nights}
      5) the number of diaries with positive sleep thoughts, {positive_thoughts}
      """

    if (week >= 2):
      average_sleep = average_sleep_time(sleep_diaries)
      average_in_bed = average_time_in_bed(sleep_diaries)
      average_sleep_rating = average_sleep_quality(sleep_diaries)
      summary_prompt += f"""
      6) average sleep time, {average_sleep} (convert from military time for the user)
      7) average time spent in bed, {average_in_bed} (convert from military time for the user)
      8) average sleep quality rating from your diaries, {average_sleep_rating}
      """
          
      return summary_prompt
   

def user_sleep_program_day_prompt(days, sleep_diary):
    print('150 fellas')
    current_sleep_diary = sleep_diary.to_s() if sleep_diary else ""
    return f"""
        The user is in the six week sleep improvement program. Today is Day {days} of the program. 
        Collect the following information from the user by asking them questions:
        1. time the user get into bed last night,
        2. time the user turned off light last night,
        3. time it takes for the user to fall asleep last night,
        4. number of times the user wake up last night,
        5. time lasted for each wakeup last night (skip if they didn't wake up last night),
        6. time the user wakeup this morning,
        7. time the user get off bed this morning,
        8. sleep quality last night on a 0-10 scale (10 being the best, 0 being the worst).
        9. negative sleep thought last night. for example: I'm stressed that if don't fall asleep, tomorrow will be terrible.
        10. positive sleep thought last night for example: I feel good today. I will sleep well.
        Ask the user every question, one question at a time. Only collect data from today's messages
        Here is the data you've already collected today: {current_sleep_diary}
        When all the answers are collected,
        call function update_sleep_diary with arguments last_night_get_into_bed_time,  last_night_turn_off_light_time,
        last_night_time_to_fall_asleep_in_minutes, last_night_number_of_times_wakeup,
        last_night_each_wakeup_time_in_minutes, this_morning_wakeup_time, this_morning_get_out_of_bed_time,
        last_night_sleep_quality, negative_sleep_thought, positive_sleep_thought 
        (record as 'no' if the user had no positive sleep thoughts)
        (record all times as military time without colons. for example, 730 means 7:30 am)
        once all data has been collected, ask the user if they would like any advice.
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

def user_sleep_diary_history(user, week=None):
    if week==None:
      sleep_diaries = find_sleep_diaries_by_user_id(user.id)
    else:
      sleep_diaries = find_sleep_diaries_by_user_id(user.id, week)
    print(f"sleep_diaries: {sleep_diaries.items}")
    if not sleep_diaries:
        return "This user has no records in their sleep diary history."
    days = reduce(combine_string, list(map(lambda s: str(s.day), sleep_diaries.items)), '')
    last_night_get_into_bed_time =  reduce(combine_string, list(map(lambda s: str(s.last_night_get_into_bed_time), sleep_diaries.items)), '')
    last_night_turn_off_light_time =  reduce(combine_string, list(map(lambda s: str(s.last_night_turn_off_light_time), sleep_diaries.items)), '')
    last_night_time_to_fall_asleep_in_minutes =  reduce(combine_string, list(map(lambda s: str(s.last_night_time_to_fall_asleep_in_minutes), sleep_diaries.items)), '')
    last_night_number_of_times_wakeup =  reduce(combine_string, list(map(lambda s: str(s.last_night_number_of_times_wakeup), sleep_diaries.items)), '')
    last_night_each_wakeup_time_in_minutes =  reduce(combine_string, list(map(lambda s: wakeup_time_to_string(s), sleep_diaries.items)), '')
    this_morning_wakeup_time =  reduce(combine_string, list(map(lambda s: str(s.this_morning_wakeup_time), sleep_diaries.items)), '')
    this_morning_get_out_of_bed_time =  reduce(combine_string, list(map(lambda s: str(s.this_morning_get_out_of_bed_time), sleep_diaries.items)), '')
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
    Positive sleep thought previous night for those days: {positive_sleep_thought}
    """

def prompt_in_program(days_in_program, user):
    print('228 fellas')
    week = days_in_program // 7
    if (week==0):
        prompt=f"""
        Give the user sleep advice based on Chapter 5 'Changing Your Thoughts About Sleep'
        of the book 'Say Goodnight to Insomnia' by Gregg D Jacobs. Pick one topic to give new
        advice about for each day. Try to give only one piece of advice each day. 
        Here are the chapter topics: 'The Placebo Effect and Psychoneuroimmunology,' 'Negative Sleep Thoughts,'
        'Cognitive Restructuring,' 'The Eight-Hour Sleep Myth,' 'Core Sleep,' 'The Effects of Sleep Loss'
        """
    elif (week==1):
        prompt=f"""
        Give the user sleep advice based on Chapter 6 Establishing Sleep Promoting Habits" 
        of the book "Say Goodnight to Insomnia" by Gregg D Jacobs. Pick one topic to give new
        advice about for each day. Try to give only one piece of advice each day. 
        Here are the chapter topics: 'Sleep-Scheduling Techniques,' 'Reducing Time Alloted for Sleep,'
        'Napping,' 'Stimulus-Control Techniques.'
        """
    elif (week==2):
        prompt=f"""
        Give the user sleep advice based on Chapter 7 'Lifestyle and Environmental Factors that Affect Sleep'
        of the book 'Say Goodnight to Insomnia' by Gregg D Jacobs. Pick one topic to give new
        advice about for each day. Try to give only one piece of advice each day. 
        """
    elif (week==3):
        prompt=f"""
        Give the user sleep advice based on Chapter 8 of the book 'Say Goodnight to Insomnia' by Gregg D Jacobs. 
        Pick one topic to give new advice about for each day. Try to give only one piece of advice each day. 
        """
    elif (week==4):
        prompt=f"""
        Give the user sleep advice based on Chapter 9 of the book 'Say Goodnight to Insomnia' by Gregg D Jacobs.
        Pick one topic to give new advice about for each day. Try to give only one piece of advice each day. 
        """
    print (f'191, week: {week}')
    prompt += sleep_summary(user, week)
    prompt += f"""
        Do not mention the book name and author name in your response.
        """
    print ('195')
    return prompt