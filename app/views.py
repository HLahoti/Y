from django.shortcuts import render,redirect, get_object_or_404
from .models import Udata,Topic,Posts
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm,PostForm, UserUpdateForm
from django.db.models import Q, Count, Sum
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView, UpdateView
import re
from django.utils.html import escape
from django.utils.safestring import mark_safe

# Create your views here.
def loginUser(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,"User does not exist")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect("home")
        else:
            messages.error(request,"Incorrect username/password")

    page = 'login'
    variables = {
        "page":page,
    }
    return render(request,"login_register.html",variables)

def registerUser(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method=="POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            if form.clean_password1() == form.clean_password2():
                curr_users = Udata.objects.filter(
                    Q(name=form.clean_name()) |
                    Q(username=form.clean_username()) |
                    Q(email=form.clean_email())
                )
                if curr_users.all().count() == 0:
                    user = User.objects.create_user(
                        form.clean_username(),
                        form.clean_email(),
                        form.clean_password1(),
                    )
                    user.first_name = form.clean_name()
                    user.save()
                    udata = Udata.objects.create(
                        userid=user,
                        name=user.first_name,
                        username = user.username,
                        email = user.email,
                    )
                    udata.save()
                messages.success(request, f'Account created for { udata.username }!')
                return redirect("login")

    form = UserRegistrationForm()
    page = 'register'
    variables = {
        "page":page,
        "form":form,
    }
    return render(request,"login_register.html",variables)

def logoutUser(request):
    logout(request)
    return redirect("home")

def home(request):
    q = request.GET.get("q") if request.GET.get("q") else ""

    posts = Posts.objects.annotate(total_likes=Count('likes')).filter(
        Q(body__icontains=q) | Q(topics__name=q) | Q(user__username__icontains=q)
    ).order_by("-created","-likes")[:10]
    topics = Topic.objects.annotate(total_posts=Count('posts')).order_by("-total_posts")
    topics = topics[:10]

    if request.method == "POST":
        body = request.POST.get("body")
        post = Posts.objects.create(
            user=request.user,
            body=body
        )
      
        tagged = body.split()
        if len(tagged)>1:
            tags = [i[1:31].lower() for i in tagged if i[0]=='#' and len(i)>1]
            for i in tags:
                if not Topic.objects.filter(name=i).exists():
                    new_topic = Topic.objects.create(name=i)
                    new_topic.save()
                else:
                    new_topic = Topic.objects.get(name=i)
                post.topics.add(new_topic)
        
        post.save()
        return redirect("home")

    post_form = PostForm()

    all_users = Udata.objects.all().values_list('username', flat=True)
    all_topics = Topic.objects.all().values_list('name', flat=True)
    tagging(all_users, all_topics, posts)
    variables = {
        "posts": posts,
        "post_form": post_form,
        "topics": topics,
        # "page":"home",
    }
    return render(request,"index.html",variables)

def thread(request,pk):
    og_post = Posts.objects.get(id=pk)
    replies = Posts.objects.filter(parent=og_post).order_by("-created","-likes")[:10]
    parentage = True if og_post.parent else False
    thread = []
    thread_post = og_post
    while(thread_post.parent and len(thread)<=3):
        thread_post = thread_post.parent
        thread.append(thread_post)
    thread = thread[::-1]

    if request.method=="POST":
        body = request.POST.get("body")
        tagged = body.split()
        post = Posts.objects.create(
            user=request.user,
            body=body,
            parent=og_post
        )

        if len(tagged)>1:
            tags = [i[1:31].lower() for i in tagged if i[0]=='#' and len(i)>1]
            for i in tags:
                if not Topic.objects.filter(name=i).exists():
                    new_topic = Topic.objects.create(name=i)
                    new_topic.save()
                    post.topics.add(new_topic)
                else:
                    new_topic = Topic.objects.get(name=i)
                post.topics.add(new_topic)

        post.save()
        return redirect("thread",pk=pk) 
    
    post_form = PostForm()
    all_users = Udata.objects.all().values_list('username', flat=True)
    all_topics = Topic.objects.all().values_list('name', flat=True)

    # parent
    tagging(all_users, all_topics, thread)

    #replies
    for post in replies:
        mentioned_usernames = re.findall(r'@(\w+)', post.body)
        mentioned_usernames = filter(lambda x: x in all_users, mentioned_usernames)
        for username in mentioned_usernames:
            mentioned_user = Udata.objects.get(username=username)
            profile_url = reverse('profile', kwargs={'pk': mentioned_user.userid_id})
            post.body = post.body.replace(f'@{username}', mark_safe(f'<a href="{ profile_url }">@{username}</a>'))

    for post in replies:
        mentioned_topics = re.findall(r'#(\w+)', post.body)
        mentioned_topics = filter(lambda x: x in all_topics, mentioned_topics)
        for topic in mentioned_topics:
            mention = Topic.objects.get(name=topic)
            topic_thread_url = mark_safe(f"/?q={mention.name}")
            post.body = post.body.replace(f'#{topic}', f'<a href="{topic_thread_url}">#{topic}</a>')

    #original_post
    mentioned_usernames = re.findall(r'@(\w+)', og_post.body)
    mentioned_usernames = filter(lambda x: x in all_users, mentioned_usernames)
    for username in mentioned_usernames:
        mentioned_user = Udata.objects.get(username=username)
        profile_url = reverse('profile', kwargs={'pk': mentioned_user.userid_id})
        og_post.body = og_post.body.replace(f'@{username}', mark_safe(f'<a href="{ profile_url }">@{username}</a>')) 

    mentioned_topics = re.findall(r'#(\w+)', og_post.body)
    mentioned_topics = filter(lambda x: x in all_topics, mentioned_topics)
    for topic in mentioned_topics:
        mention = Topic.objects.get(name=topic)
        topic_thread_url = mark_safe(f"/?q={mention.name}")
        og_post.body = og_post.body.replace(f'#{topic}', f'<a href="{topic_thread_url}">#{topic}</a>')

    variables = {
        "post":og_post,
        "posts":replies,
        "post_form":post_form,
        "parentage":parentage,
        "thread":thread,
    }
    return render(request,"thread.html",variables)

def profile(request,pk):
    q = request.GET.get("q") if request.GET.get("q") else ""
    userdata = Udata.objects.get(userid=pk)
    posts = Posts.objects.filter(
        Q(user__id=pk) & Q(Q(body__icontains=q) | Q(topics__name=q))
    ).order_by("-created","-likes")[:10]
    
    topics = Topic.objects.annotate(total_posts=Count('posts__topics')).order_by("-total_posts")[:10]
    userposts = Posts.objects.filter(user = pk).count()
    all_users = Udata.objects.all().values_list('username', flat=True)
    all_topics = Topic.objects.all().values_list('name', flat=True)
    tagging(all_users, all_topics, posts)
    variables = {
        "userdata":userdata,
        "posts":posts,
        "topics":topics,
        'userposts': userposts
        # "page":"profile",
    }
    return render(request,"profile.html",variables)

# @login_required
# def update_user(request):
#     user = request.user
#     form = UserRegistrationForm(instance=user)

@login_required
def userupdate(request, pk):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user.udata)
        if u_form.is_valid():
            u_form.save()
            username = u_form.cleaned_data.get('username')
            messages.success(request, f'Profile updated for { username }!')
            return redirect('profile', pk=pk)
    else:
        up_form = UserUpdateForm(instance=request.user.udata)
        context = {
            'up_form': up_form,
        }
        return render(request, "userupdate.html", context)

