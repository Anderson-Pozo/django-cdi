from django import forms
from core.inventory.models import Inventory
from core.inventory.models import Bodega

from core.school.models import *
from core.reports.models import *


class ReportForm(forms.Form):
    period = forms.ModelChoiceField(widget=forms.Select(
        attrs={
            'class': 'form-control select2',
            'style': 'width: 100%;'
        }), queryset=Period.objects.filter())

    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))

    breakfast = forms.ModelChoiceField(queryset=Breakfast.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    student = forms.ModelChoiceField(queryset=Student.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    conferencetheme = forms.ModelChoiceField(queryset=ConferenceTheme.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    shifts = forms.ModelChoiceField(queryset=Shifts.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    course = forms.ModelChoiceField(queryset=Cursos.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    matter = forms.ModelChoiceField(queryset=Matter.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    inventory = forms.ModelChoiceField(queryset=Inventory.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

    bodega = forms.ModelChoiceField(queryset=Bodega.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control select2',
        'style': 'width: 100%;'
    }))

