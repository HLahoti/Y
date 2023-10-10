from django.forms import ModelForm
from django import forms
from .models import Udata,Topic,Posts
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm2(UserCreationForm):

    class META:
        model=User
        fields = [
            "first_name",
            "username",
            "email_address",
            "password1",
            "password2",
        ]
        exclude = []


class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    username = forms.CharField(max_length=40)
    password1 = forms.CharField(widget = forms.PasswordInput()) 
    password2 = forms.CharField(widget = forms.PasswordInput()) 

    def clean_password1(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            return password1

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            return password2
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        return username
    def clean_name(self):
        name = self.cleaned_data["name"]
        return name
    def clean_email(self):
        email = self.cleaned_data["email"]
        return email
