from datetime import datetime, timezone
import dateutil.parser
import pytz
def days_in_program(user, program_start_time):
  tz = pytz.timezone(user.timezone)
  now = datetime.now(tz)
  hours = now.time().hour
  days = (now - program_start_time.replace(hour=0)).days
  if (hours < 4):
    days -= 1
  return days

def time_difference(from_time, to_time):
  if (from_time == None or to_time == None):
    return None
  
  diff = to_time - from_time
  if (diff < 0):
    diff += 2400
    
  return diff