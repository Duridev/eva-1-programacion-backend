from django.urls import path

from . import views

urlpatterns = [
    path('registro/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),

    path('bienvenida/', views.welcome_view, name='welcome'),

    path('logout/', views.logout_view, name='logout'),
]
