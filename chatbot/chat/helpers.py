from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
import re


# Auth decorators

def is_authenticated(url, *args):
    """is_authenticated decorator but using names
    """
    def decorator(func):
        def _redirect(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return func(request, *args, **kwargs)
            return redirect(reverse(url, args=[*args]))
        return _redirect
    return decorator


def is_not_authenticated(url, *args):
    """reverse of is_authenticated
    """
    def decorator(func):
        def _redirect(request, *args, **kwargs):
            if request.user.is_authenticated:
                return func(request, *args, **kwargs)
            return redirect(reverse(url, args=[*args]))
        return _redirect
    return decorator


# Auth functions

def is_created(username):
    return User.objects.filter(username=username).exists()


def is_valid(username):
    exp = '[^A-Za-z0-9]'
    match = re.search(exp, username)

    return match is None


def is_user_of_content(request, username):
    return request.user.username == username


def date_of(timestamp):
    if timestamp is not None:
        return timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
