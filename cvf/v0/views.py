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

from IPython import embed

import models
from forms import PostForm, UserForm, LoginForm, VoteForm, RelVoteForm, RelPositionForm
from models import Post, Vote, RelVote
from rvotes import get_next_avail_vote, create_relvotes, RelList, make_vote_list
import rvotes

from alchemy_hooks import DBSession
from alchemy_models import v0_relvote


def home(request):
    posts = models.Post.objects.all()
    return render_to_response("home.html",
            {"posts": posts},
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
    children = list(Post.objects.filter(parent=post)\
            .annotate(num_votes=Count('vote'))\
            .order_by('-num_votes'))
    pform = PostForm()
    """if len(children) > 3:
        children = [{'post': p, 'childs': p.children.all()} for p in children]
    else:
        children = [{'post': p, 'childs': p.children.all()[0:2]} for p in children]
    """
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


def profile(request, username):
    temp_args = {}
    if request.user.is_authenticated and request.user.username == username:
        temp_args["my_profile"] = True
    user = User.objects.get(username=username)
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
    return render_to_response('profile.html',
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


