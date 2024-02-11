from string import punctuation

from django.core.exceptions import ValidationError


def validate_val(value):
    if not isinstance(value, str):
        raise ValidationError('Значение - целое число или строка')
    for i in punctuation:
        if i in value:
            raise ValidationError('Значение не должно содержать символы пунктуации')
    if value.isdigit():
        if value[0] == '0' and len(value) > 1:
            raise ValidationError('Значение больше нуля не должно начинаться с нуля')
        if int(value) < 0:
            raise ValidationError('Значение должно быть больше или равно нулю')
    else:
        if isinstance(value, str) and value not in ('Э', 'ДЗ'):
            raise ValidationError('Текстовое значение - Э или ДЗ')


def validate_count_remaining_hours(hours_load, value, unallocated_hours):
    cur_val = value - hours_load.cur_hours
    if cur_val > unallocated_hours.unallocated_hours:
        raise ValidationError('Недостаточно часов в н/р')


def validate_remaining_hours(hours_load):
    cur_val = sum([i.unallocated_hours for i in hours_load])
    if cur_val <= 0:
        raise ValidationError('Недостаточно часов в н/р')

