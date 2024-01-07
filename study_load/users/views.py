from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm


# Create your views here.
def login(request):
    form = LoginForm()
    return render(request, template_name='registration/login.html', context={'form': form})