from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .forms import RegistrationForm, LoginForm


def index(request):
    if not request.user.is_authenticated:
        # if user in not logged in then direct him to login page
        return HttpResponseRedirect(reverse('login'))

    # direct user to user home page
    context = {"user": request.user}
    return render(request, 'main/userpage.html', context)

def login_view(request):
    if request.method == 'POST':
        # user submitting login request
        login_form = LoginForm(request.POST)

        if (login_form.is_valid()):
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'registration/login.html', {'message': 'Invalid credentials', 'form': login_form})

    else:
        # user is requesting form
        login_form = LoginForm()
        context = {'form': login_form}
        return render(request, 'registration/login.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        # cannot log out user that isn't logged in
        logout(request)
    return HttpResponseRedirect(reverse('index'))

def register_user(request):
    if request.method == 'POST':
        # user is submitting registration form
        registration_form = RegistrationForm(request.POST)

        if (registration_form.is_valid()):
            username = registration_form.cleaned_data['username']
            password = registration_form.cleaned_data['password']
            confirm_password = registration_form.cleaned_data['confirm_password']
            email = registration_form.cleaned_data['email']

            valid = True

            if (User.objects.filter(username=username).first()):
                # username is already in use
                valid = False
                registration_form.add_error('username', 'username is already in use, please choose another one')

            if (password != confirm_password):
                # passwords do not match
                valid = False
                registration_form.add_error('confirm_password', 'passwords do not match')

            if not valid:
                # send back the same form to user with appropriate error messages
                return render(request, 'registration/registration-form.html', {'form': registration_form})

            # create new user and save it
            newUser = User.objects.create_user(username, email, password)
            newUser.save()

            return HttpResponseRedirect(reverse('index'), {'good_message': 'Account created successfully. Please login.'})
        else:
            return render(request, 'registration/registration-form.html', {'form': registration_form})
    else:
        # user is requesting registration form
        registration_form = RegistrationForm()
        context = {'form': registration_form}
        return render(request, 'registration/registration-form.html', context)