from django import forms
from .models import Bebida, Venta, Gasto
from calendar import month_name
from datetime import datetime, time


class BebidaForm(forms.ModelForm):

    class Meta:
        model = Bebida
        fields = ["nombre", "descripcion", "precio", "stock"]
        widgets = {
            'nombre': forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe un nombre"}),
            'descripcion': forms.Textarea(attrs={"class": "form-control", "placeholder": "Escribe una descripcion"}),
            'precio': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Escribe el precio"}),
            'stock': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Escribe el stock"}),
        }


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descripcion', 'monto']
        widgets = {
            'descripcion': forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe una descripcion"}),
            'monto': forms.NumberInput(attrs={"class": "form-control", "placeholder": "Escribe el monto"}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['usuario', 'total']


class DateForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Seleccionar fecha"
    )


class MonthYearForm(forms.Form):
    MONTHS = [(i, month_name[i]) for i in range(1, 13)]
    YEARS = [(i, i) for i in range(2000, datetime.now().year + 1)]

    month = forms.ChoiceField(choices=MONTHS, label="Mes")
    year = forms.ChoiceField(choices=YEARS, label="Año")
