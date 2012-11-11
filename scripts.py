import re
import random
import argparse


from django.core.management import setup_environ
from cvf import settings
from bs4 import BeautifulSoup
from IPython import embed

setup_environ(settings)
from django.contrib.auth.models import User
from cvf.v0.models import Post, Vote, RelVote
import cvf.v0.view_funcs as view_funcs
from datetime import datetime
never = datetime(2022,1,1)

harry = User.objects.order_by('?')
if len(harry) > 0:
    harry = harry[0]
else:
    harry = User(username="harry")
    harry.set_password("a")
    harry.save()
print type(harry)

def get_uname(words):
    first = words[int(random.random()*len(words))]
    second = words[int(random.random()*len(words))]
    uname = first+"_"+second
    if len(uname) > 30 or len(uname) < 5:
        return get_uname(words)
    else:
        return uname

def make_user(itr=1):
    f = open("war_and_peace.txt")
    book = f.read()
    words = book.split(" ")
    for i in range(itr):
        uname = get_uname(words)
        view_funcs.make_new_user(uname, "a")


def make_post(itr=1):
    f = open("war_and_peace.txt")
    book = f.read()
    for j in range(itr):
        i = int(random.random()*(len(book)-200))
        g = int(random.random()*(len(book)-8000))
        title_sec = book[i:i+int(random.random()*20)]
        post_sec = book[g:g+int(random.random()*70)]
        sum_sec = book[g:g+int(random.random()*120)]
        if random.random()*2 > .25 and j > 3:
            parent = Post.objects.order_by('?')[0]
        else:
            parent = None
        user=User.objects.order_by('?')[0]
        post = Post(title=title_sec, body=post_sec, user=user,
                username=user.username, summary=sum_sec, parent=parent)
        post.save()

def rand_posts():
    initial_post = Post(title="first", body="yes", user=User(), username="Wee")
    make_user(15)
    make_post(100)

def soup_recurse(html):
    for sub in html.contents:
        try:
            sub.__dict__['name']
        except (TypeError, KeyError) as e:
            print "idied"
            print sub
            continue
        if sub.name == 'p':
            make_souppost(sub)
        if sub.name == 'div':
            make_soupcomment(sub)

def create_votes(html, post):
    rvotes, votes = (0, 0)
    try:
        votes = html['votes']
        votes = int(votes)
    except Exception:
        pass
    try:
        rvotes = html['rvotes']
        rvotes = int(rvotes)
    except Exception:
        pass
    for i in range(votes):
        vote = Vote(post=post, user=harry)
        vote.save()
    for i in range(rvotes):
        rvote = RelVote(post=post, user=harry, date_expire=never)
        rvote.save()
        


def make_souppost(posthtml):
    title = posthtml.a.text
    summary = posthtml.em
    if summary is None:
        summary = "auto generated"
    else:
        summary = posthtml.em.text
    post = Post(username='harry', user=harry, title=title, summary=summary)
    post.save()
    soup_recurse(posthtml)
    create_votes(posthtml, post)



def make_soupcomment(html):
    summary = html.text
    if summary is None:
        summary = "auto generated"
    print html.parent
    if html.parent.name == 'p' or html.parent.name == 'div':
        parent = Post.objects.filter(title=html.parent.a.
                text).all()[0]
        post = Post(username='harry', comment=True, 
                summary=summary, user=harry,          
                parent=parent)
    else:
        post = Post(username='harry',user=harry, comment=True, summary=summary)
    print "parent post"
    print post.parent
    post.save()
    soup_recurse(html)
    create_votes(html, post)

def make_copy():
    f = open("CPF_Content.txt", "r+")
    html = f.read()
    soup = BeautifulSoup(html)
    for sub in soup.contents:
        try:
            sub.__dict__['name']
        except (TypeError, KeyError) as e:
            print sub
            continue
        if sub.name == 'p':
            make_souppost(sub)
        elif sub.name == 'div':
            make_soupcomment(sub)


if __name__ == "__main__":


    parser = argparse.ArgumentParser() 
    parser.add_argument('-p', type=str, help='Program name',
           )
    parser.set_defaults(program="harry")
    args = parser.parse_args()
    if not args.program:
        print "no prog"
    if args.program == "harry":
        make_copy()
    elif args.program =="random":
        rand_posts() 

