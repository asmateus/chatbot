from django.http import HttpResponse

# Basic API actions


def chat(request):
    return HttpResponse('You got to CHAT page')


def history(request, user=''):
    return HttpResponse('You got to HISTORY page of ' + user)


def profile(request, user=''):
    return HttpResponse('You got to PROFILE page of ' + user)
