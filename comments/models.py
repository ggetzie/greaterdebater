# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 Benoit Chesneau <benoitc@metavers.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode, force_unicode

from pygments import highlight, lexers, formatters
from markdown import markdown

import re
import datetime

from tcd.comments.forms import ArgueForm
from tcd.items.models import Topic, Argument
from tcd.utils import elapsed_time

"""
We cache lexer aliases to speed parsing. To update them, get lexers_aliases like this :
tlexers=lexers.get_all_lexers()
alexers=[]
for l in tlexers:
    for a in l[1]:
        alexers.append(a)

alexers.sort()
print alexers
"""

lexers_aliases = ['aconf', 'apache', 'apacheconf', 'bash', 'bat', 'bbcode', 'befunge', 'bf', 'boo', 'brainfuck', 'c', 'c#',
'c++', 'cfg', 'cpp', 'csharp', 'css', 'css+django', 'css+erb', 'css+genshi', 'css+genshitext', 'css+jinja',
'css+mako', 'css+myghty', 'css+php', 'css+ruby', 'css+smarty', 'd', 'delphi', 'diff', 'django', 'dylan', 'erb',
'genshi', 'genshitext', 'groff', 'haskell', 'html', 'html+django', 'html+erb', 'html+genshi', 'html+jinja',
'html+kid', 'html+mako', 'html+myghty', 'html+php', 'html+ruby', 'html+smarty', 'ini', 'irb', 'irc', 'java',
'javascript', 'javascript+django', 'javascript+erb', 'javascript+genshi', 'javascript+genshitext', 'javascript+jinja',
'javascript+mako', 'javascript+myghty', 'javascript+php', 'javascript+ruby', 'javascript+smarty', 'jinja', 'js',
'js+django', 'js+erb', 'js+genshi', 'js+genshitext', 'js+jinja', 'js+mako', 'js+myghty', 'js+php', 'js+ruby',
'js+smarty', 'jsp', 'kid', 'latex', 'lua', 'make', 'makefile', 'mako', 'man', 'mf', 'minid', 'moin', 'mupad',
'myghty', 'nroff', 'obj-c', 'objc', 'objective-c', 'objectivec', 'objectpascal', 'ocaml', 'pas', 'pascal', 'perl',
'php', 'php3', 'php4', 'php5', 'pl', 'py', 'pycon', 'pytb', 'python', 'raw', 'rb', 'rbcon', 'redcode', 'rest',
'restructuredtext', 'rhtml', 'rst', 'ruby', 'scheme', 'sh', 'smarty', 'sources.list', 'sourceslist', 'sql', 'tex',
'text', 'trac-wiki', 'vb.net', 'vbnet', 'vim', 'xml', 'xml+django', 'xml+erb', 'xml+genshi', 'xml+jinja', 'xml+kid',
'xml+mako', 'xml+myghty', 'xml+php', 'xml+ruby', 'xml+smarty']
    


