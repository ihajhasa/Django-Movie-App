from django import forms

from django.core.exceptions import ValidationError

from django.contrib.auth.models import User

'''
    LoginForm:
        username: username of account
        password: password of account
'''
class LoginForm(forms.Form):
    username = forms.CharField(label = 'username')
    password = forms.CharField(label = 'password', widget = forms.PasswordInput)

'''
    RegistrationForm:
        username: desired username for account
        password: desired password for account
        confirm_password: should match the desired password to make sure user entered the desired password correctly
        email: user's email
'''
class RegistrationForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='confirm_password', widget=forms.PasswordInput)
    email = forms.EmailField(label='email')

