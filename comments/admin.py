from django.contrib import admin
from tcd.comments.models import Comment, tcdMessage, Draw

admin.site.register(Comment)

#     class Admin:
#         list_display = ('user', 'pub_date')
#         fields=(
#         (None, {'fields': ('topic', 'parent_id', 'nesting', 'is_removed', 
#                            'is_first', 'pub_date', 'arg_proper')}),
#         ('Content', {'fields': ('user', 'comment')}),
#         )
#         search_fields = ('comment','user__username')
#         date_hierarchy = 'pub_date'

admin.site.register(tcdMessage)

admin.site.register(Draw)
