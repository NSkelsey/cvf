from datetime import datetime

from django.contrib.auth.models import User
import models
from sqlalchemy import select, func, alias, and_
from IPython import embed

from alchemy_hooks import Session, sa_post, sa_relvote, sa_vote
import rvotes

def preload_front():
    session = Session()
    now = datetime.now()
    sel = select([sa_post,
        func.count(sa_relvote.c.id).label('rel_count'),],
            whereclause=and_(sa_post.c.parent_id==None,),
            from_obj=[sa_post,
            sa_post.outerjoin(sa_relvote, and_(sa_post.c.id==sa_relvote.c.post_id,
                                               sa_relvote.c.date_expire > now)),
            ]
            ).group_by(sa_post.c.id)
    rvote_count = alias(sel)
    sel = select([sa_post, rvote_count.c.rel_count,
        func.count(sa_vote.c.id).label('vote_count')],
            whereclause=and_(sa_post.c.parent_id==None,sa_post.c.id==rvote_count.c.id),
            from_obj=[sa_post, rvote_count,
            sa_post.outerjoin(sa_vote, and_(sa_post.c.id==sa_vote.c.post_id)),
            ]
            ).group_by(sa_post.c.id).order_by('-rel_count')
    posts = session.execute(sel).fetchall()
    td =  datetime.now() - now
    print "time delay is " + str(td.microseconds/1000)
    return posts

def make_vid_sets(uid):
    session = Session()
    vsel = select([sa_vote.c.post_id], whereclause=sa_vote.c.user_id==uid,  #DJANGO USERID
                 from_obj=[sa_vote])
    vote_set = set([_id[0] for (_id) in session.execute(vsel).fetchall()])
    rvsel = select([sa_relvote.c.post_id],
            whereclause=and_(sa_relvote.c.user_id==uid, rvotes.now_clause()),
            from_obj=[sa_relvote])
    rvote_set = set([_id[0] for (_id) in session.execute(rvsel).fetchall()])
    return (vote_set, rvote_set)



def make_new_user(username, password):
    user = User.objects.create_user(username, password=password)
    user.save()
    alias = models.Alias(user=user, name=user.username)
    alias.save()
    rvotes.create_relvotes(user) 
    return user



