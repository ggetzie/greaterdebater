from django.contrib import admin
from tcd.comments.models import Comment, tcdMessage, Draw



admin.site.register(Draw)


class CommentAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None,            {'fields': ['user', 'pub_date', 'topic', 'is_first']}),
        ('Flag Info',     {'fields': ['cflaggers', 'needs_review']}),
        ('Text',          {'fields': ['comment', 'comment_html', 'parent_id', 'nesting', 'is_msg', 'is_removed']}),
        ('Argument Info', {'fields': ['arguments', 'arg_proper']})
        ]
        
        

    list_display = ('user', 'pub_date', 'comment')
    list_filter = ['pub_date', 'needs_review', 'is_msg', 'arg_proper', 'is_first', 'is_removed']


admin.site.register(Comment, CommentAdmin)


class tcdMessageAdmin(admin.ModelAdmin):
    
    fieldsets = [
        (None,            {'fields': ['user', 'recipient', 'pub_date', 'is_msg', 'is_read']}),
        ('Text',          {'fields': ['subject', 'comment', 'comment_html']}),
        ]
        
    list_display = ('pub_date', 'recipient', 'subject')

admin.site.register(tcdMessage, tcdMessageAdmin)
