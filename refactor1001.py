import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tcd.settings'

from tcd.comments.models import Comment, TopicComment, ArgComment, nVote, Debate
from tcd.items.models import Topic, Argument, Vote, LogItem
from tcd.profiles.models import Profile
import datetime

def migrate():
    args = Argument.objects.all().order_by('id')
    # Find all the comments associated with a topic
    # and make a new TopicComment for each one
    coms = Comment.objects.filter(is_msg=False,
                                  arg_proper=False,
                                  topic__isnull=False).order_by('id')
    for com in coms:
        newcom = TopicComment(comment=com.comment,
                              user=com.user,
                              last_edit=com.last_edit,                                  
                              parent_id=com.parent_id,                                  
                              needs_review=com.needs_review,
                              # new fields
                              ntopic=com.topic,
                              nnesting=com.nesting,
                              first=com.is_first,                                  
                              removed=com.is_removed)
                                          
        newcom.save()

        # change the pub date to that of the original comment
        newcom.pub_date = com.pub_date
        newcom.save()
        for flagger in com.cflaggers.all():
            newcom.cflaggers.add(flagger)
        newcom.save()

    print "TopicComments created"

    for tcom in TopicComment.objects.all():
        # set parent_id for each TopicComment to that of the 
        # corresponding Comment
        oldcom = Comment.objects.get(comment=tcom.comment,
                                     user=tcom.user,
                                     pub_date=tcom.pub_date,
                                     topic__isnull=False)
        if oldcom.parent_id == 0:
            tcom.parent_id = 0
            tcom.nparent_id = 0
        else:
            oldparent = Comment.objects.get(id=oldcom.parent_id)
            newparent = TopicComment.objects.get(comment=oldparent.comment,
                                                 user=oldparent.user,
                                                 pub_date=oldparent.pub_date)
            tcom.parent_id = newparent.id
            tcom.nparent_id = newparent.id
        tcom.save()
    print "TopicComment parent ids fixed"

    for arg in args:
        newarg = Debate(plaintiff = arg.plaintiff,
                        defendant = arg.defendant,
                        end_date = arg.end_date,
                        start_date = arg.start_date,
                        topic = arg.topic,
                        title = arg.title, 
                        status = arg.status,
                        score = arg.score)

        old_incite = arg.comment_set.filter(arg_proper=False)[0]
        new_incite = TopicComment.objects.filter(comment=old_incite.comment,
                                                 user=old_incite.user,
                                                 pub_date=old_incite.pub_date)[0]
            
        newarg.incite = new_incite
        newarg.save()
        for com in arg.comment_set.filter(arg_proper=True).order_by('pub_date'):
            newcom = ArgComment(comment=com.comment,
                                user=com.user,
                                parent_id=com.parent_id,
                                # New fields
                                ntopic=com.topic,
                                debate=newarg)
            newcom.save()
            newcom.pub_date = com.pub_date
            newcom.save()

    print "Debates created, ArgComments created"
            
    # copy all existing votes to new nVote object
    votes = Vote.objects.all().order_by('id')

    for vote in votes:
        newdeb = Debate.objects.filter(title=vote.argument.title,
                                       plaintiff=vote.argument.plaintiff,
                                       defendant=vote.argument.defendant)[0]
        newvote = nVote(argument=newdeb,
                        voter=vote.voter,
                        voted_for=vote.voted_for)
        newvote.save()
    
    print "nVotes created"
    print "%d old topic comments, %d new TopicComments" % (coms.count(), TopicComment.objects.all().count())
    print "%d old arg comments, %d new ArgComments" % (Comment.objects.filter(arg_proper=True).count(),
                                                       ArgComment.objects.all().count())
    print "%d Arguments, %d Debates" % (Argument.objects.all().count(), Debate.objects.all().count())
    print "%d Votes, %d nVotes" % (Vote.objects.all().count(), nVote.objects.all().count())
        
                                       
def delnew():
    TopicComment.objects.all().delete()
    ArgComment.objects.all().delete()
    Debate.objects.all().delete()
    nVote.objects.all().delete()
    print "newly created objects deleted"
    
if __name__ == "__main__":
    migrate()
