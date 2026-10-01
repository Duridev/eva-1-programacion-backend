from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-sokt7g+y@i5#q#awa!2^+1*(ts54$(rsf0)^4!+vqj+6q)zlvw'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas:
# Se mantienen las aplicaciones del núcleo de Django necesarias para auth, sesiones y mensajes.
# Se registran las apps del proyecto: 'accounts' (usuarios/login) y 'productos' (CRUD).
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'productos',
]

# Middlewares:
# Se incluyen SessionMiddleware, AuthenticationMiddleware (para request.user) y MessageMiddleware.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Nota EVA 2: Se eliminó SESSION_ENGINE = signed_cookies para usar el motor de sesiones en base de datos.

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',      # Entrega la variable 'user' a las plantillas
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de datos: Configuración SQLite por defecto requerida para EVA 2
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuración de URLs para autenticación y decorador @login_required
LOGIN_URL = '/login/'           # Redirige al login si un usuario no autenticado intenta entrar a ruta protegida
LOGIN_REDIRECT_URL = '/'       # Redirección tras iniciar sesión correctamente
