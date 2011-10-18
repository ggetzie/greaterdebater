import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.comments.models import Debate, TopicComment, ArgComment
from tcd.items.models import Topic, LogItem
import datetime

def calculate_scores():
    tops = Topic.objects.all()
    for top in tops:
        top.comment_length = 0
        coms = top.topiccomment_set.filter(needs_review=False) | top.argcomment_set.filter(needs_review=False)
        for com in coms:
            top.comment_length += len(com.comment)
        top.recalculate()
        top.save()
    print "fin"

def recalc_all():
    # for all topics older than ninety days where the score is not already 0,
    # set the score to 0
    ninety_days = datetime.datetime.now() - datetime.timedelta(days=90)
    old_tops = Topic.objects.filter(sub_date__lt=ninety_days, score__gt = 0.0)
    for top in old_tops:
        top.score = 0
        top.save()
    
    minus1h = datetime.datetime.now() - datetime.timedelta(seconds=3540)
    tops = Topic.objects.filter(last_calc__lt=minus1h, needs_review=False, spam=False,
                                sub_date__gt=ninety_days)
    for top in tops:
        top.recalculate()
        top.save()

    args = Debate.objects.filter(status__range=(1,2))
    for arg in args: 
        arg.calculate_score()
        arg.save()

    log = LogItem(date=datetime.datetime.now(),
                  message= "recalc_all success %d update, %d expired" % (tops.count(), old_tops.count()))
    log.save()

def setback():
    minus2h = datetime.datetime.now() - datetime.timedelta(seconds=7200)
    tops = Topic.objects.all()
    for top in tops:
        top.last_calc = minus2h
        top.save()

if __name__ == "__main__":
    recalc_all()

