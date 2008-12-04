from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404

attrs_dict = {'class': 'required'}

class tcdTopicSubmitForm(forms.Form):
    title = forms.CharField(max_length=140, label="Title")
    url = forms.URLField(label="URL", required=False,
                         help_text="Leave the URL field blank to submit a self-referential topic.")
    comment = forms.CharField(label="Text", required=False,
                              widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                   'rows': 5,
                                                                   'cols': 50}))
    referring_page = forms.CharField(max_length=255, widget=forms.widgets.HiddenInput(), required=False)    

    def clean_url(self):
        url = self.cleaned_data.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            return ''.join(['http://', url])
        else:
            return url
