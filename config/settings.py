"""
==============================================================================
ARCHIVO: config/settings.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Es el archivo central de configuración de todo el proyecto Django. Aquí se define
el comportamiento global de la aplicación: qué componentes están activos, cómo
se manejan las sesiones, dónde están las plantillas (HTML) y archivos estáticos (CSS/JS).

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. Configura 'signed_cookies' para manejar sesiones sin necesidad de base de datos.
2. Registra las aplicaciones activas (sesiones, archivos estáticos y 'accounts').
3. Establece la lista de Middlewares mínimos para procesar peticiones web de forma segura.
4. Define las carpetas 'templates/' y 'static/' para que Django sepa dónde buscarlas.
5. Ajusta el idioma al español y la zona horaria.
==============================================================================
"""

from pathlib import Path

# BASE_DIR: Ruta raíz absoluta de la carpeta del proyecto en tu computador
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave criptográfica para firmar cookies de sesión y tokens de seguridad (CSRF)
SECRET_KEY = 'django-insecure-sokt7g+y@i5#q#awa!2^+1*(ts54$(rsf0)^4!+vqj+6q)zlvw'

# DEBUG = True: Muestra detalles de error en pantalla mientras estamos desarrollando
DEBUG = True

# Hosts permitidos para recibir peticiones ('*' permite desarrollo local en localhost)
ALLOWED_HOSTS = ['*']

# ------------------------------------------------------------------------------
# APLICACIONES INSTALADAS (INSTALLED_APPS)
# ------------------------------------------------------------------------------
# Nota para el profesor: Se eliminaron 'admin', 'auth' y 'contenttypes' porque
# este proyecto no utiliza base de datos real. Solo dejamos lo indispensable:
# - sessions: para recordar el usuario logueado.
# - staticfiles: para servir los archivos CSS y JS.
# - accounts: nuestra app personalizada con la lógica de registro y login.
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'accounts',
]

# ------------------------------------------------------------------------------
# MIDDLEWARES
# ------------------------------------------------------------------------------
# Son capas intermedias por las que pasa cada petición (request) y respuesta (response):
# - SecurityMiddleware: Seguridad básica de encabezados HTTP.
# - SessionMiddleware: Habilita el uso de 'request.session'.
# - CommonMiddleware: Manejo de URLs y barras finales.
# - CsrfViewMiddleware: Protección contra ataques CSRF en formularios POST.
# - XFrameOptionsMiddleware: Protección contra ataques de tipo clickjacking.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------------------------------------
# MOTOR DE SESIONES (SESSION_ENGINE)
# ------------------------------------------------------------------------------
# ¿Por qué signed_cookies?
# Por defecto, Django guarda las sesiones en una tabla de base de datos (django_session).
# Al usar 'signed_cookies', la información de la sesión viaja en una cookie encriptada
# en el navegador del usuario, permitiendo recordar el login SIN requerir base de datos
# ni tener que ejecutar 'python manage.py migrate'.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Archivo de rutas principales del proyecto
ROOT_URLCONF = 'config.urls'

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE PLANTILLAS (TEMPLATES)
# ------------------------------------------------------------------------------
# Le indica al motor de plantillas de Django que busque archivos HTML dentro de
# la carpeta 'templates/' ubicada en la raíz del proyecto.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta raíz templates/
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

# Punto de entrada para servidores web WSGI
WSGI_APPLICATION = 'config.wsgi.application'

# ------------------------------------------------------------------------------
# BASE DE DATOS (DATABASES)
# ------------------------------------------------------------------------------
# Queda vacía ({}) porque según el enunciado académico, el almacenamiento
# se realiza en memoria en 'accounts/store.py' y las sesiones en cookies firmadas.
DATABASES = {}

# ------------------------------------------------------------------------------
# INTERNACIONALIZACIÓN Y ZONA HORARIA
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS (CSS, JAVASCRIPT, IMÁGENES)
# ------------------------------------------------------------------------------
# STATIC_URL: Prefijo en la URL para acceder a estáticos (ej: /static/css/styles.css)
STATIC_URL = 'static/'
# STATICFILES_DIRS: Carpeta física donde guardamos nuestros archivos CSS, JS e imágenes
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
