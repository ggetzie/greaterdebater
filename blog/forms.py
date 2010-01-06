from django import forms

class PostEdit(forms.Form):
    id = forms.IntegerField(widget = forms.widgets.HiddenInput(), required=False)
    title = forms.CharField(max_length=140, label="Title",
                            widget = forms.TextInput(attrs={'size':'70'}))
    tags = forms.CharField(label="Tags", widget=forms.TextInput(attrs={'size':'70'})
                           required=False, 
                           help_text="Words or short phrases that describe the blog post, comma separated")
    txt = forms.CharField(label="Text",
                               widget = forms.widgets.Textarea(attrs={'class': 'required icomment',
                                                                      'rows': 50,
                                                                      'cols':80}))

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
    if tags:
        tags = tags.split(',')
        return ','.join([tag.strip().lower() for tag in tags])
    else:
        return ''
                           
