from django.contrib.auth.views import PasswordChangeDoneView, LogoutView
from django.urls import path, include

from .views import *

app_name = 'users'

urlpatterns = [

    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('register/', RegisterUserView.as_view(), name='register'),
    path('profile/', ProfileUserView.as_view(), name='profile'),

    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/',
         PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),




]
