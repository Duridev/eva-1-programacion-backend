"""
Configuración de URLs principales del proyecto (config/urls.py).

- Redirige la raíz '/' hacia '/login/'.
- Incluye las rutas de la aplicación 'accounts'.
- No incluye 'admin' para cumplir con la arquitectura sin base de datos.
"""

from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirección de la raíz '/' al login según sección 6
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home_redirect'),

    # Inclusión de todas las URLs de autenticación y cuentas
    path('', include('accounts.urls')),
]