class Comment(models.Model):
    comment = models.TextField()
    comment_html = models.TextField(blank=True)
    user = models.ForeignKey(User)
    pub_date = models.DateTimeField(blank=True, null=True)
    last_edit = models.DateTimeField(blank=True, null=True)
    is_removed = models.BooleanField(default=False)
    is_first = models.BooleanField(default=False)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    parent_id = models.IntegerField(default=0)
    nesting = models.IntegerField(null=True, blank=True)
    arguments = models.ManyToManyField(Argument, blank=True, null=True)
    arg_proper = models.BooleanField(default=False)
    is_msg = models.BooleanField(default=False)
    cflaggers = models.ManyToManyField(User, 
                                       verbose_name="Users who flagged this comment as spam", 
                                       related_name="cflaggers",
                                       blank=True)
    needs_review = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ('-pub_date',)
        
    def save(self):
        if not self.id:
            self.pub_date = datetime.datetime.now()          
        self.comment_html = self.hilight(self.comment)
        
        # match all the urls
        # this returns a tuple with two groups
        # if the url is part of an existing link, the second element
        # in the tuple will be "> or </a>
        # if not, the second element will be an empty string
        urlre = re.compile("(\(?https?://[-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|])(\">|</a>)?")
        urls = urlre.findall(self.comment_html)
        clean_urls = []
        
        # remove the duplicate matches
        # and replace urls with a link
        for url in urls:
            # ignore urls that are part of a link already
            if url[1]: continue
            c_url = url[0]
            if c_url[0] == '(' and c_url[len(c_url)-1] == ')':
                c_url = c_url[1:len(c_url)-1]

            if c_url in clean_urls: continue            
            clean_urls.append(c_url)
            # substitute only where the url is not already part of a
            # link element.
            self.comment_html = re.sub("(?<!(=\"|\">))" + re.escape(c_url), 
                                       "<a rel=\"nofollow\" href=\"" + c_url + "\">" + c_url + "</a>",
                                       self.comment_html)
            
        super(Comment, self).save()

    def __unicode__(self):
        return str(self.id)

    def get_elapsed(self):
        return elapsed_time(self.pub_date)



    def get_argue_form(self):
        return ArgueForm({'parent_id': self.id})
            
    def hilight(self, content):
        CODE_TAG_START = "{{{"
        CODE_TAG_END = "}}}"

        re_code = re.compile('%s(?P<code>.*?)%s' % (re.escape(CODE_TAG_START), re.escape(CODE_TAG_END)), re.DOTALL)

        in_tag=False
        hilighted=""
        lexer=None
        content="\n"+content
        for p in re_code.split(content): 
            if p:
                if in_tag: 
                    code_str=p
                    lang=""

                    if p.startswith("#!"):
                        c=""
                        i=0
                        while (c!=" " and c !="\n") and i<len(code_str):
                            lang+=c
                            c=code_str[i]
                            i+=1
                        if len(lang)>2:
                            lang=lang[2:].strip()

                    print lang
                    if lang in lexers_aliases:
                        lexer=lexers.get_lexer_by_name(lang)
                    else: 
                        try:
                            lexer = lexers.guess_lexer(code_str)
                        except:
                            lexer = lexers.get_lexer_by_name('text')
                    if lang:      
                        code_str=p[(len(lang)+2):]
                    print lexer
                    hilighted+= "<div class=\"hilight\">%s</div>" % highlight(code_str,lexer,
                                    formatters.HtmlFormatter(linenos='inline', 
                                                            cssclass="source", 
                                                            lineseparator="<br />"))
                else:
                    hilighted+=markdown(p, safe_mode=True)
                in_tag = not in_tag      
        return hilighted
        
class tcdMessage(Comment):
    recipient = models.ForeignKey(User)
    is_read = models.BooleanField(default=False)
    subject = models.CharField(max_length=200)
    
    def save(self):
        self.is_msg = True
        super(tcdMessage , self).save()
    
    class Meta:
        ordering = ('-pub_date',)



class TopicComment(Comment):
    ntopic = models.ForeignKey(Topic)
    first = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    nnesting = models.IntegerField()
    nparent_id = models.IntegerField(default=0)

    def save(self):
        super(TopicComment, self).save()

    def get_viewable_arguments(self):
        return Debate.objects.filter(status__range=(1,5), incite=self).count()


