from django.shortcuts import render


def index(request):
    context = {
        'title': 'Creator',
    }
    return render(request, 'table_creator/table_creator.html', context=context)
