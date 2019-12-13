import pytz
from datetime import datetime

moscow_tz = pytz.timezone('Europe/Moscow')

def now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def fromtimestamp(t):
    return datetime.fromtimestamp(t, moscow_tz)


def to_local_time(naive_dt):
    if naive_dt:
        return naive_dt.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
