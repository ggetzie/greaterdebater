from django.contrib import admin
from tcd.comments.models import TopicComment, tcdMessage, Draw, \
    ArgComment, Debate, nVote



admin.site.register(Draw)


class TopicCommentAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None,            {'fields': ['user', 'pub_date', 'ntopic', 'first']}),
        ('Flag Info',     {'fields': ['cflaggers', 'needs_review', 'spam']}),
        ('Text',          {'fields': ['comment', 'comment_html', 'nparent_id', 'nnesting', 'removed']}),
        ]
        
        

    list_display = ('user', 'pub_date', 'comment')
    list_filter = ['pub_date', 'needs_review', 'first', 'removed']


admin.site.register(TopicComment, TopicCommentAdmin)

class ArgCommentAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None,            {'fields': ['user', 'pub_date', 'ntopic']}),
        ('Flag Info',     {'fields': ['cflaggers', 'needs_review']}),
        ('Text',          {'fields': ['comment', 'comment_html']}),
        ('Debate Info', {'fields': ['debate']})
        ]
        
        

    list_display = ('user', 'pub_date', 'comment')
    list_filter = ['pub_date', 'needs_review']


admin.site.register(ArgComment, ArgCommentAdmin)


class tcdMessageAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None,            {'fields': ['user', 'recipient', 'pub_date', 'is_msg', 'is_read']}),
        ('Text',          {'fields': ['subject', 'comment', 'comment_html']}),
        ]
        
    list_display = ('pub_date', 'recipient', 'subject')

admin.site.register(tcdMessage, tcdMessageAdmin)

class DebateAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['defendant', 'plaintiff', 'title', 'topic', 'incite']}),
        ('Dates',      {'fields': ['start_date', 'end_date']}),
        ('Status',     {'fields': ['status', 'score']})
        ]

    list_display = ('start_date', 'title')
    list_filter = ('start_date', 'end_date', 'status')
         

admin.site.register(Debate, DebateAdmin)
