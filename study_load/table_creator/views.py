from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from .services import add_data
from .models import *
from .utils import *


def index(request):
    type_load = TypeLoad.objects.all()
    teachers = Teacher.objects.all()
    n = len(type_load)
    context = {
        'title': 'Creator',
        'type_load': type_load,
        "type_load_length": n,
        'type_results': type_results,
        'input_load_semester': n * 2 + 3,
        'teachers': teachers
    }
    # add_data()
    return render(request, template_name='table_creator/table_creator.html', context=context)


def get_groups(request, teacher_id):

    teacher_has_subj = TeacherHasSubject.objects.filter(
        teacher_id=teacher_id
    ).values('teacher_has_subject')

    group_ids = HoursLoad.objects.filter(
        teacher_subject_id__in=teacher_has_subj
    ).values('group_id')

    name_group = SpecialityHasCourse.objects.filter(
        speciality_id__in=group_ids
    ).order_by('name_group').values('name_group', 'course_has_speciality')

    data = list(name_group)
    return JsonResponse(data, safe=False)


def get_subjects(request, teacher_id, group_id):
    hours_load = HoursLoad.objects.filter(
        group_id=group_id
    ).values('teacher_subject_id').distinct()

    subjects_id = TeacherHasSubject.objects.filter(
        Q(teacher_has_subject__in=hours_load) & Q(teacher_id=teacher_id)
    ).values('subject_id')

    subjects = Subject.objects.filter(
        pk__in=subjects_id
    ).order_by('name').values('pk', 'name')

    data = list(subjects)
    return JsonResponse(data, safe=False)

