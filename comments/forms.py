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

#from django import newforms as forms
from django import forms

attrs_dict = { 'class': 'required' }
class CommentForm(forms.Form):
    comment =  forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                    'rows': 5,
                                                                    'cols': 50}))
    redirect = forms.CharField(max_length=255, widget=forms.widgets.HiddenInput(), 
                               required=False)    
    parent_id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)
    nesting = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)
    toplevel = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)

class ArgueForm(forms.Form):
    """Form used for one user to challenge another to an argument"""
    comment =  forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                    'rows': 5,
                                                                    'cols': 50}))
    title = forms.CharField(max_length=140,
                            label="Title",
                            widget=forms.TextInput(attrs={'size': '50'}))
                            
    parent_id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)

    
class DeleteForm(forms.Form):
    comment_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    referring_page = forms.CharField(max_length=255, widget=forms.widgets.HiddenInput(), required=False)

class RebutForm(forms.Form):
    comment =  forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                    'rows': 5,
                                                                    'cols': 50}))
    redirect = forms.CharField(max_length=255, widget=forms.widgets.HiddenInput(), 
                               required=False)    
    parent_id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)
    nesting = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)
    toplevel = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
