from django.urls import path, include

from .views import *

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path("", include("django.contrib.auth.urls")),


]