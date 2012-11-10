from datetime import datetime, timedelta
from random import randrange
from django.utils import timezone

from models import RelVote
NUM_RELVOTES = 10

# change these as nessecary
period = 60
tdelta = timedelta(minutes=1) #must change minutes to reflect correct units

class RelList:
    votes = []

    def __init__(self, votes):
        self.votes = sorted(votes, key=lambda vote: vote.date_expire)

    def save_votes(self):
        for vote in self.votes:
            vote.save()

    def make_data_fs(self,):
        data = {
        'form-TOTAL_FORMS': u'10',
        'form-INITIAL_FORMS': u'0',
        'form-MAX_NUM_FORMS': u'10',
        }

        votes = self.votes
        i = 0
        for vote in votes:
            s = "form-" + str(i) + "-position"
            t = "form-" + str(i) + "-post_id"
            data[s] = i
            _id = None
            if vote.post is not None:
                _id = vote.post.id
            data[t] = _id
            i += 1
        return data

    def push_vote_regen(self, post):
        now = datetime.now()
        new_vote = self.votes.pop(0)
        new_vote.post = post
        i = 0
        first = -1
        offset= period
        for vote in self.votes:
            if vote.date_expire > now:
                if first == -1:
                    first = i
                    diff = timedelta(seconds=offset) + tdelta*i
                    vote.date_expire = now + diff
                else:
                    diff = timedelta(seconds=offset) + tdelta*i
                    print "time diff " + str(diff)
                    vote.date_expire = now + diff
            i += 1
        if first == -1:
            new_vote.date_expire = now + tdelta*(len(self.votes) + 1)
        else:
            new_vote.date_expire = self.votes[-1].date_expire + tdelta
        self.votes.append(new_vote)
        self.save_votes()

    def update_expire_time(self):
        now = datetime.now()
        for i in range(len(self.votes)):
            self.votes[i].date_expire = now + tdelta*(i+1)
        self.save_votes()


def make_vote_list(order, user):
    votes = RelVote.objects.filter(user=user).all()
    votes = sorted(votes, key=lambda vote: vote.date_expire)
    for i in range(len(votes)):
        post_id = order[i]
        votes[i].post_id = post_id
    return votes


def create_relvotes(user):
    li = []
    for i in range(NUM_RELVOTES):
        new_vote = RelVote(user=user, date_expire=datetime.now())
        li.append(new_vote)
        new_vote.save()
    # do something with li
    return True

def get_next_avail_vote(votes):
    v = None
    for vote in votes:
        if vote.post is None:
            v = vote
            print "null vote"
        else:
            print vote.post.title
    return v




