from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404

attrs_dict = {'class': 'required'}

class tcdTopicSubmitForm(forms.Form):
    title = forms.CharField(max_length=140, label="Title", widget=forms.TextInput(attrs={'size': '70'}))
    url = forms.URLField(label="URL", required=False,
                         help_text="Leave the URL field blank to submit a self-referential topic.",
                         widget=forms.TextInput(attrs={'size': '70'}))
    tags = forms.CharField(label="Tags", widget=forms.TextInput(attrs={'size':'70'}),
                           required=False,
                           help_text = """Words or short phrases that describe the topic separated by commas <br />
e.g. Politics, News, Current Events""")
    comment = forms.CharField(label="Text", required=False,
                              widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                   'rows': 5,
                                                                   'cols': 70}))
    
    def clean_url(self):
        url = self.cleaned_data.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            return ''.join(['http://', url])
        else:
            return url

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            tags = tags.split(',')
            return ','.join([tag.strip().lower() for tag in tags])
        else:
            return ''


class TagEdit(forms.Form):
    topic_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    tags = forms.CharField(label="Tags", widget=forms.TextInput(attrs={'size':'70'}),
                           required=False,
                           help_text = """Words or short phrases that describe the topic separated by commas <br />
e.g. Politics, News, Current Events""")

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if tags:
            tags = tags.split(',')
            return ','.join([tag.strip().lower() for tag in tags])
        else:
            return ''
    

class Ballot(forms.Form):
    argument = forms.IntegerField(widget=forms.widgets.HiddenInput())
    voter = forms.IntegerField(widget=forms.widgets.HiddenInput())
    voted_for = forms.CharField(widget=forms.widgets.HiddenInput(), required=False)
    
    def clean_voted_for(self):
        voted_for = self.cleaned_data.get('voted_for', '')
        if voted_for:
            if voted_for == "P" or voted_for == "D":
                return voted_for
            else:
                raise forms.ValidationError("Invalid vote")
        else:
            return voted_for


class Flag(forms.Form):
    object_id = forms.IntegerField(widget=forms.widgets.HiddenInput())


class Concession(forms.Form):
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())


class Response(forms.Form):
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    response = forms.TypedChoiceField(widget=forms.widgets.HiddenInput(), 
                                      choices=[(0, 'accept'), (1, 'decline')],
                                      coerce=int)
