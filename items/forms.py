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

class Ballot(forms.Form):
    argument = forms.IntegerField(widget=forms.widgets.HiddenInput())
    voter = forms.IntegerField(widget=forms.widgets.HiddenInput())
    voted_for = forms.CharField(widget=forms.widgets.HiddenInput())
    
    def clean_voted_for(self):
        voted_for = self.cleaned_data.get('voted_for', '')
        if voted_for == "P" or voted_for == "D":
            return voted_for
        else:
            raise forms.ValidationError("Invalid vote")

class Flag(forms.Form):
    object_id = forms.IntegerField(widget=forms.widgets.HiddenInput())

class Concession(forms.Form):
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
