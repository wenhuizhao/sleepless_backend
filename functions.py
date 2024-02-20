import json

from db_service import update_user, update_guest, create_sleep_diary


def update_sleep_info(arguments_str, user=None, guest=None):
    output = ""
    if not user and not guest:
        return output
    arguments_dict = json.loads(arguments_str)
    if user and user.data:
        data = dict(user.data)
    elif guest and guest.data:
        data = dict(guest.data)
    else:
        data = {}
    for key in arguments_dict:
        if key in ["sleep_problem_duration", "sleep_habit", "six_week_program_start_time"]:
            value = arguments_dict[key]
            data[key] = value
            print(f"update_user or guest: {key} -> {value}")
    if user:
        user.data = data
        update_user(user)
    elif guest:
        guest.data = data
        update_guest(guest)
    output = "update sleep infor successfully"
    return output    

def update_sleep_diary(arguments_str, user, guest=None):
    output = ""
    if not user:
        return output
    arg_dict = json.loads(arguments_str)
    create_sleep_diary(
        user_id = user.id,
        last_night_get_into_bed_time=arg_dict.get('last_night_get_into_bed_time'),
        last_night_turn_off_light_time=arg_dict.get('last_night_turn_off_light_time'),
        last_night_time_to_fall_asleep_in_minutes=arg_dict.get('last_night_time_to_fall_asleep_in_minutes'),
        last_night_number_of_times_wakeup=arg_dict.get('last_night_number_of_times_wakeup'),
        last_night_each_wakeup_time_in_minutes=arg_dict.get('last_night_each_wakeup_time_in_minutes'),
        this_morning_wakeup_time=arg_dict.get('this_morning_wakeup_time'),
        this_morning_get_out_of_bed_time=arg_dict.get('this_morning_get_out_of_bed_time'),
        last_night_sleep_quality=arg_dict.get('last_night_sleep_quality'),
        negative_sleep_thought=arg_dict.get('negative_sleep_thought'),
        positive_sleep_thought=arg_dict.get('positive_sleep_thought')
    )
    output = "update sleep diary successfully"
    return output
