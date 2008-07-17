from tcd.imports import *

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
    tops = Topic.objects.all()
    for top in tops:
        top.recalculate()
        top.save()
    print "recalculated all scores"
