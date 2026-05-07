from django.shortcuts import render
import os
import json
import bcrypt
import secrets
from io import BytesIO
from xhtml2pdf import pisa
from django.conf import settings
from django.template.loader import get_template
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cliente, Tarjeta, Movimiento, SolicitudTraslado

# Create your views here.

@csrf_exempt
def registro(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)

    try:
        body_json = json.loads(request.body)
    except:
        return JsonResponse({"error": "Faltan parámetros en el cuerpo del JSON"}, status=400)

    json_dni = body_json.get('dni', None)
    json_nombre = body_json.get('nombre', None)
    json_apellidos = body_json.get('apellidos', None)
    json_email = body_json.get('email', None)
    json_telefono = body_json.get('telefono', None)
    json_password = body_json.get('password', None)

    if Cliente.objects.filter(dni=json_dni).exists():
        return JsonResponse({"error": "Este DNI ya está registrado en ABANCA"}, status=409)

    if Cliente.objects.filter(email=json_email).exists():
        return JsonResponse({"error": "Este email ya está en uso"}, status=409)

    salted_and_hashed_pass = bcrypt.hashpw(json_password.encode('utf8'), bcrypt.gensalt()).decode('utf8')
    random_token = secrets.token_hex(10)

    nuevo_cliente = Cliente(
        dni=json_dni,
        nombre=json_nombre,
        apellidos=json_apellidos,
        email=json_email,
        telefono=json_telefono,
        password_cifrada=salted_and_hashed_pass,
        token_sesion=random_token
    )
    nuevo_cliente.save()

    return JsonResponse({"registered": True, "token": random_token, "mensaje": f"Bienvenido/a a ABANCA, {json_nombre}"}, status=201)


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)

    try:
        body_json = json.loads(request.body)
        json_dni = body_json.get('dni')
        json_password = body_json.get('password')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Faltan parámetros en el cuerpo del JSON"}, status=400)

    try:
        db_user = Cliente.objects.get(dni=json_dni)
    except Cliente.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.password_cifrada.encode('utf8')):
        random_token = secrets.token_hex(10)
        db_user.token_sesion = random_token
        db_user.save()

        return JsonResponse({ "token": random_token, "dni": db_user.dni}, status=200)
    else:
        return JsonResponse({"error": "Credenciales inválidas"}, status=401)


@csrf_exempt
def resumen_banca(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)

    authenticated_user = __get_request_user(request)
    if authenticated_user is None:
        return JsonResponse({"error": "Falta el token de sesión o es inválido"}, status=401)

    cuentas = authenticated_user.cuentas.all()
    cuentas_json = []

    for cuenta in cuentas:
        tarjetas = Tarjeta.objects.filter(cuenta=cuenta)
        tarjetas_json = []
        for t in tarjetas:
            tarjetas_json.append({
                "pan": t.pan,
                "tipo": t.tipo,
                "activa": t.activa
            })

        movimientos = Movimiento.objects.filter(cuenta=cuenta).order_by('-fecha')[:5]
        movimientos_json = []
        for m in movimientos:
            movimientos_json.append({
                "concepto": m.concepto,
                "importe": float(m.importe),
                "fecha": m.fecha.strftime('%d/%m/%Y'),
                "tarjeta_asociada": m.tarjeta.pan if m.tarjeta else None
            })

        cuentas_json.append({
            "iban": cuenta.iban,
            "alias": cuenta.alias,
            "saldo": float(cuenta.saldo),
            "tarjetas": tarjetas_json,
            "ultimos_movimientos": movimientos_json
        })
    return JsonResponse(cuentas_json, safe=False, status=200)

