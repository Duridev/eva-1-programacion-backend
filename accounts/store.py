
# Diccionario en memoria para controlar intentos fallidos de inicio de sesión
# Estructura: { "username": { "intentos": int, "bloqueado": bool } }
# Nota EVA 2: La lista USERS fue eliminada porque los usuarios ahora se guardan en la tabla auth_user de SQLite.
LOGIN_ATTEMPTS = {}
