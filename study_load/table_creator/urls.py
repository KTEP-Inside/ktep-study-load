from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('get-groups/<int:teacher_id>/', GetGroupsView.as_view(), name='get_groups'),
    path('get-subjects/<int:teacher_id>/<int:group_id>/', GetSubjectsView.as_view(), name='get_subjects'),
    path('get-hours/<int:teacher_id>/<int:group_id>/<int:subject_id>/<int:type_load_id>/', GetStudyLoadHours.as_view(),
         name='get_hours'),
]