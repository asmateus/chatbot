from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.chat),
    path('chat/', views.chat),
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html')),
    path('logout/', auth_views.LogoutView.as_view()),
    path('create-user/', views.chat),
    path('u/<user>/', views.profile),
    path('u/<user>/profile/', views.profile),
    path('u/<user>/history/', views.history),
]
