from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Venta, Gasto
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractDay
from calendar import monthrange
import locale


@login_required
def ver_ventas_mensuales(request):
    usuario = request.user

    # Establecer la localización en español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Obtener el mes y año desde la solicitud GET, o usar los valores actuales por defecto
    mes_actual = int(request.GET.get('mes', timezone.now().month))
    año_actual = int(request.GET.get('ano', timezone.now().year))

    # Obtener las ventas agrupadas por día para el mes seleccionado
    ventas_por_dia = (
        Venta.objects.filter(
            usuario=usuario, fecha__year=año_actual, fecha__month=mes_actual)
        .annotate(dia=ExtractDay('fecha'))
        .values('dia')
        .annotate(total_ventas=Sum('total'))
        .order_by('dia')
    )

    # Obtener la cantidad de días en el mes seleccionado
    _, total_dias_mes = monthrange(año_actual, mes_actual)

    # Crear una lista con los días del mes y los totales de ventas
    ventas_data = []
    for dia in range(1, total_dias_mes + 1):  # 1 hasta el último día del mes
        total = next((venta['total_ventas']
                     for venta in ventas_por_dia if venta['dia'] == dia), 0)
        # Convertir a float para el formato de Highcharts
        ventas_data.append([str(dia), float(total)])

    # Ajustar el título según el mes y año seleccionados en español
    titulo = f'Ventas del Mes de {timezone.datetime(
        año_actual, mes_actual, 1).strftime("%B")} {año_actual}'

    # Obtener los nombres de los meses y los años disponibles
    months = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
              7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    available_years = range(2020, timezone.now().year + 1)

    return render(request, 'inventario/graficos/ventas_mensual.html', {
        'titulo': titulo,
        'grafico_url': 'ventas_mensuales',
        'ventas_data': ventas_data,
        'months': months,
        'available_years': available_years,
        'selected_month': mes_actual,
        'selected_year': año_actual,
    })


@login_required
def ver_gastos_mensuales(request):
    usuario = request.user

    # Establecer la localización en español
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    # Obtener el mes y año desde la solicitud GET, o usar los valores actuales por defecto
    mes_actual = int(request.GET.get('mes', timezone.now().month))
    año_actual = int(request.GET.get('ano', timezone.now().year))

    # Obtener los gastos agrupados por día para el mes seleccionado
    gastos_por_dia = (
        Gasto.objects.filter(
            usuario=usuario, fecha_gasto__year=año_actual, fecha_gasto__month=mes_actual)
        .annotate(dia=ExtractDay('fecha_gasto'))
        .values('dia')
        .annotate(total_gastos=Sum('monto'))
        .order_by('dia')
    )

    # Obtener la cantidad de días en el mes seleccionado
    _, num_dias = monthrange(año_actual, mes_actual)

    # Crear la lista de datos para el gráfico
    gastos_data = []
    for dia in range(1, num_dias + 1):  # Rango de 1 hasta el número de días en el mes
        total = next((gasto['total_gastos']
                     for gasto in gastos_por_dia if gasto['dia'] == dia), 0)
        gastos_data.append([str(dia), float(total)])

    # Ajustar el título según el mes y año seleccionados en español
    nombre_mes_espanol = timezone.datetime(
        año_actual, mes_actual, 1).strftime("%B").capitalize()
    titulo = f'Gastos del Mes de {nombre_mes_espanol} {año_actual}'

    # Obtener los nombres de los meses y los años disponibles
    months = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
              7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    available_years = range(2020, timezone.now().year + 1)

    return render(request, 'inventario/graficos/gastos_mensuales.html', {
        'titulo': titulo,
        'grafico_url': 'gastos_mensuales',
        'gastos_data': gastos_data,
        'months': months,
        'available_years': available_years,
        'selected_month': mes_actual,
        'selected_year': año_actual,
    })


