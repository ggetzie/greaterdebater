from django.contrib.auth.models import User

from blog.models import *
from comments.models import *
from items.models import *
from profiles.models import *
from utils import update_tags

from settings import HOSTNAME

def testsetup():
    # Create some users
    users = []
    profiles = []
    for i in range(10):
        username="user"+str(i)
        u, p = create_user(username=username, password="password",
                           email=username+"@test.com")
        if i < 8: 
            p.probation = False
            p.save()
        users.append(u)
        profiles.append(p)

    users[0].is_staff=True
    users[0].save()

    # Create some topics
    topic1 = create_topic(users[0], "Topic 1", "tag1", comment="First topic outside link",
                          url="http://google.com")
    topic2 = create_topic(users[1], "Topic 2", "tag2", comment="Second topic self link")
    topic3 = create_topic(users[2], "Topic 3", "tag3") # No first comment
    topic4 = create_topic(users[3], "Topic 4") # No first comment, no tags
    topic5 = create_topic(users[8], "Topic 5") # user on probation
    topic6 = create_topic(users[9], "Topic 6") # user on probation

    # Comment on some topics
    # Topic 2
    #   -com1
    #     -com2
    #       -com4
    #     -com3
    com1 = create_tcomment(users[0], topic2, txt="Comment 1")
    com2 = create_tcomment(users[1], topic2, txt="Comment 2", parent=com1)
    com3 = create_tcomment(users[2], topic2, txt="Comment 3", parent=com1)
    com4 = create_tcomment(users[0], topic2, txt="Comment 4", parent=com2)
    com5 = create_tcomment(users[8], topic1, txt="Comment 5") # user on probation
    com6 = create_tcomment(users[9], topic1, txt="Comment 6") # user on probation

    # Follow a topic and a comment
    com1.followers.add(users[0])
    com1.save()
    topic1.followers.add(users[0])
    topic1.save()

    ##  Create some debates

    # Pending debate, status=0
    deb_pending = Debate(plaintiff=users[1],
                         defendant=com1.user,
                         status=0,
                         incite=com1,
                         title="Pending Debate",
                         start_date=datetime.datetime.now(),
                         topic=com1.ntopic)
    deb_pending.save()
    deb_pending_com1 = ArgComment(user=deb_pending.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pending,
                                  pub_date=datetime.datetime.now(),
                                  comment="Pending debate challenge")
    deb_pending_com1.save()

    # Debate, plaintiff's turn status=1
    deb_pturn = Debate(plaintiff=users[2],
                         defendant=com1.user,
                         status=1,
                         incite=com1,
                         title="Debate - Plaintiff turn",
                         start_date=datetime.datetime.now(),
                         topic=com1.ntopic)
    deb_pturn.save()
    deb_pturn_com1 = ArgComment(user=deb_pending.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pturn,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plantiff turn challenge")
    deb_pturn_com1.save()

    deb_pturn_com2 = ArgComment(user=deb_pending.defendant,
                                  ntopic=com1.ntopic,
                                  debate=deb_pturn,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plantiff turn 1st rebuttal")
    deb_pturn_com2.save()

    # Debate, defendant's turn status=2
    deb_dturn = Debate(plaintiff=users[3],
                         defendant=com1.user,
                         status=2,
                         incite=com1,
                         title="Debate - Defendent turn",
                         start_date=datetime.datetime.now(),
                         topic=com1.ntopic)
    deb_dturn.save()
    deb_dturn_com1 = ArgComment(user=deb_dturn.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_dturn,
                                  pub_date=datetime.datetime.now(),
                                  comment="Defendant turn challenge")
    deb_dturn_com1.save()

    # Debate, defendant wins, status = 3
    deb_dwin = Debate(plaintiff=users[4],
                      defendant=com1.user,
                      status=3,
                      incite=com1,
                      title="Debate - Defendent wins",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_dwin.save()
    deb_dwin_com1 = ArgComment(user=deb_dwin.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_dwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Defendant win challenge")
    deb_dwin_com1.save()

    deb_dwin_com2 = ArgComment(user=deb_dwin.defendant,
                                  ntopic=com1.ntopic,
                                  debate=deb_dwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Defendant win 1st rebuttal")
    deb_dwin_com2.save()

    # Debate, plaintiff wins, status = 4
    deb_pwin = Debate(plaintiff=users[5],
                      defendant=com1.user,
                      status=4,
                      incite=com1,
                      title="Debate - Plaintiff wins",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_pwin.save()
    deb_pwin_com1 = ArgComment(user=deb_pwin.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plaintiff win challenge")
    deb_pwin_com1.save()

    deb_pwin_com2 = ArgComment(user=deb_pwin.defendant,
                                  ntopic=com1.ntopic,
                                  debate=deb_pwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plaintiff win 1st rebuttal")
    deb_pwin_com2.save()

    deb_pwin_com3 = ArgComment(user=deb_pwin.plaintiff,
                                  ntopic=com1.ntopic,
                                  debate=deb_pwin,
                                  pub_date=datetime.datetime.now(),
                                  comment="Plaintiff win 2nd rebuttal")
    deb_pwin_com3.save()
    
    deb_pwin_vote1 = nVote(argument=deb_pwin,
                           voter=users[1],
                           voted_for='P')
    deb_pwin_vote1.save()

    deb_pwin_vote2 = nVote(argument=deb_pwin,
                           voter=users[2],
                           voted_for='P')
    deb_pwin_vote2.save()

    deb_pwin_vote3 = nVote(argument=deb_pwin,
                           voter=users[3],
                           voted_for='D')
    deb_pwin_vote3.save()

    # Debate ends in a draw, status = 5
    deb_draw = Debate(plaintiff=users[5],
                      defendant=com1.user,
                      status=5,
                      incite=com1,
                      title="Debate - Draw",
                      start_date=datetime.datetime.now(),
                      end_date=datetime.datetime.now(),
                      topic=com1.ntopic)
    deb_draw.save()
    deb_draw_com1 = ArgComment(user=deb_draw.plaintiff,
                               ntopic=com1.ntopic,
                               debate=deb_draw,
                               pub_date=datetime.datetime.now(),
                               comment="Draw challenge")
    deb_draw_com1.save()

    deb_draw_com2 = ArgComment(user=deb_draw.defendant,
                               ntopic=com1.ntopic,
                               debate=deb_draw,
                               pub_date=datetime.datetime.now(),
                               comment="Draw 1st rebuttal")
    deb_draw_com2.save()
                                       

def create_user(username, password, email):
    new_user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
    new_user.is_staff=False
    new_user.is_superuser=False
    new_user.is_active=True
    new_user.save()

    prof = Profile(user=new_user,
                   score=0)
    prof.save()

    return new_user, prof

                                    
def create_topic(user, title, tags='', url='', comment=''):
    prof = Profile.objects.get(user=user)
    topic = Topic(user = user,
                  title=title,
                  score=1,
                  sub_date=datetime.datetime.now(),
                  comment_length=0,
                  last_calc=datetime.datetime.now(),
                  needs_review=prof.probation)
    topic.save()

    if url:
        topic.url=url
    else:
        topic.url = ''.join([HOSTNAME, '/', str(topic.id), '/'])

    dtags = tags
    if dtags:
        # create the count of all tags for the topic
        tags = '\n'.join([dtags, ','.join(['1']*(dtags.count(',')+1))])
        topic.tags = tags

        # create a Tags object to indicate the submitter
        # added these tags to this topic                        
        utags = Tags(user=user, topic=topic, tags=dtags)
        utags.save()

        # update the count of all tags used by the submitter
        prof.tags = update_tags(prof.tags, dtags.split(','))
        prof.save()

    topic.save()


    prof.last_post = topic.sub_date
    prof.save()

    if comment:
        comment = TopicComment(user=user,
                               ntopic=topic,
                               pub_date=datetime.datetime.now(),
                               comment=comment,
                               first=True,
                               nparent_id=0,
                               nnesting=0)
        comment.save()

        topic.comment_length += len(comment.comment)
        topic.recalculate()
        topic.save()

    return topic

def create_tcomment(user, top, txt, parent=None):

    prof = Profile.objects.get(user=user)

    params = {'comment': txt,
              'user': user,
              'ntopic': top,
              'needs_review': prof.probation}

    if parent:
        params['nparent_id'] = parent.id
        params['nnesting'] = parent.nnesting + 40
    else:
        params['nparent_id'] = 0
        params['nnesting'] = 10

    c = TopicComment(**params)
    c.save()		    

    top.comment_length += len(c.comment)
    top.recalculate()
    top.save()


    prof.last_post = c.pub_date
    prof.save()

    return c



    
