from tcd.comments.models import TopicComment
from tcd.items.models import Topic, Tags
from tcd.profiles.models import Profile
from tcd.settings import HOSTNAME
from tcd.base_utils import update_tags

from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404

import re
import datetime

attrs_dict = {'class': 'required'}

class tcdTopicSubmitForm(forms.Form):
    title = forms.CharField(max_length=140, label="Title", widget=forms.TextInput(attrs={'size': '70'}))
    url = forms.URLField(label="URL", required=False,
                         help_text="Leave the URL field blank to submit a self-referential topic.",
                         widget=forms.TextInput(attrs={'size': '70'}))
    tags = forms.CharField(label="Tags", widget=forms.TextInput(attrs={'size':'70'}),
                           required=False,
                           help_text = """Words or short phrases that describe the topic separated by commas <br />
e.g. Politics, Technology, Funny""")
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
        
    def save(self, prof):

        topic = Topic(user=prof.user,
                      title=self.cleaned_data['title'],
                      score=1,
                      sub_date=datetime.datetime.now(),
                      comment_length=0,
                      last_calc=datetime.datetime.now(),
                      needs_review=prof.probation, # topics from probationary users must be approved
                      spam = prof.shadowban, # if user is a known spammer, mark as spam right away

                      )
        topic.save()
        topic.url = self.cleaned_data['url'] and self.cleaned_data['url'] or (HOSTNAME + '/' + str(topic.id) + '/')
        topic.save()

        dtags = self.cleaned_data['tags']
        if dtags:
            # create the count of all tags for the topic
            tags = '\n'.join([dtags, ','.join(['1']*(dtags.count(',')+1))])
            topic.tags = tags

            # create a Tags object to indicate the submitter
            # added these tags to this topic                        
            utags = Tags(user=prof.user, topic=topic, tags=dtags)
            utags.save()

            # update the count of all tags used by the submitter
            prof.tags = update_tags(prof.tags, dtags.split(','))
            prof.save()

            topic.save()

        prof.last_post = topic.sub_date
        prof.save()

        if prof.followtops:
            topic.followers.add(prof.user)
            topic.save()

        if self.cleaned_data['comment']:
            comment = TopicComment(user=prof.user,
                                   ntopic=topic,
                                   pub_date=datetime.datetime.now(),
                                   comment=self.cleaned_data['comment'],
                                   first=True,
                                   nparent_id=0,
                                   nnesting=0,
                                   spam=prof.shadowban,
                                   needs_review=prof.probation)
            comment.save()

            topic.comment_length += len(comment.comment)
            topic.recalculate()
            topic.save()
        return topic
        
class TagEdit(forms.Form):
    topic_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    source = forms.IntegerField(widget=forms.widgets.HiddenInput())
    # source = 0: Topic list page (new topics/hot topics)
    # source = 1: User tags page (saved topics)
    tags = forms.CharField(label="Tags", widget=forms.TextInput(attrs={'size':'70'}),
                           help_text = """Words or short phrases that describe the topic separated by commas <br />
e.g. Politics, News, Current Events""")

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tags = tags.split(',')
        tags = ','.join([tag.strip().lower() for tag in tags])            
        if re.search("[^\w\s!@\?\$%#,&']", tags):
            raise forms.ValidationError(
                "Only letters, numbers, spaces and characters _ ! @ ? $ % # ' & are allowed in tags")                
        return tags

class TagRemove(forms.Form):
    topic_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    tag = forms.CharField(widget=forms.widgets.HiddenInput())

class Flag(forms.Form):
    object_id = forms.IntegerField(widget=forms.widgets.HiddenInput())

class Ballot(forms.Form):
    argument = forms.IntegerField(widget=forms.widgets.HiddenInput())
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

class Concession(forms.Form):
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())


class Response(forms.Form):
    arg_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    user_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    response = forms.TypedChoiceField(widget=forms.widgets.HiddenInput(), 
                                      choices=[(0, 'accept'), (1, 'decline')],
                                      coerce=int)

class DecideForm(forms.Form):
    id_list = forms.CharField(widget=forms.widgets.HiddenInput(), initial="")
    decision = forms.TypedChoiceField(choices=[(0, 'approve'), (1, 'spam'), (2, 'reject')], coerce=int)
    
