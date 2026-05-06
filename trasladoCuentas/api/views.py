from django.shortcuts import render
import json
import bcrypt
import secrets
from django.http import JsonResponse
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

    #TODO: elif request.method == 'POST':
    else:
        return JsonResponse({'error': 'Método HTTP no soportado'}, status=405)

def __get_request_user(request):
    header_token = request.headers.get('Session', None)
    if header_token is None:
        return None
    try:
        return Cliente.objects.get(token_sesion=header_token)
    except Cliente.DoesNotExist:
        return None
