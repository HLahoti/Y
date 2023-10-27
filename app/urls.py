from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.home,name="home"),
    path("login/",views.loginUser,name="login"),
    path("register/",views.registerUser,name="register"),
    path("logout/",views.logoutUser,name="logout"),
    path("updateuser/<str:pk>/", views.userupdate, name="update-user"),
    path("profile/<str:pk>/",views.profile,name="profile"),
    path("thread/<str:pk>/",views.thread,name="thread"),
    path("likepost/<int:pk>/", views.likepost, name="like-post"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name='post-delete'),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name='post-update'),
]
