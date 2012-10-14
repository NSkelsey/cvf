import django
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import auth
from django.forms.util import ErrorList
from django.db.models import Count

import models
from forms import PostForm, UserForm, LoginForm
from models import Post
from IPython import embed

def home(request):
    posts = models.Post.objects.all()
    return render_to_response("home.html",
            {"posts": posts},
            RequestContext(request))

def make_post(request):
    pform = PostForm(request.POST or None)
    if request.method == "POST":
        if pform.is_valid():
            post = pform.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect("/")
    return render_to_response("post_form.html",
            {"pform" : pform, 'dont_add_ret_url': True},
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


def post_view(request, id_num, pform=None):
    post = get_object_or_404(Post, pk=id_num)
    children = Post.objects.filter(parent=post)\
            .annotate(num_votes=Count('vote'))\
            .order_by('-num_votes')
    pform = PostForm()
    return render_to_response('post.html',
            {'post' : post, 'children':children, 'pform': pform},
            RequestContext(request))

def sub_post(request, id_num): #for nested posts
    pform = PostForm(request.POST or None)
    parent = get_object_or_404(Post, pk=id_num)
    if (request.method == 'POST'
            and pform.is_valid()
            and request.user.is_authenticated()):
        post = Post(title=pform.cleaned_data["title"],
                    body=pform.cleaned_data["body"],
                    parent=parent,
                    user=request.user)
        post.save()
    return HttpResponseRedirect("/posts/"+id_num)







