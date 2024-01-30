import os
from dotenv import load_dotenv
import decimal, datetime
from sqlalchemy.orm import sessionmaker
from database import db
from user import User
from message import Message
from blog import Blog
from guest import Guest
from sleep_diary import SleepDiary
import dateutil.parser
from datetime import datetime, timezone

load_dotenv()
engine = db.create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

PAGE_SIZE=10

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def create_user(name, email, avatar=None):
    user = User(name=name, email=email, avatar=avatar)
    session.add(user)
    session.commit()

def find_user_by_email(email):
    user = session.execute(db.select(User).filter_by(email=email)).scalar_one()
    return user

def create_guest(name):
    guest = Guest(name=name)
    session.add(guest)
    session.commit()

def update_user(user):
    local_user = session.merge(user)
    session.add(local_user)
    session.commit()

def update_guest(guest):
    local_guest = session.merge(guest)
    session.add(local_guest)
    session.commit()

def find_guest_by_name(name):
    #guest = Guest.query.filter_by(name=name).first()
    guest = session.execute(db.select(Guest).filter_by(name=name)).scalar_one()
    return guest

def create_message(user, text, type, guest=None):
    if user:
        message = Message(user_id=user.id, text=text, type=type)
    elif guest:
        message = Message(text=text, type=type, guest=guest)

    save_message(message)

def save_message(message):
    local_message = session.merge(message)
    session.add(local_message)
    session.commit()

def messages_by_user_id(user_id, page):
    messages = Message.query.filter_by(user_id=user_id).order_by(Message.time_created.desc()).paginate(page=page, per_page=PAGE_SIZE)
    return messages

def messages_by_guest(guest, page):
    messages = Message.query.filter_by(guest=guest).order_by(Message.time_created.desc()).paginate(page=page, per_page=PAGE_SIZE)
    return messages

def days_since_join_program(user_id):
    user = User.query.get(user_id)
    if user.data and user.data.get('six_week_program_start_time'):
        program_start_time = dateutil.parser.isoparse(user.data.get('six_week_program_start_time'))
        days = (datetime.now(timezone.utc) - program_start_time).days
    else:
        days = 0
        user.data['six_week_program_start_time'] = datetime.now(timezone.utc).isoformat()
        update_user(user)
    return days

def create_sleep_diary(user_id, last_night_get_into_bed_time, last_night_turn_off_light_time, last_night_time_to_fall_asleep_in_minutes,
                 last_night_number_of_times_wakeup, last_night_each_wakeup_time_in_minutes, this_morning_wakeup_time,
                 this_morning_get_out_of_bed_time, last_night_sleep_quality, negative_sleep_thought, positive_sleep_thought):
    day = days_since_join_program(user_id)
    sleep_diary = find_sleep_diary_by_user_id_day(user_id, day)
    if sleep_diary:
        if last_night_get_into_bed_time: sleep_diary['last_night_get_into_bed_time'] = last_night_get_into_bed_time
        if last_night_turn_off_light_time: sleep_diary['last_night_turn_off_light_time'] = last_night_turn_off_light_time
        if last_night_time_to_fall_asleep_in_minutes: sleep_diary["last_night_time_to_fall_asleep_in_minutes"]=last_night_time_to_fall_asleep_in_minutes
        if last_night_number_of_times_wakeup: sleep_diary['last_night_number_of_times_wakeup'] = last_night_number_of_times_wakeup
        if last_night_each_wakeup_time_in_minutes: sleep_diary['last_night_each_wakeup_time_in_minutes'] = last_night_each_wakeup_time_in_minutes
        if this_morning_wakeup_time: sleep_diary['this_morning_wakeup_time'] = this_morning_wakeup_time
        if this_morning_get_out_of_bed_time: sleep_diary['this_morning_get_out_of_bed_time'] = this_morning_get_out_of_bed_time
        if last_night_sleep_quality: sleep_diary['last_night_sleep_quality'] = last_night_sleep_quality
        if negative_sleep_thought: sleep_diary['negative_sleep_thought'] = negative_sleep_thought
        if positive_sleep_thought: sleep_diary['positive_sleep_thought'] = positive_sleep_thought
    else:
        sleep_diary = SleepDiary(user_id, day, last_night_get_into_bed_time, last_night_turn_off_light_time, last_night_time_to_fall_asleep_in_minutes,
                 last_night_number_of_times_wakeup, last_night_each_wakeup_time_in_minutes, this_morning_wakeup_time,
                 this_morning_get_out_of_bed_time, last_night_sleep_quality, negative_sleep_thought, positive_sleep_thought)
    save_sleep_diary(sleep_diary)

def save_sleep_diary(sleep_diary):
    local_sleep_diary = session.merge(sleep_diary)
    session.add(local_sleep_diary)
    session.commit()

def find_sleep_diary_by_user_id_day(user_id, day):
    try:
        sleep_diary = session.execute(db.select(SleepDiary).filter_by(user_id=user_id, day=day)).scalar_one()
    except:
        sleep_diary = None
    return sleep_diary
        
def find_sleep_diaries_by_user_id(user_id, page=1):
    sleep_diaries = SleepDiary.query.filter_by(user_id=user_id).order_by(SleepDiary.day.desc()).paginate(page=page, per_page=PAGE_SIZE)
    return sleep_diaries

def sync_guest_data_to_user(guest_name, user):
    guest = find_guest_by_name(guest_name)
    if not user.data:
        user.data = {}
    print(f"guest.data:{guest.data}")
    if guest.data:
        for key in guest.data:
            user.data[key] = guest.data[key]
            print(f"update user key:{key}, value:{guest.data[key]}")
        update_user(user)
        print("done update_user")
    messages = Message.query.filter_by(guest=guest_name)
    for message in messages:
        message.guest = None
        message.user_id = user.id
        save_message(message)

def create_blog(user, title, content):
    blog = Blog(user_id=user.id, title=title, content=content)
    session.add(blog)
    session.commit()

def blog_by_id(blog_id):
    return session.scalar(db.select(Blog).where(Blog.id == blog_id))

def all_blogs():
    result = session.scalars(db.select(Blog).order_by(Blog.time_created))
    return result

