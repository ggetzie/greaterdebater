from django.contrib import admin
from tcd.items.models import Topic, Tags


class TopicAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,        {'fields': ['user', 'sub_date', 'title', 'url']}),
        ('Flag Info', {'fields': ['tflaggers', 'needs_review']}),
        ('Scoring',   {'fields': ['score', 'comment_length', 'last_calc']}),
        (None,        {'fields': ['tags']})
        ]

    list_display = ('sub_date', 'title')
    list_filter = ('sub_date', 'needs_review', 'user')
         

admin.site.register(Topic, TopicAdmin)


class TagsAdmin(admin.ModelAdmin):
    fields = ['topic', 'user', 'tags']
    list_display = ('user', 'topic')
    

admin.site.register(Tags, TagsAdmin)
