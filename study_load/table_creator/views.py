import json
import logging
import mimetypes
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q, F
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import ClearDataForm
from .services.load_data import load_data
from .services.create_report import create_excel_report_data
from .models import *
from .utils import *
from .validators import *

logger = logging.getLogger(__name__)  # подключение логирования


class MainView(LoginRequiredMixin, View):
    """главная страница"""
    template_name = 'table_creator/table_creator.html'

    @staticmethod
    def get_context_data():
        type_load = TypeLoad.objects.all()
        teachers = Teacher.objects.all().order_by("name")
        n = len(type_load)
        context = {
            'type_load': type_load,
            "type_load_length": n,
            'type_results': type_results,
            'input_load_semester': n * 2 + 3,
            'teachers': teachers,
        }
        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, template_name=self.template_name, context=context)


class GetGroupsView(LoginRequiredMixin, View):
    """Получение списка групп"""

    # tut
    def get(self, request):
        groups = SpecialityHasCourse.objects.all() \
            .order_by("name_group").values('name_group', 'course_has_speciality', 'is_paid')

        data = tuple(groups)
        return JsonResponse(data, safe=False)


class GetSubjectsView(LoginRequiredMixin, View):
    """Получение списка предметов"""

    def get(self, request, group_id):
        subjects_id = GroupHasSubject.objects.filter(group_id=group_id).all().values('subject_id')

        subjects = Subject.objects.filter(
            pk__in=subjects_id
        ).all().order_by("name").values('pk', 'name', 'is_paid')

        data = tuple(subjects)
        return JsonResponse(data, safe=False)


class GetStudyLoadHoursView(LoginRequiredMixin, View):
    """Получение часов учебной нагрузки"""
    # тут
    def get(self, request, teacher_id, group_id, subject_id, type_load_id):

        group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)

        hours_cells = HoursLoad.objects.filter(
            Q(group_has_subject_id=group_has_subject.pk) & Q(type_load_id=type_load_id)
        ).order_by("semester")

        hours = TeacherHours.objects.filter(
            Q(teacher_id=teacher_id) & Q(hours_load_id__in=hours_cells))

        hours = hours.values('cur_hours', 'cur_exam')

        flag = False
        if not list(hours):
            flag = True
            hours = hours_cells.values(
                cur_hours=F('hours'),
                cur_exam=F('exam'))

        for i in range(len(hours)):
            if hours[i]['cur_exam'] is not None:
                val = Exam.objects.get(pk=hours[i]['cur_exam'])
                hours[i]['cur_exam'] = val.exam

            elif flag:
                hours[i]['cur_hours'] = hours_cells[i].unallocated_hours

        data = tuple(hours)
        return JsonResponse(data, safe=False)


