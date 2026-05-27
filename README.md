<p align="center">
  <img src="https://github.com/davidnoya/PFC-DAM-Frontend/blob/main/trasladoCuentas/app/src/main/res/drawable/dbanca.png" width="300" alt="Logo de dBANCA">
</p>

---

Este proyecto es una aplicación Android que digitaliza el proceso de traslado de cuentas bancarias entre entidades, proporcionando una solución moderna, accesible y realista inspirada en un entorno financiero real..

---

## 📌 Índice

- [Descripción](#-descripción)
- [Tecnologías](#️-tecnologías)
- [Instalación](#-instalación)
- [Cómo iniciar la aplicación](#-cómo-iniciar-la-aplicación)
- [Uso](#-uso)
- [Estado del Proyecto](#-estado-del-proyecto)
- [Estructura del Proyecto](#️-estructura-del-proyecto)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🧾 Descripción

La aplicación simula el proceso completo de traslado de una cuenta bancaria por parte de un cliente desde su banca electrónica hacia la nueva entidad (dBANCA). Permite:

- Registro y autenticación segura mediante tokens.
- Visualización de un pequeño resumen de las cuentas, tarjetas y movimientos de cliente dBANCA
- Visualización del estado de las solicitudes desde un panel de control (Dashboard).
- Creación guiada de nuevas solicitudes mediante un asistente paso a paso.
- Edición dinámica de los parámetros de la solicitud.
- Generación y descarga de comprobantes en formato PDF directamente al dispositivo móvil.

Este proyecto nace con el objetivo de aplicar conocimientos adquiridos en desarrollo multiplataforma a un escenario realista y con valor funcional más allá del ámbito académico (Proyecto Final de Ciclo - 2º DAM).

---

## 🛠️ Tecnologías

### Frontend (Android)
- **Lenguaje:** Java
- **Arquitectura:** Arquitectura de Activities (con algunos Fragments para el paso de creación).
- **Red:** Volley (para peticiones asíncronas a la API)
- **Descargas:** Android `DownloadManager` nativo.

### Backend (Django)
- **Lenguaje:** Python
- **API:** endpoints (GET, POST, PUT, DELETE)
- **Autenticación:** Mediante token.
- **Base de Datos:** SQLite

### Control de versiones y Repositorios
- Git
- GitHub Frontend ([Repositorio](https://github.com/davidnoya/PFC-DAM-Frontend))
- GitHub Backend ([Repositorio](https://github.com/davidnoya/PFC-DAM-Backend))

---

## 💻 Instalación

### Requisitos previos
Para poder ejecutar este proyecto en tu entorno local, necesitarás:
1. **Android Studio** instalado
2. **Python 3.10** instalado.
3. Un emulador de Android o un dispositivo físico conectado.
4. **Git** para clonar los repositorios.

---

## 🏁 Cómo iniciar la aplicación

El proyecto consta de dos partes que deben ejecutarse simultáneamente: el servidor (Backend) y la aplicación móvil (Frontend).

### Paso 1: Levantar el Backend (Django)
1. Clona el repositorio del backend:
   ``` text
   git clone [https://github.com/davidnoya/PFC-DAM-Backend.git](https://github.com/davidnoya/PFC-DAM-Backend.git)
   ``` 
3. Crea y activa un entorno virtual:
   ``` text
   python -m venv venv
   source venv/Scripts/activate
   ``` 
5. Instala las dependencias y arranca el servidor
   ``` text
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ``` 
### Paso 2: Levantar el Frontend (Android)
1. Clona el repositorio del frontend:
   git clone [https://github.com/davidnoya/PFC-DAM-Frontend.git](https://github.com/davidnoya/PFC-DAM-Frontend.git)

2. Abre el proyecto en Android Studio
3. Sincroniza el proyecto con Gradle
4. Ejecuta la aplicación en el emulador

---

## 🚀 Uso

El flujo principal de la aplicación está diseñado para ser intuitivo y simular una experiencia bancaria real:

1. **Registro:** Creación de una nueva cuenta de cliente en el sistema de dBANCA, introduciendo los datos personales.
2. **Login:** Autenticación mediante usuario y contraseña para acceder a la banca electrónica.
3. **MainActivity (Inicio):** Pantalla principal de bienvenida que ofrece un vistazo general a la banca personal del usuario y sirve como menú central para acceder a las diferentes operaciones (como el módulo de traslado de cuentas).
4. **Dashboard de Solicitudes:** Panel de control donde se listan todas las solicitudes de traslado activas. Si pulsas sobre ellas tendrás información al detalle de esta.
5. **Nueva Solicitud:** A través de la navegación, se accede al asistente de 4 pasos para tramitar la portabilidad:
   - *Paso 1:* Selección de entidad de origen e IBAN.
   - *Paso 2:* Cuenta de destino y fecha de ejecución.
   - *Paso 3:* Selección de peticiones a la antigua entidad.
   - *Paso 4:* Confirmación de actuaciones de dBANCA y envío seguro al servidor.

---

## 🔧 Estado del Proyecto
![STATUS](https://img.shields.io/badge/STATUS-FINALIZADO-brightgreen)

El proyecto se encuentra actualmente **finalizado**. Todas las funcionalidades principales establecidas para el Proyecto Final de Ciclo han sido desarrolladas y probadas con éxito. Esto incluye el flujo completo de registro y autenticación, la conexión bidireccional con la API REST en Django, la gestión del estado de las solicitudes y la implementación del asistente para crearlas.

---

## 🗂️ Estructura del Proyecto

El sistema está dividido en dos repositorios independientes con la siguiente arquitectura de carpetas principal:

### 📱 Frontend (Android - Java)
La estructura sigue una arquitectura limpia orientada a separar la lógica de datos de la interfaz de usuario.

```text
PFC-DAM-Frontend/
├── app/src/main/java/com/pfc/trasladocuentas/
│   ├── models/
│   │   └── IbanFormatter.java
│   ├── ui/
│   │   ├── DasboardActivity.java
│   │   ├── DesplegableDetalle.java
│   │   ├── LoginActivity.java
│   │   ├── MainActivity.java
│   │   ├── NuevaSolicitudActivity.java
│   │   ├── Paso1Fragment.java
│   │   ├── Paso2Fragment.java
│   │   ├── Paso3Fragment.java
│   │   ├── Paso4Fragment.java
│   │   └── RegistroActivity.java
│   │   
│   ├── JsonArrayRequestWithCustomAuth.java
│   └── JsonObjectRequestWithCustomAuth.java
│
└── app/src/main/res/       
    ├── layout/
    │       ├── activity_dashboard.xml
    │       ├── activity_login.xml
    │       ├── activity_main.xml
    │       ├── activity_nueva_solicitud.xml
    │       ├── activity_registro.xml
    │       ├── detalle.xml
    │       ├── fragment_paso1.xml
    │       ├── fragment_paso2.xml
    │       ├── fragment_paso3.xml
    │       ├── fragment_paso4.xml
    │       ├── item_cuenta.xml
    │       ├── item_detalle.xml
    │       ├── item_movimiento.xml
    │       ├── item_solicitud.xml
    │       ├── item_tarjeta.xml
    │
    ├── menu/
    │       ├── menu_fragments.xml
    │       ├── menu_resumen.xml
    │       └── menu_traslados.xml
    │
    ├── values/             
    └── drawable/ 
           ├── cabecera.xml
           ├── dbanca.png
           ├── desplegable_detalle.xml
           ├── ic_atras.xml
           ├── ic_cuenta.xml
           ├── ic_launcher_background.xml
           ├── ic_launcher_foreground.xml
           ├── ic_menu.xml
           ├── ic_nueva.xml
           ├── ic_tarjeta.xml
           └── menu.xml
```   

### ⚙️ Backend (Django - Python)
La estructura sigue el patrón MVT clásico de Django, adaptado para funcionar como una API REST.
```text
PFC-DAM-Backend/
├── trasladoCuentas              
│   ├── manage.py
│   ├── api/
│   │   ├── __init.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   │   
│   ├── trasladoCuentas/
│   │   ├── __init.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │   
│   ├── static/
│   │   └── dbanca.png
│   │   
│   ├── templates/
│   │   └── plantilla_pdf_solicitud.html
│   │   
│   └── db.sqlite3      
└── .venv
```

---

## 📄 Licencia

Este proyecto se entrega como parte del Proyecto Final de Ciclo (2º DAM) y no tiene licencia específica de momento.

---

## 📬 Personas desarrolladoras del proyecto

- **David Noya Vázquez**  
  📧 *dnoyav23@fpcoruna.afundacion.org*  
  🔗 [GitHub](https://github.com/davidnoya)
