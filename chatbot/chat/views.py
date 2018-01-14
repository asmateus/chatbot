from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from django.db.models import Q

from .models import Message


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(
            reverse('u-profile', args=[request.user.username]))

    if request.method == 'GET':
        return render(request, 'chat/login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        login(request, user)

        return HttpResponseRedirect(reverse('u-profile', args=[username]))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def create_user_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(
            reverse('u-profile', args=[request.user.username]))

    if request.method == 'GET':
        return render(request, 'chat/create_user.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        if User.objects.filter(username=username).count():
            return HttpResponseRedirect(reverse('create-user'))

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password)
        user.save()

        login(request, user)

        return HttpResponseRedirect(reverse('u-profile', args=[username]))


# Basic API actions

def chat(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        template = loader.get_template('chat/chat.html')
        context = {
            'username': request.user.username,
            'response': 'Hola',
        }
        return HttpResponse(template.render(context, request))


def history(request, user=''):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if not user == request.user.username:
        return HttpResponseRedirect(reverse('u-profile', args=[user]))

    user_obj = User.objects.get(username=user)
    messages = Message.objects.filter(Q(origin=user_obj) | Q(target=user_obj))

    template = loader.get_template('chat/history.html')
    context = {
        'username': user,
        'messages': messages,
    }

    return HttpResponse(template.render(context, request))


def profile(request, user=''):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'GET':
        user_obj = User.objects.get(username=user)
        template = loader.get_template('chat/profile.html')
        context = {
            'username': user_obj.username,
            'fullname': user_obj.get_full_name(),
            'location': user_obj.profile.location,
            'description': user_obj.profile.description,
            'is_user': request.user.username == user
        }

        return HttpResponse(template.render(context, request))
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('u-profile-edit', args=[user]))


def profile_edit(request, user=''):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if not user == request.user.username:
        return HttpResponseRedirect(reverse('u-profile', args=[user]))
    return HttpResponse('You got to PROFILE EDIT page of ' + user)
