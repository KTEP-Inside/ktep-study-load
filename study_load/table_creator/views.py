from django.shortcuts import render
from .services import add_data

def index(request):
    context = {
        'title': 'Creator',
    }
    add_data()
    return render(request, template_name='table_creator/table_creator.html', context=context)
