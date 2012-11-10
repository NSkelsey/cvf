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
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=constants["Post"]["body"]["max_length"])
    user = models.ForeignKey(User)
    username = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.BooleanField(blank=True)
    edited = models.BooleanField(blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children")
    identifier = models.IntegerField(default=0)

    def __repr__(self):
        relvotes = int(self.relvote_set.count())
        votes = int(self.vote_set.count())
        return u"<Post title: %s, Num votes: %s, Num Relvotes %s>" % (self.title, votes, relvotes)

class Revision(models.Model):
    post = models.ForeignKey(Post)
    date_stored = models.DateTimeField(auto_now=True)
    body  = models.CharField(max_length=constants["Post"]["body"]["max_length"])

class Vote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    parent_post = models.ForeignKey(Post, related_name="child_vote", null=True)

    def __repr__(self):
        title = "NULL"
        if self.post is not None:
            dst = 25 if len(self.post.title) > 25 else len(self.post.title)
            title = self.post.title[0:dst]
        return u"<Vote: Post Title %s >" % (title)


class RelVote(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post, null=True)
    parent_post = models.ForeignKey(Post, related_name="child_relvote", null=True)
    date_expire = models.DateTimeField()
    _next = models.ForeignKey('self', null=True)

    def __repr__(self):
        title = "NULL"
        if self.post is not None:
            dst = 25 if len(self.post.title) > 25 else len(self.post.title)
            title = self.post.title[0:dst]
        return u"<Relvote: Post Title %s >" % (title)


#cronjob will run through and expire these votes
class ExpiredRelVote(RelVote):
    date_retired = models.DateTimeField(auto_now=True)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, related_name="profile")
    authd = models.BooleanField()

class Alias(models.Model):
    aname = models.CharField(max_length=20)
    user = models.ForeignKey(User, unique=True, related_name="aliases")


