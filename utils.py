import datetime
import random
import types

def random_string(length):
    """Returns an alphanumeric string of random characters with the given length"""
    alphanumeric = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(alphanumeric) for x in range(length)])

def calc_start(page, paginate_by, count):
    """Calculate the first number in a section of a list of objects to be displayed as a numbered list"""
    if page is not None:
        if page == 'last':
            return paginate_by * (count / paginate_by) + 1
        else:
            return paginate_by * (int(page) - 1) + 1                
    else:
        return 1

def elapsed_time(dtime):
    delta = datetime.datetime.now() - dtime
    if delta.days > 7:
        return time_plural(delta.days / 7, "week")
    elif delta.days > 0:
        return time_plural(delta.days, "day")
    elif delta.seconds > 3600:
        return time_plural(delta.seconds / 3600, "hour")
    elif 3600 > delta.seconds >= 60:
        return time_plural(delta.seconds / 60, "minute")
    elif 60 > delta.seconds >= 1:
        return time_plural(delta.seconds, "second")
    elif delta.seconds == 0:
        return time_plural(delta.microseconds / 1000, "millisecond")
    else:
        return "0 milliseconds"

def time_plural(num, unit):
    if num == 1:
        return ''.join([str(num), " ", unit])
    else:
        return ''.join([str(num), " ", unit, "s"])

    
