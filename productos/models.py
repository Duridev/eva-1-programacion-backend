from django.db import models

# Modelo para la tabla de productos en SQLite
class Producto(models.Model):
    # 'id' lo crea Django automáticamente como clave primaria autoincremental
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.nombre} ({self.marca})"
