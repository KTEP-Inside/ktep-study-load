from django import forms


class ClearDataForm(forms.Form):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'input'}))