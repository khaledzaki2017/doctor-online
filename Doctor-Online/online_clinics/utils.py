from datetime import timedelta

# Static delta time for all reservations
DELTA_TIME = 30


# Check time is before or after static delta time?
def before_or_after_delta(time):
    if time.minute >= DELTA_TIME:
        print('after')
        time += timedelta(hours=1)
        return time.replace(minute=0, second=0, microsecond=0)
    else:
        print('before')
        return time.replace(minute=DELTA_TIME, second=0, microsecond=0)


# Return tomorrow time if latest time is bigger or equal than end time of the day
def tomorrow(start_time, time):
    print('tomorrow')
    time += timedelta(days=1)
    return time.replace(hour=start_time, minute=0, second=0, microsecond=0)
