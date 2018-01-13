from django.http import HttpResponse


# Required user related methods

def login():
    return HttpResponse('You got to LOGIN page')


def logout():
    return HttpResponse('You got to LOGOUT page')


def create_user():
    return HttpResponse('You got to CREATE USER page')

# Basic API actions


def chat():
    return HttpResponse('You got to CHAT page')


def history():
    return HttpResponse('You got to HISTORY page')


def profile():
    return HttpResponse('You got to PROFILE page')
