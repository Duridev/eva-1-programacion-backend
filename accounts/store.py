"""
Módulo de almacenamiento en memoria (accounts/store.py).

En cumplimiento con las especificaciones del proyecto:
- No se utiliza una base de datos real ni el ORM de Django.
- Los usuarios registrados se almacenan en la lista 'USERS'.
- Los intentos fallidos de inicio de sesión y el estado de bloqueo
  se gestionan en el diccionario 'LOGIN_ATTEMPTS'.
- Ambas estructuras residen en la memoria del servidor Python.
"""

# Lista de usuarios registrados en el sistema (en memoria).
# Se precarga un usuario de prueba (semilla) para permitir pruebas inmediatas.
USERS = [
    {
        "username": "admin",
        "email": "admin@ejemplo.com",
        "password": "Admin1234"
    }
]

# Diccionario para rastrear intentos de inicio de sesión por usuario.
# Estructura:
# {
#     "nombre_usuario": {
#         "intentos": int,     # Número de intentos fallidos acumulados
#         "bloqueado": bool    # True si alcanzó 3 fallos consecutivos
#     }
# }
LOGIN_ATTEMPTS = {}
