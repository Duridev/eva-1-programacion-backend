from django.urls import path
from . import views

# Rutas de la aplicación productos (CRUD)
urlpatterns = [
    path('', views.mostrarIndex, name='mostrar_index'),
    path('form_registrar/', views.mostrarFormRegistrar, name='mostrar_form_registrar'),
    path('insertar/', views.insertarProducto, name='insertar_producto'),
    path('listado/', views.mostrarListado, name='mostrar_listado'),
    path('form_actualizar/<int:id>/', views.mostrarFormActualizar, name='mostrar_form_actualizar'),
    path('actualizar/<int:id>/', views.actualizarProducto, name='actualizar_producto'),
    path('eliminar/<int:id>/', views.eliminarProducto, name='eliminar_producto'),
]
