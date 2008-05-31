from django import newforms as forms
from django.contrib.auth.models import User
from django.contrib import auth
attrs_dict = {'class': 'required'}

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

class tcdLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.widgets.PasswordInput(),
                               label="Password")

class tcdTopicSubmitForm(forms.Form):
    title = forms.CharField(max_length=140, label="Title")
    url = forms.URLField(label="URL", required=False)
    comment = forms.CharField(label="Text",
                              widget=forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                   'rows': 5,
                                                                   'cols': 50}))

    def clean_url(self):
        url = self.cleaned_data.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            return 'http://' + url
        else:
            return url
