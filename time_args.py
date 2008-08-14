import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.comments.models import *
from tcd.items.models import *
import datetime

def time_args():
    """Get all active arguments from the database and end the ones without
a reply for more than seven days"""

    args = Argument.objects.filter(status__range=(1,2))
    count = 0
    for arg in args:
        last_comment = arg.comment_set.latest('pub_date')
        elapsed = datetime.datetime.now() - last_comment.pub_date
        if elapsed.days >= 7:
            count += 1
            loser = arg.whos_up()
            winner = arg.get_opponent(loser)
            prof = Profile.objects.get(user=winner)
            prof.score += 1
            win_message = ''.join(["No reply has been made for 7 days in the argument \n",
                                   "[", arg.title, "]", "(/argue/", str(arg.id), "/)",
                                   "\nSo you win by default, the two sweetest words in",
                                   " the English language!"])
            win_msg = tcdMessage(user=loser,
                                 recipient=winner,
                                 comment=win_message,
                                 subject="De-Fault!",
                                 parent_id=0,
                                 nesting=0)
            lose_message = ''.join(["Too slow! The argument \n",
                                    "[", arg.title, "]", "(/argue/", str(arg.id), "/)",
                                    "\n has timed out. You lose."])
            lose_msg = tcdMessage(user=winner,
                                  recipient=loser,
                                  comment=lose_message,
                                  subject="That's too bad",
                                  parent_id=0,
                                  nesting=0)
            arg.status += 2
            arg.end_date = datetime.datetime.now()
            arg.save()
            prof.save()
            win_msg.save()
            lose_msg.save()
    log = LogItem(date=datetime.datetime.now(),
                  message="time_args success. %i args ended." % count)
    log.save()

    # Clear all log items older than 30 days
    cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
    expired_logs = LogItem.objects.filter(date__lt=cutoff)
    log = LogItem(date=datetime.datetime.now(),
                  message="deleted %i expired log items" % expired_logs.count())
    log.save()
    expired_logs.delete()

if __name__ == "__main__":
    time_args()

    
