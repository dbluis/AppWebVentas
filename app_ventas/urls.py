from django.urls import path
from . import views, views_graficos

urlpatterns = [
    # Urls Ventas
    path('', views.index, name='index'),
    path('listar_bebidas', views.listar_bebidas, name='listar_bebidas'),
    path('agregar/', views.agregar_bebida, name='agregar_bebida'),
    path('editar/<int:id>/', views.editar_bebida, name='editar_bebida'),
    path('eliminar/<int:id>/',
         views.eliminar_bebida, name='eliminar_bebida'),
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('ventas/', views.listar_ventas, name='listar_ventas'),
    path('total_ventas/', views.total_ventas, name='total_ventas'),
    path('eliminar_venta/<int:id>/', views.eliminar_venta, name='eliminar_venta'),
    # Carrito
    path('agregar_al_carrito/', views.agregar_al_carrito,
         name='agregar_al_carrito'),
    path('cambiar-cantidad-carrito/', views.cambiar_cantidad_carrito,
         name='cambiar_cantidad_carrito'),
    # Urls Gastos
    path('gastos/', views.listar_gastos, name='listar_gastos'),
    path('gastos/agregar/', views.agregar_gasto, name='agregar_gasto'),
    path('gastos/editar/<int:id>/', views.editar_gasto, name='editar_gasto'),
    path('gastos/eliminar/<int:id>/delete',
         views.eliminar_gasto, name='eliminar_gasto'),
    path("total_gastos/", views.total_gastos, name="total_gastos"),
    # Urls User
    path("crearUser/", views.crearUser, name="crearUser"),
    path("signout/", views.signout, name="signout"),
    path("signin/", views.signin, name="signin"),
    path("crearSuperUser/", views.crearSuperUser, name="crearSuperUser"),
    # Carrito
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/', views.eliminar_del_carrito,
         name='eliminar_del_carrito'),
    path('carrito/completar/', views.completar_compra, name='completar_compra'),
    # Urls Graficos
    path('ventas_mensuales/', views.ventas_mensuales, name='ventas_mensuales'),
    path('gastos_mensuales/', views.gastos_mensuales, name='gastos_mensuales'),
    path('ventas_diarias/', views.ventas_diarias, name='ventas_diarias'),
    path('gastos_diarios/', views.gastos_diarios, name='gastos_diarios'),
    path('ventas_semanales/', views.ventas_semanales, name='ventas_semanales'),
    path('gastos_semanales/', views.gastos_semanales, name='gastos_semanales'),
    path('ventas_anuales/', views.ventas_anuales, name='ventas_anuales'),
    path('gastos_anuales/', views.gastos_anuales, name='gastos_anuales'),
    # Rutas para las vistas que renderizan las plantillas de los gráficos
    path('ver_ventas_mensuales/', views_graficos.ver_ventas_mensuales,
         name='ver_ventas_mensuales'),
    path('ver_gastos_mensuales/', views_graficos.ver_gastos_mensuales,
         name='ver_gastos_mensuales'),
    path('ver_ventas_diarias/', views_graficos.ver_ventas_diarias,
         name='ver_ventas_diarias'),
    path('ver_gastos_diarios/', views_graficos.ver_gastos_diarios,
         name='ver_gastos_diarios'),
    path('ver_ventas_semanales/', views_graficos.ver_ventas_semanales,
         name='ver_ventas_semanales'),
    path('ver_gastos_semanales/', views_graficos.ver_gastos_semanales,
         name='ver_gastos_semanales'),
    path('ver_ventas_anuales/', views_graficos.ver_ventas_anuales,
         name='ver_ventas_anuales'),
    path('ver_gastos_anuales/', views_graficos.ver_gastos_anuales,
         name='ver_gastos_anuales'),
    path("link_graficos/", views.link_graficos, name="link_graficos"),
    # Nuevos graficos:
]
