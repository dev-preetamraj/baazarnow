from ast import Mod
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Profile
)

class RegisterUserForm(forms.Form):
    USERTYPE = (
        ('supplier', 'supplier'),
        ('consumer', 'consumer')
    )
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    first_name = forms.CharField(
        label="First Name"
    )
    last_name = forms.CharField(
        label="Last Name"
    )
    username = forms.CharField(
        label="Username"
    )
    email = forms.CharField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    
    gender = forms.ChoiceField(choices=GENDER)
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "pass1"
            }
        )
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "pass2"
            }
        )
    )
    user_type = forms.ChoiceField(choices=USERTYPE)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError("User with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError("User with this email already exists.")
        return email

    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password1',
    #               'password2', 'first_name', 'last_name','gender', 'user_type']

    #     widgets = {
    #         'username': forms.TextInput(attrs={'class': 'input-material'}),
    #         'email': forms.EmailInput(attrs={'class': 'input-material'}),
    #         'password1': forms.TextInput(attrs={'class': 'input-material', 'type': 'password'}),
    #         'password2': forms.TextInput(attrs={'class': 'input-material', 'type': 'password'}),
    #         'first_name': forms.TextInput(attrs={'class': 'input-material'}),
    #         'last_name': forms.TextInput(attrs={'class': 'input-material'})
    #     }

class UpdateProfilePicForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic']