from sqlalchemy import select, func, outerjoin

from alchemy_hooks import session, sa_post

from cvf.v0.models import Post, RelVote

expr = ""

#10 for now
def load_top_40(post):
    a = sa_post.alias()
    expr =  outerjoin(a, sa_post, a.c.parent_id == sa_post.c.id)
    for i in range(1):
        new_a = sa_post.alias()
        expr = outerjoin(expr, new_a, expr.c.v0_post_id == new_a.c.parent_id)
    return expr