class ExcelFileUploadView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Загрузка данных из файла в бд"""
    permission_required = 'table_creator.add_hoursload'

    def post(self, request):
        if 'file_name' in request.FILES:
            uploaded_file = request.FILES['file_name']
            try:
                load_data(uploaded_file)
                return redirect('upload-success')

            except Exception as e:
                 return redirect('upload-error')

        return redirect('upload-error')


class CreateExcelReportView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """сохраняем получившийся отчет в базе"""
    permission_required = 'table_creator.change_hoursload'

    def post(self, request):
        data = json.loads(request.body)['val']

        output = BytesIO()
        wb, filename = create_excel_report_data(data)
        wb.save(output)
        output.seek(0)

        mime_type = mimetypes.guess_type(f'{filename}.xlsx')[0]
        response = FileResponse(output, content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'

        return response


class CreateRowForTeacherHoursView(LoginRequiredMixin, View):

    def post(self, request, teacher_id, group_id, subject_id):
        try:
            group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)
            hours_load = HoursLoad.objects.filter(group_has_subject=group_has_subject)
            for hours in hours_load:

                TeacherHours.objects.create(teacher_id=teacher_id,
                                            hours_load_id=hours.pk,
                                            cur_hours=hours.unallocated_hours,
                                            cur_exam=hours.exam)

                obj = HoursLoad.objects.get(pk=hours.pk)
                obj.unallocated_hours = 0
                obj.save()
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error'})


class DeleteRowForTeacherHoursView(LoginRequiredMixin, View):
    # нр
    def delete(self, request, teacher_id, group_id, subject_id):
        group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)

        hours_load = HoursLoad.objects.filter(group_has_subject=group_has_subject.pk) \
            .values_list('pk', flat=True)

        try:
            delete_row = TeacherHours.objects.filter(teacher_id=teacher_id, hours_load_id__in=hours_load)

            for del_cel, un_cel in zip(delete_row, hours_load):

                cur_del_cell = TeacherHours.objects.get(pk=del_cel.pk)
                obj = HoursLoad.objects.get(pk=un_cel)
                obj.unallocated_hours += cur_del_cell.cur_hours
                obj.save()

            delete_row.delete()
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error'})


class GetAllDataForTeacher(LoginRequiredMixin, View):
    def get(self, request, teacher_id):

        try:
            teacher = Teacher.objects.get(pk=teacher_id)
            hours = TeacherHours.objects.filter(teacher=teacher).all().order_by('hours_load') \
                .values_list('hours_load', flat=True)
            groups_has_subjects = HoursLoad.objects.filter(pk__in=hours).values('group_has_subject').distinct()

            rows = GroupHasSubject.objects.filter(pk__in=groups_has_subjects).values('group', 'subject_id')

            for row in range(len(rows)):
                selected_group = SpecialityHasCourse.objects.get(
                    course_has_speciality=rows[row]['group'])
                rows[row]['name_group'] = selected_group.name_group
                rows[row]['group_is_paid'] = selected_group.is_paid

                subject = Subject.objects.get(pk=rows[row]['subject_id'])
                rows[row]['subject_is_paid'] = subject.is_paid
                rows[row]['subject_name'] = subject.name

            return JsonResponse({'status': 'success', 'data': list(rows)})
        except Exception as e:
            return JsonResponse({'status': 'error'})


class UpdateHoursView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Обновление ячейки в базе"""

    permission_required = 'table_creator.change_hoursload'

    @staticmethod
    def _set_exam_or_hours(obj, unallocated_hours, exam=None, hours=0):
        if exam:
            unallocated_hours.unallocated_hours += obj.cur_hours
        else:
            unallocated_hours.unallocated_hours += (obj.cur_hours - hours)

        unallocated_hours.save()
        obj.cur_exam = exam
        obj.cur_hours = hours
        obj.save()

        return unallocated_hours.unallocated_hours

    @staticmethod
    def _get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id):

        prev_val = 0
        try:
            group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)
            cur_cell = HoursLoad.objects.get(
                semester_id=semester_id, group_has_subject=group_has_subject,
                type_load_id=type_load_id)
            obj = TeacherHours.objects.get(teacher_id=teacher_id, hours_load_id=cur_cell.pk)

            if obj.cur_hours is None:
                prev_val = obj.cur_exam
            elif obj.cur_exam is None:
                prev_val = obj.cur_hours

        except ObjectDoesNotExist:
            prev_val = 0
        except MultipleObjectsReturned:
            prev_val = 0

        return prev_val

    def _update_hours_load(self, teacher_id, subject_id, semester_id,
                           group_id, type_load_id, val):

        group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)

        hours_load_cell = HoursLoad.objects.get(
            semester_id=semester_id,
            group_has_subject=group_has_subject,
            type_load_id=type_load_id
        )

        hours_load = TeacherHours.objects.get(teacher_id=teacher_id, hours_load_id=hours_load_cell.pk)

        updated_on_hours = None
        if val in exams_type:
            exam = Exam.objects.get(exam=val)
            updated_on_hours = self._set_exam_or_hours(hours_load, hours_load_cell, exam=exam)
        elif val.isdigit():
            val = int(val)
            validate_count_remaining_hours(hours_load, val, hours_load_cell)
            updated_on_hours = self._set_exam_or_hours(hours_load, hours_load_cell, hours=val)

        return updated_on_hours

    def check_sum_in_str(self, teacher_id, group_id, subject_id):
        group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)
        hours_load = HoursLoad.objects.filter(group_has_subject=group_has_subject)
        teacher_hours = TeacherHours.objects.filter(teacher_id=teacher_id, hours_load_id__in=hours_load)\
            .values('cur_hours', 'cur_exam')
        _sum = sum([teacher_hours[i]['cur_hours'] for i in range(len(teacher_hours))])
        # _exams = any([teacher_hours[i]['cur_exam'] for i in range(len(teacher_hours))])
        if _sum == 0:
            return True
        else:
            return False

    def put(self, request, teacher_id, group_id, subject_id, type_load_id, semester_id):
        try:
            val = json.loads(request.body)['val']
            validate_val(val)

            unallocated_hours = self._update_hours_load(teacher_id, subject_id, semester_id,
                                                        group_id, type_load_id, val)

            is_null = self.check_sum_in_str(teacher_id, group_id, subject_id)
            logger.info('Изменение значения в базе')

            return JsonResponse({'status': 'success', 'message': 'Успешно', 'unallocated_hours': unallocated_hours,
                                 'is_null': is_null})

        except ValidationError as validation_error:
            prev_val = self._get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id)
            return JsonResponse(
                {'status': 'validation-error', 'message': str(validation_error.message), 'data': prev_val})

        except Exception as e:
            prev_val = self._get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id)
            return JsonResponse({'status': 'error', 'message': str(e), 'data': prev_val})


