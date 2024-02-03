import json
import logging
import mimetypes
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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

    def get(self, request, teacher_id):
        teacher_has_subj = TeacherHasSubject.objects.filter(
            teacher_id=teacher_id
        ).values('teacher_has_subject').distinct()

        group_ids = HoursLoad.objects.filter(
            teacher_subject_id__in=teacher_has_subj
        ).values('group_id').distinct()

        name_group = SpecialityHasCourse.objects.filter(
            course_has_speciality__in=group_ids
        ).order_by("name_group").values('name_group', 'course_has_speciality', 'is_paid')

        data = tuple(name_group)
        return JsonResponse(data, safe=False)


class GetSubjectsView(LoginRequiredMixin, View):
    """Получение списка предметов"""
    def get(self, request, teacher_id, group_id):
        hours_load = HoursLoad.objects.filter(
            group_id=group_id
        ).values('teacher_subject_id').distinct()

        subjects_id = TeacherHasSubject.objects.filter(
            Q(teacher_has_subject__in=hours_load) & Q(teacher_id=teacher_id)
        ).values('subject_id')

        subjects = Subject.objects.filter(
            pk__in=subjects_id
        ).order_by("name").values('pk', 'name', 'is_paid')

        data = tuple(subjects)
        return JsonResponse(data, safe=False)


class GetStudyLoadHoursView(LoginRequiredMixin, View):
    """Получение часов учебной нагрузки"""

    def get(self, request, teacher_id, group_id, subject_id, type_load_id):

        teacher_has_subj = TeacherHasSubject.objects.filter(
            Q(subject_id=subject_id) & Q(teacher_id=teacher_id)
        ).values('teacher_has_subject')

        hours = HoursLoad.objects.filter(
            Q(teacher_subject__in=teacher_has_subj) & Q(group_id=group_id) & Q(type_load_id=type_load_id)
        ).order_by("semester").values('hours', 'exam')

        for i in range(len(hours)):
            if hours[i]['exam'] is not None:
                val = Exam.objects.get(pk=hours[i]['exam'])
                hours[i]['exam'] = val.exam

        data = tuple(hours)
        return JsonResponse(data, safe=False)


class ExcelFileUploadView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Загрузка данных из файла в бд"""
    permission_required = 'table_creator.add_hoursload'

    def post(self, request):

        if 'file_name' in request.FILES:
            uploaded_file = request.FILES['file_name']
            # try:
            load_data(uploaded_file)
            return redirect('upload-success')
            #
            # except Exception as e:
            #     return redirect('upload-error')

        # return redirect('upload-error')


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


class UpdateHoursView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Обновление ячейки в базе"""
    permission_required = 'table_creator.change_hoursload'

    @staticmethod
    def _set_exam_or_hours(obj, exam=None, hours=None):
        obj.exam = exam
        obj.hours = hours
        obj.save()

    @staticmethod
    def _get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id):
        teacher_has_subj = TeacherHasSubject.objects.filter(
            Q(subject_id=subject_id) & Q(teacher_id=teacher_id)
        ).values('teacher_has_subject')

        prev_val = 0
        try:
            obj = HoursLoad.objects.get(
                teacher_subject_id__in=teacher_has_subj, semester_id=semester_id, group_id=group_id,
                type_load_id=type_load_id)

            if obj.hours is None:
                prev_val = obj.exam
            elif obj.exam is None:
                prev_val = obj.hours

        except ObjectDoesNotExist:
            prev_val = 0
        except MultipleObjectsReturned:
            prev_val = 0

        return prev_val

    def _update_hours_load(self, teacher_has_subj, semester_id, group_id, type_load_id, val):
        hours_load, created = HoursLoad.objects.get_or_create(
            teacher_subject_id=teacher_has_subj,
            semester_id=semester_id,
            group_id=group_id,
            type_load_id=type_load_id
        )

        if val in exams_type:
            exam = Exam.objects.get(exam=val)
            self._set_exam_or_hours(hours_load if hours_load else created, exam=exam)
        elif val.isdigit():
            val = int(val)
            self._set_exam_or_hours(hours_load if hours_load else created, hours=val)

    def put(self, request, teacher_id, group_id, subject_id, type_load_id, semester_id):
        try:
            val = json.loads(request.body)['val']
            validate_val(val)

            teacher_has_subj = TeacherHasSubject.objects.get(
                subject_id=subject_id, teacher_id=teacher_id)
            teacher_has_subj = teacher_has_subj.teacher_has_subject

            self._update_hours_load(teacher_has_subj, semester_id, group_id, type_load_id, val)

            logger.info('Изменение значения в базе')
            return JsonResponse({'status': 'success', 'message': 'Успешно'})

        except ValidationError as validation_error:
            prev_val = self._get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id)
            return JsonResponse(
                {'status': 'validation-error', 'message': str(validation_error.message), 'data': prev_val})

        except Exception as e:
            prev_val = self._get_prev_value(teacher_id, group_id, subject_id, type_load_id, semester_id)
            return JsonResponse({'status': 'error', 'message': str(e), 'data': prev_val})


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
        models_list = [Teacher, TeacherHasSubject, Subject, SpecialityHasCourse, HoursLoad]
        for model in models_list:
            model.objects.all().delete()


class ClearDataDoneView(PermissionRequiredMixin, LoginRequiredMixin, View):
    """Очистка базы"""
    template_name = 'table_creator/clear_data_done.html'
    permission_required = 'table_creator.delete_hoursload'

    def get(self, request):
        logger.info('Очистка базы')
        return render(request, self.template_name)


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
