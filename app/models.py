from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse


class Topic(models.Model):
    name = models.CharField(max_length=30,null=False)

    def __str__(self):
        return str(self.name)

class Udata(models.Model):
    userid = models.OneToOneField(User,on_delete=models.CASCADE,null=False)
    name = models.CharField(max_length=100,null=False)
    email = models.EmailField(null=False,unique=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg", upload_to='profile_pics')
    username = models.CharField(max_length=40,null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.username)

class Posts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=False)
    # title = models.CharField(max_length=20,null=True)
    body = models.TextField(max_length=300,null=False)
    parent = models.ForeignKey("self",null=True,on_delete=models.SET_NULL,default=None,blank=True)
    likes = models.ManyToManyField(Udata,blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.body[:50])
    
    def get_absolute_url(self):
        return reverse('home')
