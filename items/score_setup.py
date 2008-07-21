import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.imports import *
import datetime

def calculate_scores():
    tops = Topic.objects.all()
    for top in tops:
        coms = top.comment_set.filter(is_msg=False)
        for com in coms:
            top.comment_length += len(com.comment)
        top.recalculate()
        top.save()
    print "fin"

def recalc_all():
    minus1h = datetime.datetime.now() - datetime.timedelta(seconds=3540)
    tops = Topic.objects.filter(last_calc__lt=minus1h)
    for top in tops:
        top.recalculate()
        top.save()
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

