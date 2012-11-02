from datetime import datetime

import django
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import auth, messages
from django.forms.util import ErrorList
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory
from sqlalchemy import select, func
from IPython import embed

import models
from forms import PostForm, UserForm, LoginForm, VoteForm, RelVoteForm, RelPositionForm, AliasForm
from models import Post, Vote, RelVote
from rvotes import get_next_avail_vote, create_relvotes, RelList, make_vote_list
from alchemy_hooks import session, sa_post, sa_relvote
import rvotes

def home(request):
    posts = models.Post.objects.all()
    return render_to_response("home.html",
            {"posts": posts},
            RequestContext(request))

def principles(request):
    return render_to_response("principles.html",
            {},
            RequestContext(request))

def information(request):
    users = User.objects.all()
    return render_to_response("information.html",
            {'users' : users},
            RequestContext(request))

def most_relevant(request):
    timer = datetime.now()
    join = sa_post.join(sa_relvote, onclause=(sa_relvote.c.post_id==sa_post.c.id))
    sel = select([sa_post.c.id, func.count(sa_relvote.c.id).label("votes")], whereclause=sa_relvote.c.date_expire > datetime.now(), 
            from_obj=[join]).group_by(sa_post.c.id).order_by("votes DESC")
    ps = session.execute(sel).fetchall()
    print ps
    delta = datetime.now() - timer
    print delta
    if not ps:
        messages.info(request, "This site has nothing relevant green vote on something")
    try:
        _id = ps[0][0]
        post = Post.objects.get(pk=_id)
    except:
        post = Post.objects.get(pk=1)
    temp_args = {'post' : post}
    children = list(Post.objects.filter(parent=post)\
            .annotate(num_votes=Count('vote'))\
            .order_by('-num_votes'))
    temp_args['p_struct'] = children
    temp_args['prof_user'] = request.user
    return render_to_response("most_relevant.html",
            temp_args,
            RequestContext(request))

def most_discussed(request):
    sel = select([sa_post.c.parent_id, func.count(sa_post.c.id).label("childs")], 
            whereclause=(sa_post.c.parent_id != None),
            from_obj=[sa_post])\
            .group_by(sa_post.c.parent_id).order_by("childs DESC")
    p_id = session.execute(sel).first()[0]
    post = Post.objects.get(pk=p_id)
    temp_args = {'post' : post}
    children = list(Post.objects.filter(parent=post)\
            .annotate(num_votes=Count('vote'))\
            .order_by('-num_votes'))
    temp_args['p_struct'] = children
    temp_args['prof_user'] = request.user
    return render_to_response("most_discussed.html",
            temp_args,
            RequestContext(request))

def make_post(request): #for commiting posts to the forum proper
    pform = PostForm(request.POST or None)
    if request.method == "POST":
        if pform.is_valid():
            post = pform.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect("/")
    return render_to_response("post_form.html",
            {"pform" : pform, "dont_add_ret_url": True},
            RequestContext(request))

