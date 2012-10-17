from django.db import models
from django.contrib.auth.models import User

constants = {
        "Post" : {
            "body" :  {
                "max_length" : 8000,
                },
            },
        }

class Post(models.Model):
    title = models.CharField(max_length=120)
    body = models.CharField(max_length=constants["Post"]["body"]["max_length"])
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.BooleanField(blank=True)
    edited = models.BooleanField(blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")
    identifier = models.IntegerField(default=0)

    def __repr__(self):
        return u"<PostO title: %s>" % (self.title)

class Revision(models.Model):
    post = models.ForeignKey(Post)
    date_stored = models.DateTimeField(auto_now=True)
    body  = models.CharField(max_length=constants["Post"]["body"]["max_length"])

class Vote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    parent_post = models.ForeignKey(Post, related_name="child_vote", null=True)

class RelVote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    parent_post = models.ForeignKey(Post, related_name="child_relvote")
    date_expire = models.DateTimeField()
    _next = models.ForeignKey('self', null=True)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    authd = models.BooleanField()

