from django.shortcuts import render
import json
import bcrypt
import secrets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Cliente

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

def __get_request_user(request):
    header_token = request.headers.get('Session', None)
    if header_token is None:
        return None
    try:
        return Cliente.objects.get(token_sesion=header_token)
    except Cliente.DoesNotExist:
        return None
