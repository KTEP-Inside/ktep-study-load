from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('get-groups/<int:teacher_id>/', GetGroupsView.as_view(), name='get_groups'),
    path('get-subjects/<int:teacher_id>/<int:group_id>/', GetSubjectsView.as_view(), name='get_subjects'),
    path('get-hours/<int:teacher_id>/<int:group_id>/<int:subject_id>/<int:type_load_id>/', GetStudyLoadHoursView.as_view(),
         name='get_hours'),
    path('upload-file/', ExcelFileUploadView.as_view(), name='upload-file'),
    path('update-hours/<int:teacher_id>/<int:group_id>/<int:subject_id>/<int:type_load_id>/<int:semester_id>/',
         UpdateHoursView.as_view(), name='update-hours'),
    path('upload-success/', success, name='upload-success'),
    path('upload-error/', error, name='upload-error'),
]