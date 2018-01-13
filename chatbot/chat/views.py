from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render

from django.contrib.auth.models import User


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
    return HttpResponse('You got to CHAT page')


def history(request, user=''):
    return HttpResponse('You got to HISTORY page of ' + user)


def profile(request, user=''):
    return HttpResponse('You got to PROFILE page of ' + user)


def profile_edit(request, user=''):
    return HttpResponse('You got to PROFILE EDIT page of ' + user)
