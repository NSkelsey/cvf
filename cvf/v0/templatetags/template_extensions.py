from django import template
from cvf.v0.models import RelVote
from datetime import datetime

from sqlalchemy import select, func, and_

from cvf.v0.alchemy_hooks import Session, sa_post, sa_relvote

register = template.Library()

@register.filter(name='rel_count')
def field_type(value):
    session = Session()
    now = datetime.now()
    post = value
    sel = select([func.count(sa_relvote.c.id)], whereclause=(and_(sa_relvote.c.post_id==post.id, sa_relvote.c.date_expire > now)), from_obj=[sa_relvote]).group_by(sa_relvote.c.post_id)
    rvl = session.execute(sel).fetchall()
    print rvl
    if len(rvl) > 0:
        return int(rvl[0][0])
    else:
        return 0


