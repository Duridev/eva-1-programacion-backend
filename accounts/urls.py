"""
Rutas de la aplicación accounts (accounts/urls.py).

Define los endpoints correspondientes a la Sección 6 del documento:
- /registro/ -> register_view
- /login/ -> login_view
- /bienvenida/ -> welcome_view
- /logout/ -> logout_view
"""

from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('bienvenida/', views.welcome_view, name='welcome'),
    path('logout/', views.logout_view, name='logout'),
]
