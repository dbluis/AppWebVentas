from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import matplotlib.dates as mdates
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import BebidaForm, GastoForm, VentaForm,  DateForm, MonthYearForm
from .models import Bebida, Venta, DetalleVenta, Gasto, Carrito, ItemCarrito
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import pandas as pd
import matplotlib.pyplot as plt
from calendar import month_name
from django.utils.translation import gettext_lazy as _
from django import forms
from datetime import datetime, time
from django.utils import timezone
from django.db.models import Q, Sum
import pytz
import matplotlib
matplotlib.use('Agg')
# Create your views here.

argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')


def index(request):
    return render(request, "inventario/index.html")


def listar_bebidas(request):
    bebidas = Bebida.objects.filter(user=request.user)

    # Buscador de bebidas
    busqueda = request.GET.get("buscar")
    if busqueda:
        bebidas = Bebida.objects.filter(
            Q(nombre__icontains=busqueda) |
            Q(precio__icontains=busqueda)
        ).distinct()

    # Manejar carrito para usuario autenticado
    if request.user.is_authenticated:
        carrito, _ = Carrito.objects.get_or_create(
            usuario=request.user, completado=False)
        total_precio = sum(item.subtotal() for item in carrito.items.all())
    else:
        carrito = None
        total_precio = 0

    return render(request, 'inventario/listar_bebidas.html', {'bebidas': bebidas, 'carrito': carrito, 'total_precio': total_precio})


# User:


def crearUser(request):
    if request.method == "GET":
        return render(request, "user/crearUser.html")
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('listar_bebidas')
            except IntegrityError:
                return render(request, "user/crearUser.html", {"error": "El usuario ya existe"})


def crearSuperUser(request):
    if request.method == "GET":
        return render(request, "user/crearSuperUser.html")
    else:
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        es_superusuario = request.POST.get('superuser')
        if password1 == password2:
            if password1 == password2:
                try:
                    user = User.objects.create_user(
                        username=username, password=password1)
                    if es_superusuario:
                        user.is_superuser = True
                        user.is_staff = True
                    user.save()
                    messages.success(
                        request, "Superusuario creado exitosamente.")
                    return redirect('login')  # Redirigir a la página de login
                except Exception as e:
                    messages.error(request, f"Error: {e}")
        else:
            messages.error(request, "Las contraseñas no coinciden.")
    return render(request, 'user/crearSuperUser.html')


def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == "GET":
        return render(request, "user/signin.html")
    else:
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, "user/signin.html", {"error": "El usuario o contraseña no coinciden. O necesita abonar el servicio"})
        else:
            login(request, user)
            return redirect('listar_bebidas')


# CRUD Bebidas:

@login_required
def agregar_bebida(request):
    if request.method == 'POST':
        form = BebidaForm(request.POST)
        if form.is_valid():
            new_material = form.save(commit=False)
            new_material.user = request.user
            new_material.save()
            return redirect('listar_bebidas')
    else:
        form = BebidaForm()
    return render(request, 'inventario/agregar_bebida.html', {'form': form})


@login_required
def editar_bebida(request, id):
    bebida = get_object_or_404(Bebida, id=id, user=request.user)
    if request.method == 'POST':
        form = BebidaForm(request.POST, instance=bebida)
        if form.is_valid():
            form.save()
            return redirect('listar_bebidas')
    else:
        form = BebidaForm(instance=bebida)
    return render(request, 'inventario/editar_bebida.html', {'form': form, 'bebida': bebida})


@login_required
def eliminar_bebida(request, id):
    bebida = get_object_or_404(Bebida, pk=id, user=request.user)
    if request.method == 'POST':
        bebida.delete()
        return redirect('listar_bebidas')

# Venta

# No usado por el momento registar_venta.


@login_required
def registrar_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_bebidas')
    else:
        form = VentaForm()
    return render(request, 'inventario/registrar_venta.html', {'form': form})


@login_required
def listar_ventas(request):
    ventas = Venta.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'inventario/listar_ventas.html', {'ventas': ventas})


