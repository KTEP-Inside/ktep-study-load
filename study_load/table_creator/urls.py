from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('get-groups/<int:teacher_id>/', views.get_groups, name='get_groups'),
    path('get-subjects/<int:teacher_id>/<int:group_id>/', views.get_subjects, name='get_subjects'),
]