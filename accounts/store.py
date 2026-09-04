"""
==============================================================================
ARCHIVO: accounts/store.py
------------------------------------------------------------------------------
¿PARA QUÉ SIRVE ESTE ARCHIVO?
Actúa como la "base de datos en memoria" del servidor. En lugar de usar una base
de datos relacional (como SQLite, MySQL o PostgreSQL) con modelos u ORM de Django,
aquí almacenamos la información directamente en estructuras de datos de Python.

¿QUÉ FUNCIONES REALIZA DENTRO DEL PROGRAMA?
1. Almacena la lista de usuarios registrados en el sistema (USERS).
2. Precarga un usuario semilla ('admin' / 'Admin1234') para permitir pruebas inmediatas.
3. Almacena el historial de intentos fallidos y el estado de bloqueo de cada cuenta (LOGIN_ATTEMPTS).
4. Mantiene la persistencia durante el ciclo de vida del servidor (se reinicia al reiniciar runserver).
==============================================================================
"""

# ------------------------------------------------------------------------------
# 1. LISTA DE USUARIOS REGISTRADOS (USERS)
# ------------------------------------------------------------------------------
# Cada usuario es un diccionario con:
# - 'username': Nombre de usuario único.
# - 'email': Correo electrónico único.
# - 'password': Clave en texto plano (según simplificación permitida en la especificación).
USERS = [
    {
        "username": "admin",
        "email": "admin@ejemplo.com",
        "password": "Admin1234"
    }
]

# ------------------------------------------------------------------------------
# 2. CONTROL DE INTENTOS Y BLOQUEO EN SERVIDOR (LOGIN_ATTEMPTS)
# ------------------------------------------------------------------------------
# Es un diccionario cuyas claves son los nombres de usuario:
# {
#     "nombre_usuario": {
#         "intentos": int,     # Contador de intentos fallidos consecutivos (1, 2 o 3)
#         "bloqueado": bool    # True cuando llega a 3 intentos fallidos
#     }
# }
# ¿Por qué está aquí y no en JavaScript?
# Para garantizar la seguridad: si el bloqueo estuviera en JS, cualquier usuario
# podría esquivarlo abriendo la consola o desactivando JavaScript.
LOGIN_ATTEMPTS = {}
