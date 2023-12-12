import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from .models import *


def ex_func(ws: Worksheet):
    """Основной скрипт получения данных с excel
    Будет разбит на несколько функций"""

    num_course = int(ws.title[0])
    print(num_course)  # номер курса
    num_course = Course.objects.get(pk=num_course)

    speciality = ws['A1'].value.split()[3].strip()
    print(ws['A1'].value.split()[3])  # специальность
    speciality_obj, created = Speciality.objects.get_or_create(name=speciality)  # специальность

    print(''.join(ws['A1'].value.split()[3:5]))  # полностью группа и курс
    SpecialityHasCourse.objects.get_or_create(course=num_course, speciality=speciality_obj,  # группы
                                              name_group=''.join(ws['A1'].value.split()[3:5]))
    print()

    # получаем преподавателей + их предмет
    for subject, teachers in ws.iter_rows(min_col=2, max_col=3, min_row=5):
        if teachers.value is not None and subject.value is not None:
            # print(i[0].row)  # номер строки
            print(f'{subject.value.strip()}: {teachers.value}')
            # print(teacher.value.split(','))
            Subject.objects.get_or_create(name=subject.value.strip())

            for teacher in teachers.value.split(','):
                Teacher.objects.get_or_create(name=teacher)

                for load in ws.iter_cols(min_col=4, min_row=2, max_row=2):  # все типы нагрузки
                    print(load[0].value)
                    if load[0].value is not None:
                        if load[0].value.find('Всего часов') == -1:
                            type_load = TypeLoad.objects.filter(name=load[0].value.strip()).exists()
                            if type_load:
                                # print(j[0].value)  # значение
                                # print(j[0].column)  # номер колонки

                                # берем первый и второй семестр каждой дисциплины
                                semester = 1
                                for k in ws.iter_cols(min_col=load[0].column, max_col=load[0].column + 1,
                                                      min_row=subject.row, max_row=subject.row):
                                    print(k, k[0].value)
                                    if isinstance(k[0].value, int):
                                        pass
                                    elif k[0].value in ['ДЗ', 'Э']:
                                        pass
                                    else:
                                        pass

                                    semester += 1
                        else:
                            break


def add_data():
    wb = openpyxl.load_workbook(filename=r'C:\Users\user\PycharmProjects\ktep-study-load\study_load\table_creator\ИСиПы+ 2023-2024.xlsx')
    all_sheets = wb.sheetnames
    for sheet_id, _ in enumerate(all_sheets):
        ws = wb.worksheets[sheet_id]
        ex_func(ws)


add_data()