"""
==============================================================================
ARCHIVO: config/urls.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Es el enrutador principal (dispatcher) de todo el proyecto Django. Cada vez que
un usuario entra a una dirección en el navegador, Django consulta este archivo
para saber qué vista debe responder.

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. Redirecciona automáticamente la ruta raíz '/' (ej: http://127.0.0.1:8000/)
   hacia el formulario de login ('/login/').
2. Conecta e incluye las rutas definidas dentro de la aplicación 'accounts'
   (accounts/urls.py) mediante la función 'include()'.
3. Mantiene el enrutamiento limpio y modular, delegando a cada app sus rutas.
==============================================================================
"""

from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Ruta raíz ('/'): Cuando el usuario ingresa a la raíz del sitio,
    # RedirectView lo redirige inmediatamente a la página de login ('/login/').
    # permanent=False genera una redirección temporal HTTP 302.
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home_redirect'),

    # Delegación de rutas: Cualquier otra ruta es enviada a 'accounts.urls'
    # para ser atendida por la aplicación de cuentas (/registro/, /login/, etc.).
    path('', include('accounts.urls')),
]
