# -*- coding: utf-8 -*-


# Copyright (c) 2007 Benoit Chesneau <bchesneau@gmail.com>
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


from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from comments.forms import CommentForm
from comments.models import Comment


register = template.Library()
class CommentFormNode(template.Node):
    def __init__(self, content_type, object_id_var, redirect_to):
        self.content_type=content_type
        self.object_id_var=object_id_var
        self.redirect_to=redirect_to
               
    def render(self, context):
        if self.object_id_var is not None:
            try:
                object_id=template.resolve_variable(self.object_id_var, context)
            except template.VariableDoesNotExist:
                return ''

            try:
                self.content_type.get_object_for_this_type(pk=object_id)
            except ObjectDoesNotExist:
                context['display_form_comment'] = False
            else:
                context['display_form_comment'] = True
        else:
            context['display_form_comment'] = False
          
        if self.redirect_to != None:
            try:
                redirect_to=template.resolve_variable(self.redirect_to, context)
            except:
                redirect_to=self.redirect_to     
        
            form = CommentForm({
                'content_type': self.content_type.id,
                'object_id': object_id,
                'redirect': redirect_to,
            })
        else:
            form = CommentForm({
                'content_type': self.content_type.id,
                'object_id': object_id,
            })
        context['form_comment']=form
        context['form_comment_action']=reverse('comments.views.add')
        return ''
        
def do_comment_form(parser, token):
    bits = token.contents.split()
    len_bits = len(bits)
    
    if len_bits not in (4, 6):
        raise template.TemplateSyntaxError("'%s' tag takes three or five arguments" % bits[0])
        
    if bits[1]!='for':
         raise TemplateSyntaxError("first argument to %s tag must be 'for'" % bits[0])
         
    if bits[4]!='redirect_to':
        raise TemplateSyntaxError("fifth argument to %s tag must be 'redirect_to'" % bits[0])
        
    try:
        package, module = bits[2].split('.')
    except ValueError: # unpack list of wrong size
        raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
    try:
        content_type = ContentType.objects.get(app_label__exact=package, model__exact=module)
    except ContentType.DoesNotExist:
        raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
    
        
    if len_bits==4:
        return CommentFormNode(content_type,bits[3],None)
    
    return CommentFormNode(content_type,bits[3],bits[5])
register.tag('comment_form', do_comment_form)        

class ShowCommentsNode(template.Node):
    def __init__(self, content_type, object_id_var):
        self.content_type=content_type
        self.object_id_var=object_id_var
               
    def render(self, context):
        if self.object_id_var is not None:
            try:
                object_id=template.resolve_variable(self.object_id_var, context)
            except template.VariableDoesNotExist:
                return ''
            
            try:
                self.content_type.get_object_for_this_type(pk=object_id)
            except ObjectDoesNotExist:
                context['display_comments'] = False
            else:
                context['display_comments'] = True
                context['comments']=Comment.objects.filter(content_type=self.content_type).filter(object_id=object_id)
                context['comments_count'] = len(context['comments'])
        else:
            context['display_comments'] = False
        
        return ''


def do_show_comments(parser,token):
    bits = token.contents.split()
    len_bits = len(bits)
    
    if len_bits != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    
    if bits[1]!='for':
        raise TemplateSyntaxError("first argument to %s tag must be 'for'" % bits[0])
    
    try:
        package, module = bits[2].split('.')
    except ValueError: # unpack list of wrong size
        raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
    try:
        content_type = ContentType.objects.get(app_label__exact=package, model__exact=module)
    except ContentType.DoesNotExist:
        raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
    return ShowCommentsNode(content_type,bits[3])
register.tag('show_comments', do_show_comments)



class CommentsCountNode(template.Node):
    def __init__(self, content_type, object_id_var):
        self.content_type=content_type
        self.object_id_var=object_id_var
               
    def render(self, context):
        if self.object_id_var is not None:
            try:
                object_id=template.resolve_variable(self.object_id_var, context)
            except template.VariableDoesNotExist:
                return ''
            
            try:
                self.content_type.get_object_for_this_type(pk=object_id)
            except ObjectDoesNotExist:
                return 0
            else:
                return Comment.objects.filter(content_type=self.content_type).filter(object_id=object_id).count()
        
        return 0


def do_comment_count(parser,token):
    bits = token.contents.split()
    len_bits = len(bits)
    
    if len_bits != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    
    if bits[1]!='for':
        raise TemplateSyntaxError("first argument to %s tag must be 'for'" % bits[0])
    
    try:
        package, module = bits[2].split('.')
    except ValueError: # unpack list of wrong size
        raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
    try:
        content_type = ContentType.objects.get(app_label__exact=package, model__exact=module)
    except ContentType.DoesNotExist:
        raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
    return CommentsCountNode(content_type,bits[3])
register.tag('comments_count', do_comment_count)
