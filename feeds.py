from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist

from tcd.blog.models import Blog, Post
from tcd.comments.models import Debate
from tcd.items.models import Topic
from tcd.settings import HOSTNAME

class NewTopics(Feed):
    title = 'GreaterDebater - New Topics'
    link = HOSTNAME + '/new/'
    description = 'The latest topics on GreaterDebater'
    
    def items(self):
        return Topic.objects.order_by('-sub_date')[:15]

class NewArguments(Feed):
    title = 'GreaterDebater - New Debates'
    link = HOSTNAME + '/argue/new/'
    description = 'The latest debates on GreaterDebater'

    def items(self):
        return Debate.objects.filter(status__range=(1,2)).order_by('-start_date')[:15]

class BlogFeed(Feed):
    desciption_template = 'feeds/blog_description.html'

    def get_object(self, blog_id):
        if len(blog_id) != 1:
            return ObjectDoesNotExist
        else:
            return Blog.objects.get(id__exact=blog_id[0])

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.about_html

    def items(self, obj):
        return Post.objects.filter(blog=obj, draft=False).order_by('-pub_date')[:30]
        
