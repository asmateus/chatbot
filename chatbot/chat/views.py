from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

from .models import Message
from .helpers import (is_authenticated, is_valid, is_user_of_content,
                      is_not_authenticated, is_created)


@is_authenticated('app-chat')
def login(request):
    if request.method == 'GET':
        return render(request, 'chat/login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request,
                                 username=username,
                                 password=password)

        # Wrong password, or username does not exist
        if user is None:
            return redirect(reverse('login'))

        # Successful authentication, remember it
        auth.login(request, user)

        return redirect(reverse('app-chat'))


def logout(request):
    # In any case, attempt logout and
    # redirect to login page.
    auth.logout(request)
    return redirect(reverse('login'))


@is_authenticated('app-chat')
def create_user(request):
    if request.method == 'GET':
        return render(request, 'chat/create_user.html')

    if request.method == 'POST':
        # username is the only crucial parameter
        # for validation
        username = request.POST.get('username')
        if (not is_valid(username)) or is_created(username):
            return redirect(reverse('create-user'))

        # It is safe to create the user
        # Get post values and pass them to user
        user = User.objects.create_user(
            username=request.POST.get('username'),
            email=request.POST.get('email'),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            password=request.POST.get('password'),
        )
        user.save()
        auth.login(request, user)

        return redirect(reverse('u-profile', args=[username]))


# Basic API actions

@is_not_authenticated('login')
def chat(request):
    if request.method == 'GET':
        # Pass the username to display it in the title
        # of the chat.
        context = {'username': request.user.username}
        return render(request, 'chat/chat.html', context)


@is_not_authenticated('login')
def history(request, username=''):
    """Static history page, same response always
    """

    # Is the logged user the owner of the information
    if not is_user_of_content(request, username):
        return redirect(reverse('u-profile', args=[username]))

    # The user may supply an output limit as a parameter
    # it is not trusted so it is sanitized
    raw_limit = request.GET.get('limit_to')
    limit = Message.objects.sanitize_raw_limit(raw_limit)

    messages = Message.objects.of(username, limit=limit)

    context = {'username': username, 'messages': messages, 'limit': limit}
    return render(request, 'chat/history.html', context)


@is_not_authenticated('login')
def profile(request, username=''):
    if request.method == 'GET':
        # Load html with user info
        user = User.objects.get(username=username)
        context = {
            'username': user.username,
            'fullname': user.get_full_name(),
            'location': user.profile.location,
            'description': user.profile.description,
            'is_user': is_user_of_content(request, username)  # To hide edit
        }
        return render(request, 'chat/profile.html', context)

    if request.method == 'POST':
        # An attempt to edit the profile was triggered
        return redirect(reverse('u-profile-edit', args=[username]))


@is_not_authenticated('login')
def profile_edit(request, username=''):
    # Is the logged user the owner of the information
    if not is_user_of_content(request, username):
        return redirect(reverse('u-profile', args=[username]))

    if request.method == 'GET':
        # Show the form for editing
        user = User.objects.get(username=username)
        context = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'location': user.profile.location,
            'description': user.profile.description,
        }
        return render(request, 'chat/profile_edit.html', context)

    if request.method == 'POST':
        # Update the user with the edits
        user = User.objects.get(username=username)
        user.profile.update(request.POST)
        user.save()

        return redirect(reverse('u-profile', args=[username]))
