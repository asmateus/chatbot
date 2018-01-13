from django.urls import path

from . import views


urlpatterns = [
    path('', views.chat, name='app-chat'),
    path('chat/', views.chat, name='app-chat'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.create_user_view, name='create-user'),
    path('u/<user>/', views.profile, name='u-profile'),
    path('u/<user>/profile/', views.profile, name='u-profile'),
    path('u/<user>/profile/edit', views.profile_edit, name='u-profile-edit'),
    path('u/<user>/history/', views.history, name='u-history'),
]
