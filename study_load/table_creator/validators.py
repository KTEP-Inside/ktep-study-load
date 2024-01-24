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
    else:
        if isinstance(value, str) and value not in ('Э', 'ДЗ'):
            raise ValidationError('Текстовое значение - Э или ДЗ')