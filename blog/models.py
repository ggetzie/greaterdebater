from django.db import models
from django.contrib.auth.models import User

from markdown import markdown

from tcd.comments.models import Comment

class Blog(models.Model):
    author = models.ForeignKey(User)
    started = models.DateTimeField()


class Post(models.Model):
    post_txt = models.TextField()
    post_html = models.TextField(blank=True)
    pub_date = models.DateTimeField(blank=True)
    draft = models.BooleanField(default=True)
    tags = models.TextField(blank=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-pub_date')

    def save(self):
        self.post_html = markdown(post_txt)

class PostComment(Comment):
    post = models.ForeignKey(Post)

                             
