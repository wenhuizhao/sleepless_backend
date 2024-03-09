
import enum
from sqlalchemy import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from database import db 


class SleepDiary(db.Model):
    __tablename__ = 'sleep_diaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True, nullable=True)
    day = db.Column(db.Integer)
    last_night_get_into_bed_time = db.Column(db.Integer)
    last_night_turn_off_light_time = db.Column(db.Integer)
    last_night_time_to_fall_asleep_in_minutes = db.Column(db.Integer)
    last_night_number_of_times_wakeup = db.Column(db.Integer)
    last_night_each_wakeup_time_in_minutes = db.Column(JSONB)
    this_morning_wakeup_time = db.Column(db.Integer)
    this_morning_get_out_of_bed_time = db.Column(db.Integer)
    last_night_sleep_quality = db.Column(db.Integer)
    negative_sleep_thought = db.Column(db.String)
    positive_sleep_thought = db.Column(db.String)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user = db.relationship("User", backref="sleep_diaries")
 
    def __init__(self, user_id, day, last_night_get_into_bed_time, last_night_turn_off_light_time, last_night_time_to_fall_asleep_in_minutes,
                 last_night_number_of_times_wakeup, last_night_each_wakeup_time_in_minutes, this_morning_wakeup_time,
                 this_morning_get_out_of_bed_time, last_night_sleep_quality, negative_sleep_thought, positive_sleep_thought):
        self.user_id = user_id
        self.day = day
        self.last_night_get_into_bed_time = last_night_get_into_bed_time
        self.last_night_turn_off_light_time = last_night_turn_off_light_time
        self.last_night_time_to_fall_asleep_in_minutes = last_night_time_to_fall_asleep_in_minutes
        self.last_night_number_of_times_wakeup = last_night_number_of_times_wakeup
        self.last_night_each_wakeup_time_in_minutes = last_night_each_wakeup_time_in_minutes
        self.this_morning_wakeup_time = this_morning_wakeup_time
        self.this_morning_get_out_of_bed_time = this_morning_get_out_of_bed_time
        self.last_night_sleep_quality = last_night_sleep_quality
        self.negative_sleep_thought = negative_sleep_thought
        self.positive_sleep_thought = positive_sleep_thought
    
    def to_s(self):
        if (self.last_night_get_into_bed_time):
            last_night_get_into_bed_time_val = f"The time get into bed last night: {self.last_night_get_into_bed_time},"
        else: 
            last_night_get_into_bed_time_val = ""
        
        if (self.last_night_turn_off_light_time):
            last_night_turn_off_light_time_val = f"The time turned off light last night: {self.last_night_turn_off_light_time},"
        else: 
            last_night_turn_off_light_time_val = ""

        if (self.last_night_time_to_fall_asleep_in_minutes):
            last_night_time_to_fall_asleep_in_minutes_val = f"The time spent to fall asleep last night: {self.last_night_time_to_fall_asleep_in_minutes},"
        else: 
            last_night_time_to_fall_asleep_in_minutes_val = ""

        if (self.last_night_number_of_times_wakeup):
            last_night_number_of_times_wakeup_val = f"The number of times woke up last night: {self.last_night_number_of_times_wakeup},"
        else: 
            last_night_number_of_times_wakeup_val = ""
        
        if (self.last_night_each_wakeup_time_in_minutes):
            last_night_each_wakeup_time_in_minutes_val = f"Time lasted for each wake up last night: {self.last_night_each_wakeup_time_in_minutes},"
        else: 
            last_night_each_wakeup_time_in_minutes_val = ""

        if (self.this_morning_wakeup_time):
            this_morning_wakeup_time_val = f"The time wake up this morning: {self.this_morning_wakeup_time}"
        else: 
            this_morning_wakeup_time_val = ""

        if (self.this_morning_get_out_of_bed_time):
            this_morning_get_out_of_bed_time_val = f"The time get out of bed this morning: {self.this_morning_get_out_of_bed_time},"
        else:
            this_morning_get_out_of_bed_time_val = ""

        if (self.last_night_sleep_quality):
            last_night_sleep_quality_val = f"The sleep quality of last night: {self.last_night_sleep_quality},"
        else:
            last_night_sleep_quality_val = ""
        
        if (self.negative_sleep_thought):
            negative_sleep_thought_val = f"Negative sleep thought last night: {self.negative_sleep_thought},"
        else:
            negative_sleep_thought_val = ""
        
        if (self.positive_sleep_thought):
            positive_sleep_thought_val = f"Positive sleep thought last night: {self.positive_sleep_thought},"
        else:
            positive_sleep_thought_val = ""

        return f"""
        This is the sleep diary for day {self.day}:
        {last_night_get_into_bed_time_val}
        {last_night_turn_off_light_time_val}
        {last_night_time_to_fall_asleep_in_minutes_val}
        {last_night_number_of_times_wakeup_val}
        {last_night_each_wakeup_time_in_minutes_val}
        {this_morning_wakeup_time_val}
        {this_morning_get_out_of_bed_time_val}
        {last_night_sleep_quality_val}
        {negative_sleep_thought_val}
        {positive_sleep_thought_val}
        """

    def __repr__(self):
        return '<id {}>'.format(self.id)