@login_required
def eliminar_venta(request, id):
    venta = get_object_or_404(Venta, id=id, usuario=request.user)
    if request.method == 'POST':
        venta.delete()
        # Redirige a la vista de listado de ventas
        return redirect('listar_ventas')
    return render(request, 'inventario/eliminar_venta.html', {'venta': venta})


@login_required
def total_ventas(request):
    formd = DateForm(request.GET or None)
    if formd.is_valid() and formd.cleaned_data['date']:
        selected_date = formd.cleaned_data['date']
    else:
        selected_date = timezone.now().astimezone(argentina_tz).date()

    # Inicio y fin del día seleccionado con zona horaria
    start_of_day = datetime.combine(
        selected_date, time.min).astimezone(argentina_tz)
    end_of_day = datetime.combine(
        selected_date, time.max).astimezone(argentina_tz)

    # Filtrar ventas del día
    ventas_dia = Venta.objects.filter(
        fecha__range=(start_of_day, end_of_day),
        usuario=request.user
    ).aggregate(total=Sum('total'))['total'] or 0

    form = MonthYearForm(request.GET or None)
    if form.is_valid() and form.cleaned_data['month'] and form.cleaned_data['year']:
        selected_month = int(form.cleaned_data['month'])
        selected_year = int(form.cleaned_data['year'])
    else:
        now = timezone.now().astimezone(argentina_tz)
        selected_month = now.month
        selected_year = now.year

    # Filtrar ventas del mes
    ventas_mes = Venta.objects.filter(
        fecha__year=selected_year,
        fecha__month=selected_month,
        usuario=request.user
    ).aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'inventario/total_ventas.html', {
        'ventas_dia': ventas_dia,
        'ventas_mes': ventas_mes,
        'form': form,
        'formd': formd
    })


# CRUD Gasto:

@login_required
def listar_gastos(request):
    gastos = Gasto.objects.filter(
        usuario=request.user).order_by('-fecha_gasto')
    return render(request, 'inventario/listar_gastos.html', {'gastos': gastos})


@login_required
def agregar_gasto(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.usuario = request.user  # Asocia el usuario actual al gasto
            gasto.save()
            return redirect('listar_gastos')
    else:
        form = GastoForm()
    return render(request, 'inventario/agregar_gasto.html', {'form': form})


@login_required
def editar_gasto(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            return redirect('listar_gastos')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'inventario/editar_gasto.html', {'form': form, "gasto": gasto})


@login_required
def eliminar_gasto(request, id):
    gasto = get_object_or_404(Gasto, id=id, usuario=request.user)
    if request.method == 'POST':
        gasto.delete()
        return redirect('listar_gastos')
    return render(request, 'inventario/eliminar_gasto.html', {'gasto': gasto})


@login_required
def total_gastos(request):
    formd = DateForm(request.GET or None)
    if formd.is_valid() and formd.cleaned_data['date']:
        selected_date = formd.cleaned_data['date']
    else:
        selected_date = timezone.now().astimezone(argentina_tz).date()

    # Inicio y fin del día seleccionado con zona horaria
    start_of_day = datetime.combine(
        selected_date, time.min).astimezone(argentina_tz)
    end_of_day = datetime.combine(
        selected_date, time.max).astimezone(argentina_tz)

    # Filtrar gastos del día
    gastos_dia = Gasto.objects.filter(
        fecha_gasto__range=(start_of_day, end_of_day),
        usuario=request.user
    ).aggregate(total=Sum('monto'))['total'] or 0

    form = MonthYearForm(request.GET or None)
    if form.is_valid() and form.cleaned_data['month'] and form.cleaned_data['year']:
        selected_month = int(form.cleaned_data['month'])
        selected_year = int(form.cleaned_data['year'])
    else:
        now = timezone.now().astimezone(argentina_tz)
        selected_month = now.month
        selected_year = now.year

    # Filtrar gastos del mes
    gastos_mes = Gasto.objects.filter(
        fecha_gasto__year=selected_year,
        fecha_gasto__month=selected_month,
        usuario=request.user
    ).aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'inventario/total_gastos.html', {
        'gastos_dia': gastos_dia,
        'gastos_mes': gastos_mes,
        'form': form,
        'formd': formd
    })
