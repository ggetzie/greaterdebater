from django.contrib import admin
from tcd.items.models import Topic, Argument, Vote, Tags

admin.site.register(Topic)
admin.site.register(Argument)
admin.site.register(Tags)