class Debate(models.Model):
    plaintiff = models.ForeignKey(User, related_name='plaintiff_set')
    defendant = models.ForeignKey(User, related_name='defendant_set')
    end_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField()
    incite = models.ForeignKey(TopicComment)
    topic = models.ForeignKey(Topic)
    title = models.CharField(max_length=140)
    # status codes: 0 = challenge made, response pending
    #               1 = argument in progress, plaintiff's turn
    #               2 = argument in progress, defendant's turn
    #               3 = argument over, defendant won
    #               4 = argument over, plaintiff won
    #               5 = argument over, draw
    #               6 = plaintiff declined challenge
    #               others invalid
    status = models.PositiveSmallIntegerField(default=0)
    score = models.FloatField(default=0)

    
    class Meta:
        ordering = ['-score', '-start_date']

    
    def __unicode__(self):
        return self.title
    
    def get_status(self):
        if self.status == 0:
            # challenge offered, defendent's turnn
            return "challenge pending"
        elif self.status == 1:
            # argument in progress, plaintiff's turn
            return ''.join([self.plaintiff.username, "'s turn"])
        elif self.status == 2:
            # argument in progress, defendants's turn
            return ''.join([self.defendant.username, "'s turn"])
        elif self.status == 3:
            # argument over, defendant wins
            return ''.join([self.defendant.username, " wins!"])
        elif self.status == 4:
            # argument over, plaintiff wins
            return ''.join([self.plaintiff.username, " wins!"])
        elif self.status == 5:
            # opponents agreed to a draw
            return "draw"
        elif self.status == 6:
            # argument never started, defendant declined challenge
            return ''.join([ self.defendant.username, " declined challenge"])
        else:
            return "invalid status"        

    def is_current(self):
        if self.status in (1,2):
            return True
        else:
            return False
    
    def whos_up(self, invert=0):
        # returns the user whose turn it is in an argument
        # if invert == 1, returns the user whose turn it is NOT
        participants = (self.defendant, self.plaintiff)
        if self.status in [0, 2]:
            return participants[invert]
        elif self.status == 1:
            return participants[1-invert]
        else:
            return None

    def get_opponent(self, user):
        if user == self.defendant:
            return self.plaintiff
        elif user == self.plaintiff:
            return self.defendant
        else:
            return None

    def get_elapsed(self):
        return elapsed_time(self.start_date)

    def get_remaining(self):
        end = self.start_date + datetime.timedelta(days=8)
        # The debate ends on midnight after
        # the debate is 7 days old
        end = datetime.datetime(year=end.year,
                                month=end.month,
                                day=end.day,
                                hour=0,
                                minute=0, 
                                second=0)
        remaining = end - datetime.datetime.now()
        if remaining.days > 0:
            if remaining.days == 1:
                return "%d day" % remaining.days
            else:
                return "%d days" % remaining.days
        elif remaining.seconds > 3600:
            hours = remaining.seconds / 3600
            if hours == 1:
                return "%d hour" % hours
            else:
                return "%d hours" % hours
        elif remaining.seconds > 60:
            minutes = remaining.seconds / 60
            if minutes == 1:
                return "%d minute" % minutes
            else:
                return "%d minutes" % minutes
        else:
            return "Time's Up!"

    def reset(self):
        # Get the winner and reduce his score by one
        winner = None
        if self.status == 3:
            winner = self.defendant
        elif self.status == 4:
            winner = self.plaintiff
        else:
            return "Argument cannot be reset, no winner"
        prof = Profile.objects.get(user = winner)
        prof.score -= 1
        prof.save()

        # Set the status of the argument so it's the loser's turn again
        self.status -= 2
        self.save()

    def calculate_score(self):
        numvotes = nVote.objects.filter(argument=self.id).count()
        delta = datetime.datetime.now() - self.start_date
        hours2 = (delta.days*24 + delta.seconds/(3600) + 1.0)**2
        self.score = float(numvotes / hours2)
        self.save()

    def first_two(self):
        # The initial comment that inspired the argument
        # and the first assault by the plaintiff
        return [self.incite, self.argcomment_set.order_by('pub_date')[0]]

    def get_absolute_url(self):
        return '/'.join([HOSTNAME, 'argue', str(self.id)])

class ArgComment(Comment):
    ntopic = models.ForeignKey(Topic)
    debate = models.ForeignKey(Debate)
    
    def save(self):
        super(ArgComment, self).save()


class nVote(models.Model):

    argument = models.ForeignKey(Debate)
    voter = models.ForeignKey(User)
    voted_for = models.CharField(max_length=1) # "P" for plaintiff or "D" for defendant
    
    def __unicode__(self):
        return ' '.join([self.voter.username, "voted for", self.voted_for, "in arg", self.argument.title])

class Draw(models.Model):
    offeror = models.ForeignKey(User, related_name='offeror')
    recipient = models.ForeignKey(User, related_name='recipient')
    offer_date = models.DateTimeField()
    argument = models.ForeignKey(Debate)

    def __unicode__(self):
        return ''.join(["Argument ", str(self.argument.id)])
