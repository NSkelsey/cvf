from django import template
from cvf.v0.models import RelVote
from datetime import datetime

register = template.Library()

@register.filter(name='rel_count')
def field_type(value):
    now = datetime.now()
    post = value
    rvl = RelVote.objects.filter(post=post, date_expire__gt=now).all()
    return len(rvl)


