from django.urls import path

from . import views

urlpatterns = [
    path('', views.chat),
    path('chat/', views.chat),
    path('login/', views.login),
    path('logout/', views.logout),
    path('create-user/', views.create_user),
    path('u/<user>/', views.profile),
    path('u/<user>/profile/', views.profile),
    path('u/<user>/history/', views.history),
]
