from django.contrib.auth.models import User

from blog.models import *
from comments.models import *
from items.models import *
from profiles.models import *
from utils import update_tags

from settings import HOSTNAME

def testsetup():
    # Create some users
    user1, prof1 = create_user(username="user1", password="password",
                               email="user1@test.com")
    user2, prof2 = create_user(username="user2", password="password",
                               email="user2@test.com")
    user3, prof3 = create_user(username="user3", password="password",
                               email="user3@test.com")

    # Create some topics
    topic1 = create_topic(user1, "Topic 1", "tag1", comment="First topic outside link",
                          url="http://google.com")
    topic2 = create_topic(user2, "Topic 2", "tag2", comment="Second topic self link")
    topic3 = create_topic(user3, "Topic 3", "tag3") # No first comment
    topic4 = create_topic(user1, "Topic 4") # No first comment, no tags

    # Comment on some topics
    # Topic 2
    #   -com1
    #     -com2
    #       -com4
    #     -com3
    com1 = create_tcomment(user1, topic2, txt="Comment 1")
    com2 = create_tcomment(user2, topic2, txt="Comment 2", parent=com1)
    com3 = create_tcomment(user3, topic2, txt="Comment 3", parent=com1)
    com4 = create_tcomment(user1, topic2, txt="Comment 4", parent=com2)

    # Follow a topic and a comment
    com1.followers.add(user1)
    com1.save()
    topic1.followers.add(user1)
    topic1.save()


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
                  last_calc=datetime.datetime.now())
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

    params = {'comment': txt,
              'user': user,
              'ntopic': top}

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

    prof = Profile.objects.get(user=user)
    prof.last_post = c.pub_date
    prof.save()

    return c
