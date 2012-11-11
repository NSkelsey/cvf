import re

from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User

import models

class PostForm(ModelForm):
    class Meta:
        model = models.Post
        fields = ('title','summary', 'body')
        widgets = {
                "body" : Textarea(attrs={'cols':200,'rows':10}),
                }

class CommentForm(ModelForm):
    class Meta:
        model = models.Post
        fields = ('summary',)
        widgets = {
                "summary" : Textarea(attrs={'cols':150,'rows':5}),
                }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
                "password" : forms.PasswordInput
                }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=30)


class VoteForm(forms.Form):
    pass

class RelVoteForm(forms.Form):
    pass


class RelPositionForm(forms.Form):
    position = forms.IntegerField()
    post_id = forms.IntegerField()


class AliasForm(forms.Form):
    name = forms.CharField()

    def clean(self):
        cleaned_data = super(AliasForm, self).clean()
        name = cleaned_data.get("name")
        if len(name) <= 0:
            raise forms.ValidationError("Name cannot be empty")
        upper = "[A-Z]"
        num = "[0-9]" #\d
        if re.search(upper, name) and re.search(num, name):
            return cleaned_data
        else:
            raise forms.ValidationError("Aliases must have at least one uppercase letter and one number.")