@csrf_exempt
def solicitudes(request):
    authenticated_user = __get_request_user(request)
    if authenticated_user is None:
        return JsonResponse({"error": "Falta el token de sesión o es inválido"}, status=401)

    if request.method == 'GET':
        solicitudes = SolicitudTraslado.objects.filter(cliente=authenticated_user)
        json_list = []
        for s in solicitudes:
            json_list.append({
                "id": s.id,
                "referencia": s.referencia,
                "entidad_origen": s.entidad_origen,
                "iban_origen": s.iban_origen,
                "iban_destino": s.iban_destino,
                "estado": s.estado,
                "fecha_ejecucion": s.fecha_ejecucion.strftime('%Y-%m-%d'),
                "fecha_solicitud": s.fecha_solicitud.strftime('%d/%m/%Y %H:%M')
            })

        return JsonResponse(json_list, safe=False, status=200)

    elif request.method == 'POST':
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Faltan parámetros en el cuerpo del JSON"}, status=400)

        campos_obligatorios = ['entidad_origen', 'iban_origen', 'iban_destino', 'fecha_ejecucion']
        for campo in campos_obligatorios:
            if not body_json.get(campo):
                return JsonResponse({"error": f"Falta el campo: {campo}"}, status=400)

        ultima_solicitud = SolicitudTraslado.objects.order_by('-id').first()
        if ultima_solicitud and ultima_solicitud.referencia.startswith('REF'):
            try:
                nuevo_numero = int(ultima_solicitud.referencia[3:]) + 1
            except ValueError:
                nuevo_numero = 1
        else:
            nuevo_numero = 1

        referencia_generada = f"REF{nuevo_numero:04d}"

        nueva_solicitud = SolicitudTraslado(
            cliente=authenticated_user,
            referencia=referencia_generada,
            entidad_origen=body_json['entidad_origen'],
            iban_origen=body_json['iban_origen'],
            iban_destino=body_json['iban_destino'],

            pet_cancelar_ordenes=body_json.get('pet_cancelar_ordenes', False),
            pet_bloquear_entrantes=body_json.get('pet_bloquear_entrantes', False),
            pet_transferir_saldo_cierre=body_json.get('pet_transferir_saldo_cierre', False),
            pet_recibir_info=body_json.get('pet_recibir_info', False),

            act_habilitar_ordenes=body_json.get('act_habilitar_ordenes', False),
            act_aceptar_adeudos=body_json.get('act_aceptar_adeudos', False),
            act_informar_emisores=body_json.get('act_informar_emisores', False),

            fecha_ejecucion=body_json['fecha_ejecucion']
        )
        nueva_solicitud.save()

        return JsonResponse({ "mensaje": "Solicitud de traslado creada con éxito", "referencia": referencia_generada}, status=201)
    else:
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)


@csrf_exempt
def detalle_solicitud(request, refSolicitud):
    authenticated_user = __get_request_user(request)
    if authenticated_user is None:
        return JsonResponse({"error": "Falta el token de sesión o es inválido"}, status=401)
    if request.method == 'GET':
        try:
            solicitud = SolicitudTraslado.objects.get(referencia=refSolicitud, cliente=authenticated_user)
            solicitud_json = {
                "referencia": solicitud.referencia,
                "entidad_origen": solicitud.entidad_origen,
                "iban_origen": solicitud.iban_origen,
                "iban_destino": solicitud.iban_destino,
                "estado": solicitud.estado,
                "fecha_ejecucion": solicitud.fecha_ejecucion.strftime('%Y-%m-%d'),
                "fecha_solicitud": solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M'),

                "pet_cancelar_ordenes": solicitud.pet_cancelar_ordenes,
                "pet_bloquear_entrantes": solicitud.pet_bloquear_entrantes,
                "pet_transferir_saldo_cierre": solicitud.pet_transferir_saldo_cierre,
                "pet_recibir_info": solicitud.pet_recibir_info,

                "act_habilitar_ordenes": solicitud.act_habilitar_ordenes,
                "act_aceptar_adeudos": solicitud.act_aceptar_adeudos,
                "act_informar_emisores": solicitud.act_informar_emisores
            }
            return JsonResponse(solicitud_json, status=200)

        except SolicitudTraslado.DoesNotExist:
            return JsonResponse({"error": "La solicitud no existe"}, status=404)

    elif request.method == 'DELETE':
        try:
            solicitud = SolicitudTraslado.objects.get(referencia=refSolicitud, cliente=authenticated_user)

            if solicitud.estado != 'PENDIENTE':
                return JsonResponse({"error": f"No se puede cancelar la solicitud porque ya está en estado: {solicitud.estado}"}, status=400)

            solicitud.delete()
            return JsonResponse({"mensaje": f"Solicitud con {refSolicitud} eliminada"}, status=200)

        except SolicitudTraslado.DoesNotExist:
            return JsonResponse({"error": "La solicitud no existe"}, status=404)
    else:
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)


@csrf_exempt
def generar_pdf(request, refSolicitud):
    authenticated_user = __get_request_user(request)
    if authenticated_user is None:
        return JsonResponse({"error": "Falta el token de sesión o es inválido"}, status=401)

    try:
        solicitud = SolicitudTraslado.objects.get(referencia=refSolicitud, cliente=authenticated_user)

        logo = os.path.join(settings.BASE_DIR, 'static', 'abanca.png')
        plantilla = get_template('plantilla_pdf_solicitud.html')

        contexto = {
            's': solicitud,
            'ruta_logo': logo
        }

        html = plantilla.render(contexto)
        result = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="solicitud_{refSolicitud}.pdf"'
            return response

        return JsonResponse({"error": "Error interno al generar el PDF"}, status=500)

    except SolicitudTraslado.DoesNotExist:
        return JsonResponse({"error": "La solicitud no existe"}, status=404)

def __get_request_user(request):
    header_token = request.headers.get('Session', None)
    if header_token is None:
        return None
    try:
        return Cliente.objects.get(token_sesion=header_token)
    except Cliente.DoesNotExist:
        return None
