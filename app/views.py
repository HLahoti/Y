from django.shortcuts import render,redirect
from .models import Udata,Topic,Posts
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.db.models import Q, Count

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
    posts = Posts.objects.all()
    variables = {
        "posts":posts,
    }
    return render(request,"index.html",variables)


def profile(request,pk):
    userdata = Udata.objects.get(userid=pk)
    posts = Posts.objects.filter(user__id=pk)
    variables = {
        "userdata":userdata,
        "posts":posts,
    }
    return render(request,"profile.html",variables)