# Graficos y reportes


@login_required
def ventas_mensuales(request):
    # Recuperar el usuario actual
    usuario = request.user

    # Obtener el mes y año actuales
    now = timezone.now()
    year = now.year
    month = now.month

    # Filtrar las ventas del usuario actual para el mes actual
    ventas = Venta.objects.filter(
        usuario=usuario, fecha__year=year, fecha__month=month)

    # Crear un DataFrame de las ventas
    df = pd.DataFrame(list(ventas.values('fecha', 'total')))
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)

    # Resamplear las ventas diarias y sumarlas
    df_resampled = df.resample('D').sum()

    # Traducir el nombre del mes al español
    nombre_mes = _(month_name[month])

    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df_resampled.index,
             df_resampled['total'], marker='o', linestyle='-')
    plt.xlabel('Día del Mes')
    plt.ylabel('Ventas Totales')
    plt.title(f'Ventas del Mes de {nombre_mes} {year}')
    plt.grid(True)
    plt.tight_layout()

    # Guardar el gráfico en un buffer de memoria
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convertir el buffer a una respuesta HTTP
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="ventas_mensuales.png"'

    return response


@login_required
def gastos_mensuales(request):
    current_year = timezone.now().year
    gastos = Gasto.objects.filter(
        fecha_gasto__year=current_year, usuario=request.user)

    df = pd.DataFrame(gastos.values('fecha_gasto', 'monto'))
    df['fecha_gasto'] = pd.to_datetime(df['fecha_gasto']).dt.tz_localize(
        timezone.get_current_timezone(), ambiguous='NaT', nonexistent='NaT')
    df = df.set_index('fecha_gasto').resample('M').sum()

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['monto'], marker='o')
    plt.title('Gastos Mensuales (Año Actual)')
    plt.xlabel('Mes')
    plt.ylabel('Monto Gastado')
    plt.grid(True)

    response = HttpResponse(content_type="image/png")
    plt.savefig(response, format="png")
    plt.close()
    return response

# .----------.


