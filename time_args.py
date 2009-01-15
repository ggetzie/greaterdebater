import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.comments.models import *
from tcd.items.models import Argument, Vote, LogItem
from tcd.profiles.models import Profile
import datetime

def time_args():
    """Get all active arguments from the database and end the ones without
a reply for more than seven days"""

    args = Argument.objects.filter(status__range=(1,2))
    count = 0
    for arg in args:
        last_comment = arg.comment_set.latest('pub_date')
        elapsed = datetime.datetime.now() - arg.start_date
        if elapsed.days >= 7:
            count += 1            
            votes = Vote.objects.filter(argument=arg)
            pvotes = votes.filter(voted_for="P").count()
            dvotes = votes.filter(voted_for="D").count()
            if pvotes == dvotes:
                arg.status = 5
                winner = arg.plaintiff
                loser = arg.defendant
                win_message = ''.join(["The masses have spoken regarding the argument \n",
                                       "[", arg.title, "]", "(/argue/", str(arg.id), "/)",
                                       "\nand their answer is...It's a tie"])
                lose_message = win_message
            else:
                if pvotes > dvotes:
                    arg.status = 4
                    winner = arg.plaintiff
                    loser = arg.defendant
                else:                    
                    arg.status = 3
                    winner = arg.defendant
                    loser = arg.plaintiff
                
                win_message = ''.join(["By popular demand, you are the winner of the argument \n",
                                       "[", arg.title, "]", "(/argue/", str(arg.id), "/)",
                                       "\nCongratulations!"])

                lose_message = ''.join(["Sorry! You have lost the argument \n",
                                        "[", arg.title, "]", "(/argue/", str(arg.id), "/)",
                                        "\n By popular vote."])

                prof = Profile.objects.get(user=winner)
                prof.score += 1
                prof.save()
            win_msg = tcdMessage(user=loser, recipient=winner, comment=win_message, 
                                 subject="And the winner is...", parent_id=0, nesting=0)

            lose_msg = tcdMessage(user=winner, recipient=loser, comment=lose_message, 
                                  subject="And the winner is...", parent_id=0, nesting=0)
            arg.end_date = datetime.datetime.now()
            arg.save()
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

def age_args():
    """
    Artificially age arguments by 8 days for testing purposes
    """
    args = Argument.objects.filter(status__range=(1,2))
    delta = datetime.timedelta(days=8)
    for arg in args:
        arg.start_date = arg.start_date - delta
        arg.save()

if __name__ == "__main__":
    time_args()

    
