from datetime import datetime, timedelta
from random import randrange
from django.utils import timezone

from models import RelVote
NUM_RELVOTES = 10

period = 60
tdelta = timedelta(minutes=1)

class RelList:
    votes = []

    def __init__(self, votes):
        self.votes = sorted(votes, key=lambda vote: vote.date_expire)

    def save_votes(self):
        for vote in self.votes:
            vote.save()

    def regen_vote_expires(self, post):
        now = datetime.now()
        new_vote = self.votes.pop(0)
        new_vote.post = post
        i = 0
        first = -1
        for vote in self.votes:
            if vote.date_expire > now:
                if first == -1:
                    first = i
                    if i == 0 and (vote.date_expire - tdelta) > now:
                        lower_delta = (vote.date_expire - now).total_seconds()
                        remainder = lower_delta%period
                        if remainder > .20*period:
                            offset = randrange(int(.25*period), period)
                        else:
                            offset = remainder
                        vote.date_expire = now + timedelta(seconds=offset)
                else:
                    vote.date_expire = self.votes[first].date_expire + tdelta*(i - first)
            i += 1
        new_vote.date_expire = self.votes[-1].date_expire + tdelta
        self.votes.append(new_vote)
        self.save_votes()






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