@login_required
def ventas_diarias(request):
    # Filtrar las ventas del usuario
    user_ventas = Venta.objects.filter(usuario=request.user)
    df = pd.DataFrame(user_ventas.values('fecha', 'total'))

    # Convertir a datetime y eliminar timezone
    df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_convert(
        'America/Argentina/Buenos_Aires')

    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=['fecha'])

    df.set_index('fecha', inplace=True)

    # Rango para el día de hoy en zona horaria de Argentina
    today = pd.Timestamp.now(tz='America/Argentina/Buenos_Aires').normalize()
    df_filtered = df[today:today + pd.Timedelta(days=1)]

    # Resample por hora para ventas diarias
    df_resampled = df_filtered.resample('H').sum()

    # Convertir la columna 'total' a numérico
    df_resampled['total'] = pd.to_numeric(
        df_resampled['total'], errors='coerce')

    if df_resampled.empty or df_resampled['total'].isna().all():
        return HttpResponse("No hay datos para mostrar para el día de hoy.", content_type="text/plain")

    # Agrupar por hora del día
    df_resampled['hora'] = df_resampled.index.hour
    df_grouped = df_resampled.groupby('hora').sum()

    fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar el tamaño del gráfico
    df_grouped.plot(kind='bar', y='total', ax=ax, color='skyblue')
    ax.set_title('Ventas a lo largo del Día', fontsize=14)
    ax.set_xlabel('Hora del Día', fontsize=12)
    ax.set_ylabel('Total', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Etiquetas de las horas en formato 24 horas
    ax.set_xticks(range(24))
    ax.set_xticklabels([f'{i:02d}:00' for i in range(24)],
                       fontsize=10, rotation=45)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')


@login_required
def gastos_diarios(request):
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    user_gastos = Gasto.objects.filter(usuario=request.user)
    df = pd.DataFrame(user_gastos.values('fecha_gasto', 'monto'))
    df['fecha_gasto'] = pd.to_datetime(df['fecha_gasto'])
    df.set_index('fecha_gasto', inplace=True)

    start_date_naive = pd.Timestamp(
        request.GET.get('start_date', '2023-01-01'))
    end_date_naive = pd.Timestamp(request.GET.get(
        'end_date', pd.Timestamp.now().strftime('%Y-%m-%d')))

    df_filtered = df[start_date_naive:end_date_naive]
    df_resampled = df_filtered.resample('D').sum()

    fig, ax = plt.subplots()
    df_resampled.plot(kind='bar', ax=ax)
    ax.set_title('Gastos Diarios')
    ax.set_xlabel('Día')
    ax.set_ylabel('Monto')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')

# .----------.


@login_required
def ventas_semanales(request):
    user_ventas = Venta.objects.filter(usuario=request.user)
    df = pd.DataFrame(user_ventas.values('fecha', 'total'))

    # Convertir a datetime y eliminar timezone
    df['fecha'] = pd.to_datetime(df['fecha']).dt.tz_localize(None)

    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=['fecha'])

    df.set_index('fecha', inplace=True)

    # Rango de los últimos 7 días
    end_date_naive = pd.Timestamp.now()
    start_date_naive = end_date_naive - pd.Timedelta(days=7)

    df_filtered = df[start_date_naive:end_date_naive]
    # Resample diario en lugar de semanal
    df_resampled = df_filtered.resample('D').sum()

    # Convertir la columna 'total' a numérico
    df_resampled['total'] = pd.to_numeric(
        df_resampled['total'], errors='coerce')

    if df_resampled.empty or df_resampled['total'].isna().all():
        return HttpResponse("No hay datos para mostrar en el rango de fechas seleccionado.", content_type="text/plain")

    fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar el tamaño del gráfico
    df_resampled.plot(kind='line', y='total', ax=ax,
                      marker='o', linestyle='-', color='skyblue')
    ax.set_title('Ventas de los Últimos 7 Días', fontsize=14)
    ax.set_xlabel('Día', fontsize=12)
    ax.set_ylabel('Total', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Ajustar etiquetas del eje x para que no se solapen y mostrar el formato correcto
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.xticks(rotation=45, ha='right', fontsize=10)

    # Asegurar que se ajusten correctamente las etiquetas del eje x
    fig.autofmt_xdate()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')

# Carrito de compras:


@login_required
def cambiar_cantidad_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        accion = request.POST.get('accion')

        item = get_object_or_404(
            ItemCarrito, id=item_id, carrito__usuario=request.user)

        if accion == 'incrementar':
            item.cantidad += 1
        elif accion == 'decrementar' and item.cantidad > 1:
            item.cantidad -= 1

        item.save()

        # Calcular el total del carrito actualizado
        total_precio = sum(item.subtotal()
                           for item in item.carrito.items.all())

        return JsonResponse({
            'cantidad': item.cantidad,
            'subtotal': item.subtotal(),
            'total_precio': total_precio
        })


@login_required
def gastos_semanales(request):
    user_gastos = Gasto.objects.filter(usuario=request.user)
    df = pd.DataFrame(user_gastos.values('fecha_gasto', 'monto'))

    # Convertir a datetime y eliminar timezone
    df['fecha_gasto'] = pd.to_datetime(df['fecha_gasto']).dt.tz_localize(None)

    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=['fecha_gasto'])

    df.set_index('fecha_gasto', inplace=True)

    # Rango de los últimos 7 días
    end_date_naive = pd.Timestamp.now()
    start_date_naive = end_date_naive - pd.Timedelta(days=7)

    df_filtered = df[start_date_naive:end_date_naive]
    # Resample diario en lugar de semanal
    df_resampled = df_filtered.resample('D').sum()

    # Convertir la columna 'monto' a numérico
    df_resampled['monto'] = pd.to_numeric(
        df_resampled['monto'], errors='coerce')

    if df_resampled.empty or df_resampled['monto'].isna().all():
        return HttpResponse("No hay datos para mostrar en el rango de fechas seleccionado.", content_type="text/plain")

    fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar el tamaño del gráfico
    df_resampled.plot(kind='line', y='monto', ax=ax,
                      marker='o', linestyle='-', color='salmon')
    ax.set_title('Gastos Diarios de los Últimos 7 Días', fontsize=14)
    ax.set_xlabel('Día', fontsize=12)
    ax.set_ylabel('Monto', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Ajustar etiquetas del eje x para que no se solapen y mostrar el formato correcto
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.xticks(rotation=45, ha='right', fontsize=10)

    # Asegurar que se ajusten correctamente las etiquetas del eje x
    fig.autofmt_xdate()

    # Verificar fechas en df_resampled para debugging
    print("Fechas en df_resampled:")
    print(df_resampled.index)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')


@login_required
def ventas_anuales(request):
    usuario = request.user

    # Obtener todas las ventas del usuario actual
    ventas = Venta.objects.filter(usuario=usuario)

    # Crear un DataFrame de las ventas
    df = pd.DataFrame(list(ventas.values('fecha', 'total')))
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)

    # Resumir las ventas por mes
    df_resampled = df.resample('M').sum()

    # Extraer los nombres de los meses y los totales de ventas
    meses = df_resampled.index.strftime('%B').tolist()
    ventas_mensuales = df_resampled['total'].tolist()

    # Pasar los datos al contexto
    context = {
        'meses': meses,
        'ventas_mensuales': ventas_mensuales
    }

    return render(request, 'inventario/graficos/ventas_anuales.html', context)


