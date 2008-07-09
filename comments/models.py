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
from datetime import datetime

from tcd.items.models import Topic, Argument

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
    is_removed = models.BooleanField(default=False)
    is_first = models.BooleanField(default=False)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    parent_id = models.IntegerField()
    nesting = models.IntegerField(null=True, blank=True)
    arguments = models.ManyToManyField(Argument, blank=True, null=True)
    arg_proper = models.BooleanField(default=False)
    is_msg = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ('pub_date',)
        
    class Admin:
        list_display = ('user', 'pub_date')
        fields=(
        (None, {'fields': ('topic', 'parent_id', 'nesting', 'is_removed', 
                           'is_first', 'pub_date', 'arg_proper')}),
        ('Content', {'fields': ('user', 'comment')}),
        )
        search_fields = ('comment','user__username')
        date_hierarchy = 'pub_date'
        
    def save(self):
        if not self.id:
            self.pub_date = datetime.now()          
        self.comment_html=self.hilight(self.comment)
        self.comment_html = self.comment_html.replace('\n', "<br />")
        self.comment_html = self.comment_html.replace('<p>', """<p class="commentp">""")
        super(Comment , self).save()

    def __unicode__(self):
        return str(self.id)
        
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
    
    class Admin:
        list_display = ('user', 'pub_date')
        fields=(
        (None, {'fields': ('parent_id', 'pub_date', 'is_read')}),
        ('Content', {'fields': ('user', 'recipient', 'comment')}),
        )
        search_fields = ('comment','user__username', 'recipient__username')

        
    class Meta:
        ordering = ('-pub_date',)

class Draw(models.Model):
    offeror = models.ForeignKey(User, related_name='offeror')
    recipient = models.ForeignKey(User, related_name='recipient')
    offer_date = models.DateTimeField()
    argument = models.ForeignKey(Argument)

    def __unicode__(self):
        return ''.join(["Argument ", str(self.argument.id)])

