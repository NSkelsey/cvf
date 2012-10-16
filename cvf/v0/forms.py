from django import forms
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User

import models

class PostForm(ModelForm):
    class Meta:
        model = models.Post
        fields = ('title', 'body')
        widgets = {
                "body" : Textarea(attrs={'cols':200,'rows':10}),
                }

class UserForm(forms.Form):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
                "password" : forms.PasswordInput
                }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=30)


