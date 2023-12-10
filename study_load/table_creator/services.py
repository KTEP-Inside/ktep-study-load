import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from .models import *


def ex_func(ws: Worksheet):
    num_course = int(ws.title[0])
    print(num_course)  # номер курса
    num_course = Course.objects.get(pk=num_course)
    speciality = ws['A1'].value.split()[3].strip()
    print(ws['A1'].value.split()[3])  # специальность
    speciality_obj, created = Speciality.objects.get_or_create(name=speciality)
    print(speciality_obj.id)
    print(''.join(ws['A1'].value.split()[3:5]))  # полностью группа и курс
    SpecialityHasCourse.objects.get_or_create(course=num_course, speciality=speciality_obj,
                                              name_group=''.join(ws['A1'].value.split()[3:5]))
    print()
    ls = ['Лекции', 'Лабораторные работы', 'Практические работы', 'Практика (УП/ПП)',
          'Консультации', 'Зачет, экзамен, контрольные работы', 'Курсовая работа']
    # получаем преподавателей + их предмет
    for subject, teacher in ws.iter_rows(min_col=2, max_col=3, min_row=5):
        if teacher.value is not None and subject.value is not None:
            # print(i[0].row)  # номер строки
            print(f'{subject.value.strip()}: {teacher.value}')
            print(len(teacher.value.strip()))
            Teacher.objects.get_or_create(name=teacher.value.strip())
            Subject.objects.get_or_create(name=subject.value.strip())
            # for j in ws.iter_cols(min_col=4, min_row=2, max_row=2):  # все типы нагрузки
            #     if j[0].value is not None and j[0].value in ls:  # не None и нужная колонка
            #         if j[0].value.find('Всего часов') == -1:  # до этой колонки, дальше не нужно
            #             # print(j[0].value)  # значение
            #             # print(j[0].column)  # номер колонки
            #
            #             # берем первый и второй семестр каждой дисциплины
            #             for k in ws.iter_cols(min_col=j[0].column, max_col=j[0].column + 1,
            #                                   min_row=i[0].row, max_row=i[0].row):
            #                 print(k, k[0].value)
            #         else:
            #             break


def add_data():
    wb = openpyxl.load_workbook(filename=r'C:\Users\user\PycharmProjects\ktep-study-load\study_load\table_creator\ИСиПы+ 2023-2024.xlsx')
    all_sheets = wb.sheetnames
    for sheet_id, _ in enumerate(all_sheets):
        ws = wb.worksheets[sheet_id]
        ex_func(ws)


add_data()