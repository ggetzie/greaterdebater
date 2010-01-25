from django.contrib import admin
from tcd.blog.models import Blog, Post, PostComment

class BlogAdmin(admin.ModelAdmin):
    fields = ['author', 'start_date', 'title', 'tagline_txt', 'about_txt', 'altfeedurl']
    list_display = ('author', 'title')
    list_filter = ('start_date',)

admin.site.register(Blog, BlogAdmin)


class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'txt', 'html', 'created', 'pub_date', 'draft', 'tags', 'blog']

    list_display = ('created', 'title', 'blog')
    list_filter = ('created', 'pub_date', 'draft')
    
admin.site.register(Post, PostAdmin)        


class PostCommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,        {'fields': ['user', 'pub_date', 'post', 'blog']}),
        ('Flag Info', {'fields': ['cflaggers', 'needs_review']}),
        ('Text',      {'fields': ['comment', 'comment_html', 'nparent_id', 'nnesting']})
        ]

    list_display = ('user', 'comment', 'post', 'blog')
    list_filter = ('pub_date', 'needs_review')

admin.site.register(PostComment, PostCommentAdmin)

