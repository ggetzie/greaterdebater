from django.db import models
from django.contrib.auth.models import User

from markdown import markdown

from tcd.comments.models import Comment
from tcd.settings import HOSTNAME

class Blog(models.Model):
    author = models.ForeignKey(User)
    start_date = models.DateTimeField()
    title = models.CharField(max_length=140)
    tagline_txt = models.CharField(max_length=140, blank=True)
    about_txt = models.TextField(blank=True)
    about_html = models.TextField(blank=True)
    altfeedurl = models.URLField(blank=True, verify_exists=False)

    def save(self):
        about_html = markdown(self.about_txt)
        super(Blog, self).save()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ''.join([HOSTNAME, '/blog/', self.author.username, '/'])

    def getrssurl(self):
        if self.altfeedurl:
            return self.altfeedurl
        else:
            return ''.join([HOSTNAME, '/feeds/blog/', str(self.id)])


class Post(models.Model):
    title = models.CharField(max_length=140)
    txt = models.TextField()
    html = models.TextField(blank=True)
    created = models.DateTimeField()
    pub_date = models.DateTimeField(blank=True, null=True)
    draft = models.BooleanField(default=True)
    tags = models.TextField(blank=True)
    blog = models.ForeignKey(Blog)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def save(self):
        self.html = markdown(self.txt)
        super(Post, self).save()

    def get_absolute_url(self):
        return ''.join([self.blog.get_absolute_url(), 'post/', str(self.id), '/'])

class PostComment(Comment):
    blog = models.ForeignKey(Blog)
    post = models.ForeignKey(Post)
    nparent_id = models.IntegerField(default=0)
    nnesting = models.IntegerField(default=0)
