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
    minus1h = datetime.datetime.now() - datetime.timedelta(seconds=3540)
    tops = Topic.objects.filter(last_calc__lt=minus1h, needs_review=False, spam=False)
    for top in tops:
        top.recalculate()
        top.save()

    args = Debate.objects.filter(status__range=(1,2))
    for arg in args: 
        arg.calculate_score()
        arg.save()

    log = LogItem(date=datetime.datetime.now(),
                  message= ''.join(["recalc_all success ", str(tops.count()), " updated"]))
    log.save()

def setback():
    minus2h = datetime.datetime.now() - datetime.timedelta(seconds=7200)
    tops = Topic.objects.all()
    for top in tops:
        top.last_calc = minus2h
        top.save()

if __name__ == "__main__":
    recalc_all()

