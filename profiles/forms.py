from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404

import re

class tcdUserCreationForm(forms.Form):
    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(min_length=8, 
                                widget=forms.widgets.PasswordInput(),
                                label="Password:")
    password2 = forms.CharField(min_length=8, 
                                widget=forms.widgets.PasswordInput(),
                                label="Password (again)")

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if User.objects.filter(username=username):
            raise forms.ValidationError("A user with that name already exists")
        
        if re.search("[^a-zA-Z0-9_]", username):
            raise forms.ValidationError("Only letters and numbers allowed in username")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email):
            raise forms.ValidationError("A user with that email address already exists")
        return email

    def clean(self):
        pass1 = self.cleaned_data.get('password1', '')
        pass2 = self.cleaned_data.get('password2', '')
        if not pass1 == pass2:
            raise forms.ValidationError("Password fields must match")
        return self.cleaned_data

class tcdPasswordResetForm(forms.Form):

    new_password1 = forms.CharField(min_length=8,
                                    widget=forms.widgets.PasswordInput(),
                                    label="New Password:")
    new_password2 = forms.CharField(min_length=8,
                                    widget=forms.widgets.PasswordInput(),
                                    label="New Password (again):")
    code = forms.CharField(max_length=32, widget=forms.widgets.HiddenInput(),
                           required=False)

    def clean(self):
        pass1 = self.cleaned_data.get('new_password1', '')
        pass2 = self.cleaned_data.get('new_password2', '')
        if not pass1 == pass2:
            raise forms.ValidationError("New password fields must match.")
        return self.cleaned_data

class tcdLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.widgets.PasswordInput(),
                               label="Password")

class forgotForm(forms.Form):
    email = forms.EmailField(label="Email")
    def clean(self):
        if not User.objects.filter(email=self.cleaned_data.get('email', '')):
            raise forms.ValidationError("email address not found")
        return self.cleaned_data

class FeedbackForm(forms.Form):
    subject = forms.CharField(max_length=140, label="Subject",
                              widget=forms.widgets.TextInput(attrs={'size': 50}), required=False)
    message = forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                   'rows': 10,
                                                                   'cols': 70}))

    def clean_subject(self):
        subj = self.cleaned_data.get('subject', '')
        if subj == '':
            subj = "GreaterDebater Feedback"
        return subj