# @login_required
# def likepost(request, pk):
#     post = get_object_or_404(Posts, id=request.POST.get('post_id'))
#     if request.user.udata not in post.likes.all():
#         post.likes.add(request.user.udata)
#         post.save()
#     return HttpResponseRedirect(reverse('thread', args=[str(pk)]))

@login_required
def like_post(request, pk):
    if request.method == 'POST':
        userdata = request.user.udata
        # Retrieve the post and add the user to the likes field
        post = get_object_or_404(Posts, id=pk)
        if userdata not in post.likes.all():
            post.likes.add(userdata)
            post.save()
            like_count = post.likes.count()
            return JsonResponse({'message': 'Post liked successfully', 'like_count': like_count})  
        else:
            return JsonResponse({'message': 'You have already liked this post'})

    return JsonResponse({'message': 'Invalid request'}, status=400)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Posts
    fields = ['body']
    template_name = 'post_form.html'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False 

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Posts
    template_name = 'post_confirm_delete.html'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False
    success_url = reverse_lazy('home')


def about(request):
    return render(request, 'about.html')

def usermentions(request, pk):
    userdata = Udata.objects.get(userid=pk)
    posts = Posts.objects.filter(
        ~Q(user__id=pk) & Q(body__icontains='@'+userdata.username)
    ).order_by("-created","-likes")[:10]
    
    topics = Topic.objects.annotate(total_posts=Count('posts__topics')).order_by("-total_posts")[:10]
    variables = {
        "userdata":userdata,
        "posts":posts,
        "topics":topics,
        # "page":"profile",
    }
    return render(request, 'user_mentions.html', variables)

def tagging(all_users, all_topics, posts):
    for post in posts:
        mentioned_usernames = re.findall(r'@(\w+)', post.body)
        mentioned_usernames = filter(lambda x: x in all_users, mentioned_usernames)
        for username in mentioned_usernames:
            mentioned_user = Udata.objects.get(username=username)
            profile_url = reverse('profile', kwargs={'pk': mentioned_user.userid_id})
            post.body = post.body.replace(f'@{username}', mark_safe(f'<a href="{ profile_url }">@{username}</a>'))
    for post in posts:
        mentioned_topics = re.findall(r'#(\w+)', post.body)
        mentioned_topics = filter(lambda x: x in all_topics, mentioned_topics)
        for topic in mentioned_topics:
            mention = Topic.objects.get(name=topic)
            topic_thread_url = mark_safe(f"/?q={mention.name}")
            post.body = post.body.replace(f'#{topic}', mark_safe(f'<a href="{topic_thread_url}">#{topic}</a>'))
