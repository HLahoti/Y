from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("login/",views.loginUser,name="login"),
    path("register/",views.registerUser,name="register"),
    path("logout/",views.logoutUser,name="logout"),
    path("profile/<str:pk>/",views.profile,name="profile"),
]