class ValidateHoursLoad(LoginRequiredMixin, View):

    def get(self, request, group_id, subject_id):

        try:
            group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)
            hours_load = HoursLoad.objects.filter(group_has_subject=group_has_subject)

            validate_remaining_hours(hours_load)
            return JsonResponse({'status': 'success'})

        except ValidationError as val_e:
            return JsonResponse({'status': 'validation-error', 'message': str(val_e.message)})
        except Exception as e:
            return JsonResponse({'status': 'error'})


class ClearDataView(PermissionRequiredMixin, LoginRequiredMixin, FormMixin, View):
    """Очищаем данные за прошлый год, можно изменить post на delete
    для соблюдения REST, но тут не вижу в этом смысла"""
    form_class = ClearDataForm
    template_name = 'table_creator/clear_data.html'
    permission_required = 'table_creator.delete_hoursload'

    def get(self, request):
        form = self.form_class()
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            password = form.cleaned_data['password']
            user = request.user

            if user.check_password(password):
                self.delete_data()
                return self.form_valid(form)
            else:
                form.add_error('password', 'Неверный пароль')
                return self.form_invalid(form)

        return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return reverse_lazy('clear_data_done')

    @staticmethod
    def delete_data() -> None:
        models_list = [Teacher, Subject, SpecialityHasCourse, HoursLoad, TeacherHours, GroupHasSubject]
        for model in models_list:
            model.objects.all().delete()


class ClearDataDoneView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Очистка базы"""
    template_name = 'table_creator/clear_data_done.html'
    permission_required = 'table_creator.delete_hoursload'

    def get(self, request):
        logger.info('Очистка базы')
        return render(request, self.template_name)


class UnallocatedHours(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    template_name = 'table_creator/unallocated_hours.html'
    permission_required = 'table_creator.delete_hourload'
    model = HoursLoad

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = SpecialityHasCourse.objects.all()
        return context

    def get_queryset(self):
        queryset = HoursLoad.objects.exclude(unallocated_hours=0)
        return queryset


class UpdateUnallocatedData(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'table_creator.delete_hourload'

    def get(self, request, group_id=None, subject_id=None):
        queryset = HoursLoad.objects.exclude(unallocated_hours=0)

        if group_id and subject_id:
            group_has_subject = GroupHasSubject.objects.get(group_id=group_id, subject_id=subject_id)
            queryset = queryset.filter(group_has_subject=group_has_subject)
        elif group_id:
            group_has_subject = GroupHasSubject.objects.filter(group_id=group_id)
            queryset = queryset.filter(group_has_subject_id__in=group_has_subject)
        res = []
        for obj in queryset:
            st = f"{obj.semester} семестр {obj.group_has_subject} {obj.type_load}" \
                 f" нр: {obj.unallocated_hours} (Часов по умолчанию: {obj.hours})"
            res.append(st)
        return JsonResponse({'status': 'success', 'data': res})


@login_required
def success(request):
    return render(request, template_name='table_creator/success.html')


@login_required
def error(request):
    logger.info('неправильный шаблон файла')
    return render(request, template_name='table_creator/error.html')


def page_not_found_view(request):
    return render(request, template_name='404.html', status=404)


def page_access_is_denied(request):
    logger.warning('Не достаточно прав у пользователя')
    return render(request, template_name='403.html', status=403)
