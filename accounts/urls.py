"""
==============================================================================
ARCHIVO: accounts/urls.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Es el enrutador específico de la aplicación 'accounts'. Asocia cada URL que el
usuario puede visitar en el navegador con su función controladora correspondiente
en 'accounts/views.py'.

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. Vincula la URL '/registro/' con la función 'register_view'.
2. Vincula la URL '/login/' con la función 'login_view'.
3. Vincula la URL '/bienvenida/' con la función 'welcome_view'.
4. Vincula la URL '/logout/' con la función 'logout_view'.
5. Asigna nombres internos (name='...') para poder referenciar rutas fácilmente.
==============================================================================
"""

from django.urls import path
from . import views

urlpatterns = [
    # Ruta para mostrar y procesar el registro de usuarios
    path('registro/', views.register_view, name='register'),

    # Ruta para mostrar y procesar el inicio de sesión y control de intentos
    path('login/', views.login_view, name='login'),

    # Ruta protegida de bienvenida visible únicamente con sesión iniciada
    path('bienvenida/', views.welcome_view, name='welcome'),

    # Ruta para cerrar la sesión activa y limpiar cookies
    path('logout/', views.logout_view, name='logout'),
]
