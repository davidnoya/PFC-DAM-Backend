from django.contrib import admin
from .models import Cliente, Cuenta, Tarjeta, Movimiento, SolicitudTraslado

# Register your models here.

admin.site.register(Cliente)
admin.site.register(Cuenta)
admin.site.register(Tarjeta)
admin.site.register(Movimiento)
admin.site.register(SolicitudTraslado)
