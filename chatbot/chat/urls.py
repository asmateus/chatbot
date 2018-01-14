from django.urls import path

from . import views


urlpatterns = [
    path('', views.chat, name='app-chat'),
    path('chat/', views.chat, name='app-chat'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('create-user/', views.create_user, name='create-user'),
    path('u/<username>/', views.profile, name='u-profile'),
    path('u/<username>/profile/', views.profile, name='u-profile'),
    path('u/<username>/profile/edit', views.profile_edit, name='u-profile-edit'),
    path('u/<username>/history/', views.history, name='u-history'),
]
