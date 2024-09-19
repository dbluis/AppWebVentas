from django.contrib import admin
from .models import Bebida, Venta, Gasto, DetalleVenta, Carrito, ItemCarrito

# Register your models here.

admin.site.register(Bebida)
admin.site.register(Venta)
admin.site.register(Gasto)
admin.site.register(DetalleVenta)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
