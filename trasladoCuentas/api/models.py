from django.db import models
from django.db.models import Q

# Create your models here.

class Cliente(models.Model):
    dni = models.CharField(max_length=9, unique=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    password_cifrada = models.CharField(max_length=255)
    token_sesion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.dni}"

class Cuenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cuentas')
    iban = models.CharField(max_length=34, unique=True)
    alias = models.CharField(max_length=50, default="Cuenta Clara")
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.alias} - {self.iban}"


class Tarjeta(models.Model):
    TIPOS = [('DEBITO', 'Débito'), ('CREDITO', 'Crédito')]
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='tarjetas')
    pan = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cuenta.alias} - {self.tipo} ({self.pan})"

class Movimiento(models.Model):
    cuenta = models.ForeignKey('Cuenta', on_delete=models.CASCADE, null=True, blank=True)
    tarjeta = models.ForeignKey('Tarjeta', on_delete=models.CASCADE, null=True, blank=True)
    concepto = models.CharField(max_length=100)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=((Q(cuenta__isnull=False) & Q(tarjeta__isnull=True)) | (Q(cuenta__isnull=True) & Q(tarjeta__isnull=False))),
                name='check_movimiento'
            )
        ]

    def __str__(self):
        return f"{self.concepto} - {self.importe}"


class SolicitudTraslado(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de revisión'),
        ('EN_PROCESO', 'En proceso'),
        ('COMPLETADO', 'Traslado completado'),
        ('RECHAZADO', 'Solicitud rechazada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitudes')
    referencia = models.CharField(max_length=7, unique=True, editable=False)

    entidad_origen = models.CharField(max_length=100)
    iban_origen = models.CharField(max_length=34)
    iban_destino = models.CharField(max_length=34)

    pet_cancelar_ordenes = models.BooleanField(default=False)
    pet_bloquear_entrantes = models.BooleanField(default=False)
    pet_transferir_saldo_cierre = models.BooleanField(default=False)
    pet_recibir_info = models.BooleanField(default=False)

    act_habilitar_ordenes = models.BooleanField(default=False)
    act_aceptar_adeudos = models.BooleanField(default=False)
    act_informar_emisores = models.BooleanField(default=False)

    fecha_ejecucion = models.DateField()

    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    documento_pdf = models.FileField(upload_to='traslados_pdfs/', null=True, blank=True)

    def __str__(self):
        return f"{self.referencia} - {self.cliente.dni} ({self.estado})"