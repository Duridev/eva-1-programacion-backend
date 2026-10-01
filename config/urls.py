from django.urls import path, include

# Mapeo general de rutas del proyecto
urlpatterns = [
    # Rutas de la app accounts (/registro/, /login/, /logout/)
    path('', include('accounts.urls')),
    # Rutas de la app productos (menú principal '/', /listado/, /form_registrar/, etc.)
    path('', include('productos.urls')),
]