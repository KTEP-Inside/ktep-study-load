from .validators import sum_hours
from .models import TeacherHours

exams_type = ('Э', 'ДЗ')  # лучше убрать
type_results = ['Всего', 'Праздничные дни', 'Итого']

menu = [{'title': 'Таблица', 'url_name': 'home'},
        {'title': 'Профиль', 'url_name': 'users:profile'}, ]


def check_sum_hours(hours_load, unallocated_teacher):
    unallocated_sum = sum_hours(TeacherHours.objects.filter(teacher_id=unallocated_teacher,
                                                            hours_load_id__in=hours_load))
    if unallocated_sum <= 0:
        TeacherHours.objects.filter(teacher_id=unallocated_teacher, hours_load_id__in=hours_load).delete()