@login_required
def gastos_anuales(request):
    gastos = Gasto.objects.filter(usuario=request.user)
    df = pd.DataFrame(gastos.values('fecha_gasto', 'monto'))
    df['fecha_gasto'] = pd.to_datetime(df['fecha_gasto'])
    df = df.set_index('fecha_gasto').resample('Y').sum()

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['monto'], marker='o')
    plt.title('Gastos Anuales')
    plt.xlabel('Año')
    plt.ylabel('Monto Gastado')
    plt.grid(True)

    response = HttpResponse(content_type="image/png")
    plt.savefig(response, format="png")
    plt.close()
    return response


# Vista para agregar al carrito usando AJAX
@login_required
def agregar_al_carrito(request):
    if request.method == 'POST':
        bebida_id = request.POST.get('bebida_id')
        bebida = get_object_or_404(Bebida, id=bebida_id)
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user, completado=False)

        # Obtener o crear el item del carrito
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito, bebida=bebida, defaults={'precio': bebida.precio, 'cantidad': 1})

        # Si el item ya existía, incrementar la cantidad
        if not created:
            item.cantidad += 1
            item.save()

        # Calcular el total de items y el precio total en el carrito
        total_items = carrito.items.count()
        total_precio = sum(item.subtotal() for item in carrito.items.all())

        return JsonResponse({'total_items': total_items, 'total_precio': total_precio})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista para eliminar del carrito usando AJAX


@login_required
def eliminar_del_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(ItemCarrito, id=item_id)
        item.delete()

        carrito = get_object_or_404(
            Carrito, usuario=request.user, completado=False)
        total_items = carrito.items.count()
        total_precio = sum(item.subtotal() for item in carrito.items.all())
        return JsonResponse({'total_items': total_items, 'total_precio': total_precio})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para completar la compra


@login_required
def completar_compra(request):
    carrito = get_object_or_404(
        Carrito, usuario=request.user, completado=False)
    venta = Venta.objects.create(usuario=request.user, total=sum(
        item.subtotal() for item in carrito.items.all()))
    for item in carrito.items.all():
        bebida = item.bebida
        bebida.save()
        DetalleVenta.objects.create(
            venta=venta, bebida=bebida, cantidad=item.cantidad, precio=item.precio)
    carrito.completado = True
    carrito.save()
    return redirect('listar_bebidas')

# Pagina para ver los graficos


@login_required
def link_graficos(request):
    return render(request, "inventario/link_graficos.html")
