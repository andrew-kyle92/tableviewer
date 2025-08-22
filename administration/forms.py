from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import SiteGroup


class SiteGroupForm(forms.ModelForm):
    class Meta:
        model = SiteGroup
        fields = ['name', 'department']
        exclude = ['owners', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddUserForm(ModelForm):
    search_user = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control auto-input", "autofocus": True, 'required': True, 'autocomplete': 'off',
        'data-user-selected': 'false'
    }))

    class Meta:
        model = User
        fields = ('search_user', 'username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={"class": "form-control readonly", "readonly": True}),
            'first_name': forms.TextInput(attrs={"class": "form-control readonly", "readonly": True}),
            'last_name': forms.TextInput(attrs={"class": "form-control readonly", "readonly": True}),
            'email': forms.TextInput(attrs={"class": "form-control readonly", "readonly": True}),
        }
