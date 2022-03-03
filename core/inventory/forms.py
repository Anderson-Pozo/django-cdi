from django import forms
from django.forms import ModelForm

from core.inventory.models import *


class MaterialForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Material
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Nombre del material didáctico',
                    'class': 'form-control',
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'bodega_id': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                },
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': '5',
                    'class': 'form-control',
                    'placeholder': 'Descripción del material'
                },
            ),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class EntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = '__all__'
        widgets = {
            'date_entry': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'id': 'date_entry',
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'data-toggle': 'datetimepicker',
                    'data-target': '#date_entry'
                }
            ),
            'employee': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'disabled': True
                }
            )
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)


class OutputForm(ModelForm):
    class Meta:
        model = Output
        fields = '__all__'
        widgets = {
            'date_output': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control datetimepicker-input',
                    'id': 'date_output',
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'data-toggle': 'datetimepicker',
                    'data-target': '#date_output'
                }
            ),
            'teacher': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            )
        }


class StockForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].widget.attrs['autofocus'] = True

    class Meta:
        model = Inventory
        fields = '__all__'
        widgets = {
            'material': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                },
            ),
            'stock': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el stock'
                }
            )
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
