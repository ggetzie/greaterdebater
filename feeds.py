from django.contrib.syndication.feeds import Feed
from tcd.items.models import Topic, Argument
from tcd.settings import HOSTNAME

class NewTopics(Feed):
    title = 'GreaterDebater - New Topics'
    link = HOSTNAME + '/new/'
    description = 'The latest topics on GreaterDebater'
    
    def items(self):
        return Topic.objects.order_by('-sub_date')[:15]

class NewArguments(Feed):
    title = 'GreaterDebater - New Arguments'
    link = HOSTNAME + '/argue/new/'
    description = 'The latest arguments on GreaterDebater'

    def items(self):
        return Argument.objects.filter(status__range=(1,2)).order_by('-start_date')[:15]
