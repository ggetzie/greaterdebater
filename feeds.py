from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.utils.feedgenerator import Atom1Feed

from tcd.blog.models import Blog, Post
from tcd.comments.models import Debate, TopicComment
from tcd.items.models import Topic
from tcd.profiles.models import Profile
from tcd.settings import HOSTNAME

class NewTopics(Feed):
    title = 'GreaterDebater - New Topics'
    link = HOSTNAME + '/new/'
    description = 'The latest topics on GreaterDebater'
    
    def items(self):
        return Topic.objects.filter(needs_review=False, spam=False).order_by('-sub_date')[:15]

class NewArguments(Feed):
    title = 'GreaterDebater - New Debates'
    link = HOSTNAME + '/argue/new/'
    description = 'The latest debates on GreaterDebater'

    def items(self):
        return Debate.objects.filter(status__range=(1,2)).order_by('-start_date')[:15]

class BlogFeed(Feed):
    description_template = 'feeds/blog_description.html'

    def get_object(self, request, blog_id):
        return get_object_or_404(Blog, pk=blog_id)
    
    def title(self, obj):
        return obj.title
    
    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.about_html

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def items(self, obj):
        return Post.objects.filter(blog=obj, draft=False).order_by('-pub_date')[:30]
        
class UserFeed(Feed):
    description = "Recent activity on GreaterDebater."

    def get_object(self, request, username):
        # if len(username) != 1:
        #     return ObjectDoesNotExist
        
        prof = Profile.objects.get(user__username__exact=username)
        
        if not (prof.feedcoms or prof.feedtops or prof.feeddebs):
            return ObjectDoesNotExist

        return prof

    def title(self, obj):
        return "GreaterDebater activity for " + obj.user.username

    def link(self, obj):
        return obj.get_absolute_url()

    def items(self, obj):
        return activity(obj)[:15]

    def item_description(self, item):
        if type(item) == Topic:
            item_template = loader.get_template('feeds/newtopics_description.html')
        elif type(item) == TopicComment:
            item_template = loader.get_template('feeds/comdesc.html')
        elif type(item) == Debate:
            item_template = loader.get_template('feeds/newargs_description.html')
        else:
            return "Unknown Object"
        item_context = Context({'obj': item})
        return item_template.render(item_context)
        

class UserFeedAtom(UserFeed):
    feed_type = Atom1Feed
    subtitle = UserFeed.description

def activity(prof):
    coms = None
    tops = None
    debs = None
    qsets = []
    if prof.feedcoms:
        coms = list(TopicComment.objects.filter(user=prof.user, first=False).order_by("-pub_date")[:50])
        qsets.append(coms)
    if prof.feedtops:
        tops = list(Topic.objects.filter(user=prof.user).order_by("-sub_date")[:50])
        qsets.append(tops)
    if prof.feeddebs:
        debset = Debate.objects.filter(plaintiff=prof.user, status__in=(range(1,6))) | \
            Debate.objects.filter(defendant=prof.user, status__in=(range(1,6)))
        debs = list(debset.order_by("-start_date")[:50])
        qsets.append(debs)

    if len(qsets) == 1: return qsets[0]
    itemlist = []
    for qset in qsets: itemlist.extend(qset)
    itemlist.sort(key=lambda x: x.get_date(), reverse=True)
    return itemlist
                
