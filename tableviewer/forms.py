from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from django import forms

from tableviewer.models import DynamicTable, TableColumn


class TableModelForm(ModelForm):
    class Meta:
        model = DynamicTable
        fields = ['name', 'description', 'table_file', 'results_shown', 'logo', 'before_table_text',
                  'after_table_text']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'table_file': forms.FileInput(attrs={'class': 'form-control'}),
            'results_shown': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class TableForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=200, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    table_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))


class TableColumnForm(ModelForm):
    class Meta:
        model = TableColumn
        fields = ['name', 'label', 'order', 'use_column']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'use_column': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Authentication forms
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