@login_required
def ver_ventas_diarias(request):
    return render(request, 'inventario/grafico.html', {'titulo': 'Ventas Diarias', 'grafico_url': 'ventas_diarias'})


@login_required
def ver_gastos_diarios(request):
    return render(request, 'inventario/grafico.html', {'titulo': 'Gastos Diarios', 'grafico_url': 'gastos_diarios'})


@login_required
def ver_ventas_semanales(request):
    return render(request, 'inventario/grafico.html', {'titulo': 'Ventas Semanales', 'grafico_url': 'ventas_semanales'})


@login_required
def ver_gastos_semanales(request):
    return render(request, 'inventario/grafico.html', {'titulo': 'Gastos Semanales', 'grafico_url': 'gastos_semanales'})

# Ventas y Gastos anuales:


@login_required
def ver_ventas_anuales(request):
    usuario = request.user

    # Obtener el año seleccionado del formulario, o el año actual si no se selecciona ninguno
    año_seleccionado = request.GET.get('ano', timezone.now().year)

    # Obtener las ventas agrupadas por mes para el año seleccionado
    ventas_por_mes = (
        Venta.objects.filter(usuario=usuario, fecha__year=año_seleccionado)
        .annotate(mes=ExtractMonth('fecha'))
        .values('mes')
        .annotate(total_ventas=Sum('total'))
        .order_by('mes')
    )

    # Crear una lista con los nombres de los meses y los totales de ventas
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    ventas_data = []

    for i in range(1, 13):  # 1 a 12 para los meses de enero a diciembre
        total = next((venta['total_ventas']
                     for venta in ventas_por_mes if venta['mes'] == i), 0)
        # Convierte a float para el formato de Highcharts
        ventas_data.append([meses[i - 1], float(total)])

    # Obtener los años disponibles en las ventas para el select del formulario
    available_years = Venta.objects.filter(usuario=usuario).dates(
        'fecha', 'year', order='DESC').distinct()

    # Extraer solo el año de cada objeto datetime
    available_years = [fecha.year for fecha in available_years]

    return render(request, 'inventario/graficos/ventas_anuales.html', {
        'titulo': f'Ventas del Año {año_seleccionado}',
        'grafico_url': 'ventas_anuales',
        'ventas_data': ventas_data,
        'available_years': available_years,
        'selected_year': int(año_seleccionado)
    })


@login_required
def ver_gastos_anuales(request):
    usuario = request.user

    # Obtener el año seleccionado del formulario, o el año actual si no se selecciona ninguno
    año_seleccionado = request.GET.get('ano', timezone.now().year)

    # Obtener los gastos agrupados por mes para el año seleccionado
    gastos_por_mes = (
        Gasto.objects.filter(
            usuario=usuario, fecha_gasto__year=año_seleccionado)
        .annotate(mes=ExtractMonth('fecha_gasto'))
        .values('mes')
        .annotate(total_gasto=Sum('monto'))
        .order_by('mes')
    )

    # Crear una lista con los nombres de los meses y los totales de gastos
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    gastos_data = []

    for i in range(1, 13):  # 1 a 12 para los meses de enero a diciembre
        total = next((gasto['total_gasto']
                     for gasto in gastos_por_mes if gasto['mes'] == i), 0)
        # Convierte a float para el formato de Highcharts
        gastos_data.append([meses[i - 1], float(total)])

    # Obtener los años disponibles en los gastos para el select del formulario
    available_years = Gasto.objects.filter(usuario=usuario).dates(
        'fecha_gasto', 'year', order='DESC').distinct()

    # Extraer solo el año de cada objeto datetime
    available_years = [fecha.year for fecha in available_years]

    return render(request, 'inventario/graficos/gastos_anuales.html', {
        'titulo': f'Gastos del Año {año_seleccionado}',
        'grafico_url': 'gastos_anuales',
        'gastos_data': gastos_data,
        'available_years': available_years,
        'selected_year': int(año_seleccionado)
    })
