from django.shortcuts import render
from .services import add_data
from .models import *
from .utils import *


def index(request):
    type_load = TypeLoad.objects.all()
    n = len(type_load)
    context = {
        'title': 'Creator',
        'type_load': type_load,
        "type_load_length": n,
        'type_results': type_results
    }
    add_data()
    return render(request, template_name='table_creator/table_creator.html', context=context)