def login(request):
    log_form = LoginForm(request.POST or None)
    if request.method == "POST" and log_form.is_valid():
        username = log_form.cleaned_data["username"]
        password = log_form.cleaned_data["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect("/")
        else:
            errors = log_form._errors.setdefault(django.forms.forms.NON_FIELD_ERRORS, ErrorList())
            errors.append("Bad Username or password")
    return render_to_response("login.html",
            {"form":log_form},
            RequestContext(request))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

def create_user(request):
    uf = UserForm(request.POST or None)
    if request.method == 'POST' and uf.is_valid():
        user = User(username=uf.cleaned_data["username"],
                    )
        user.set_password(uf.cleaned_data["password"])
        user.save()
        create_relvotes(user)


        return HttpResponse("USER MADE with uname: %s and pw: %s"%(user.username, user.password))

    return render_to_response("create.html",
            {'uf': uf},
            RequestContext(request))

def post_view(request, id_num, pform=None):
    post = get_object_or_404(Post, pk=id_num)
    rel_o = Post.objects.select_related().filter(parent=post)\
            .annotate(num_votes=Count('vote'))\
            .order_by('-num_votes')
    children = list(rel_o)
    pform = PostForm()
    temp_args = {'post' : post, 'p_struct':children, 'pform': pform}
    temp_args['prof_user'] = request.user
    if request.user.is_authenticated():
        votes = RelVote.objects.filter(user=request.user).all()
        rel_o = RelList(votes)
        temp_args['rel_o'] = rel_o
        temp_args['now'] = datetime.now()
    return render_to_response('post.html',
            temp_args,
            RequestContext(request))

def sub_post(request, id_num): #for nested posts
    pform = PostForm(request.POST or None)
    parent = get_object_or_404(Post, pk=id_num)
    if (request.method == 'POST'
        and request.user.is_authenticated()):
        if pform.is_valid():
            title = pform.cleaned_data["title"]
            check = Post.objects.filter(title=title).order_by("-identifier")
            check_int = 0
            if len(check) > 0:
                check_int = check[0].identifier + 1
            post = Post(title=title,
                        body=pform.cleaned_data["body"],
                        parent=parent,
                        user=request.user,
                        identifier=check_int)
            post.save()
        else:
            return render_to_response("post_form.html",
                    {'pform' : pform, 'post':parent},
                    RequestContext(request))
    return HttpResponseRedirect("/posts/"+id_num)

@require_http_methods(["POST",])
def vote(request, id_num):
    vf = VoteForm(request.POST or None)
    post = get_object_or_404(Post, pk=id_num)
    if vf.is_valid() and request.user.is_authenticated():
        user = request.user
        prev_vote = Vote.objects.filter(user=user, parent_post=post.parent,)
        if prev_vote.exists():
            prev_vote.delete()
            messages.warning(request, 'Changing your vote because you already voted on some child of the parent post')
        vote  = Vote(post=post, parent_post=post.parent, user=user)
        vote.save()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required(login_url="/login", )
@require_http_methods(["POST",])
def rel_vote(request, id_num):
    rvf = RelVoteForm(request.POST)
    post = get_object_or_404(Post, pk=id_num)
    user = request.user
    if rvf.is_valid():
        votes = RelVote.objects.filter(user=user).all()
        rel_o = RelList(votes)
        rel_o.push_vote_regen(post)
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required(login_url="/login",)
def profile(request):
    user = request.user
    temp_args = {}
    temp_args['prof_user'] = user

    votes = RelVote.objects.filter(user=user).all()
    rel_o = RelList(votes)
    temp_args['rel_o'] = rel_o
    temp_args['now'] = datetime.now()

    RelPosFormSet = formset_factory(RelPositionForm, extra=9)
    data = rel_o.make_data_fs()
    rpfs = RelPosFormSet(data)
    temp_args['formset'] = rpfs
    formlist = []
    for i in range(len(rpfs)):
        formlist.append((rpfs[i], rel_o.votes[i]))
    temp_args['formlist'] = formlist
    temp_args['alias_form'] = AliasForm()
    return render_to_response('profile.html',
            temp_args,
            RequestContext(request))

@login_required(login_url="/login", )
@require_http_methods(["POST",])
def alias_sub(request):
    af = AliasForm(request.POST)
    if not af.is_valid():
        messages.error(request, af.errors)
    messages.info(request, "alias posted! nothing done")
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def user_profile(request, username):
    temp_args = {}
    if request.user.is_authenticated and request.user.username == username:
        return HttpResponseRedirect("/profile")
    user = User.objects.get(username=username)
    return render_to_response('user_profile.html',
            temp_args,
            RequestContext(request))

@login_required(login_url="/login")
@require_http_methods(["POST",])
def reorder_rvotes(request, username):
    user = User.objects.get(username=username)
    if request.user == user:
        RelPosFormSet = formset_factory(RelPositionForm)
        rpfs = RelPosFormSet(request.POST)
        order = []
        if rpfs.is_valid() and len(rpfs) == rvotes.NUM_RELVOTES:
            for i in range(len(rpfs)):
                form = rpfs[i]
                post_id  = form.cleaned_data["post_id"]
                order.append(post_id)
        votes = make_vote_list(order, user)
        rl = RelList(votes)
        rl.update_expire_time()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


