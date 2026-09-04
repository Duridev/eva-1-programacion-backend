"""
Configuración del proyecto Django (config/settings.py).

Este archivo ha sido adaptado para un entorno académico introductorio:
- Se utiliza 'signed_cookies' como motor de sesión para no requerir base de datos.
- Se eliminaron las apps y middlewares de admin, auth y contenttypes para mantener
  el proyecto simple y sin dependencias de base de datos ni migraciones.
- Se configuraron los directorios de templates/ y static/.
"""

from pathlib import Path

# Construcción de rutas dentro del proyecto: BASE_DIR apunta a la raíz del repositorio
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta para desarrollo
SECRET_KEY = 'django-insecure-sokt7g+y@i5#q#awa!2^+1*(ts54$(rsf0)^4!+vqj+6q)zlvw'

# Modo depuración activo para desarrollo local
DEBUG = True

ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas: únicamente sesiones, archivos estáticos y nuestra app 'accounts'
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'accounts',
]

# Middlewares mínimos necesarios (sin autenticación de Django ni base de datos)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Motor de sesiones basado en cookies firmadas criptográficamente
# Esto permite manejar sesiones (request.session) SIN requerir base de datos ni migraciones
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

ROOT_URLCONF = 'config.urls'

# Configuración de plantillas (templates/)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# No se requiere base de datos en este proyecto académico
DATABASES = {}

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
