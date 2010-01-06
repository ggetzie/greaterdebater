from django.db import models
from django.contrib.auth.models import User

from markdown import markdown

from tcd.comments.models import Comment

class Blog(models.Model):
    author = models.ForeignKey(User)
    start_date = models.DateTimeField()


class Post(models.Model):
    txt = models.TextField()
    html = models.TextField(blank=True)
    created = models.DateTimeField()
    pub_date = models.DateTimeField(blank=True)
    draft = models.BooleanField(default=True)
    tags = models.TextField(blank=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-pub_date')

    def save(self):
        self.html = markdown(post_txt)

class PostComment(Comment):
    blog = models.ForeignKey(Blog)
    post = models.ForeignKey(Post)

                             
