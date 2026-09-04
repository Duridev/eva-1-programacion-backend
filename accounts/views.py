"""
Vistas de la aplicación accounts (accounts/views.py).

Implementación del comportamiento especificado en la Sección 7 y 8 (formato EDD:
Dado / Cuando / Entonces) para:
- register_view: Registro de usuarios y validaciones de datos.
- login_view: Autenticación, control de intentos fallidos y bloqueo en servidor.
- welcome_view: Página protegida por sesión de Django (signed_cookies).
- logout_view: Cierre de sesión y limpieza de cookies de sesión.
"""

from django.shortcuts import render, redirect
from .store import USERS, LOGIN_ATTEMPTS


def register_view(request):
    """
    Vista de registro de nuevos usuarios.
    
    Dado GET: Presenta el formulario de registro vacío.
    Dado POST: Realiza las validaciones en el servidor (Django) y, si son correctas,
               almacena el usuario en la lista en memoria 'USERS'.
    """
    if request.method == 'GET':
        return render(request, 'accounts/register.html')

    # Procesamiento del formulario POST
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    errors = []

    # 1. Validación de campos obligatorios
    if not username:
        errors.append("El nombre de usuario es obligatorio.")
    if not email:
        errors.append("El correo electrónico es obligatorio.")
    if not password:
        errors.append("La contraseña es obligatoria.")

    # 2. Validación de usuario único (recorrer USERS en memoria)
    if username and any(u['username'].lower() == username.lower() for u in USERS):
        errors.append("El nombre de usuario ya está en uso.")

    # 3. Validación de correo único (recorrer USERS en memoria)
    if email and any(u['email'].lower() == email for u in USERS):
        errors.append("El correo ya está registrado.")

    # 4. Validaciones de complejidad de contraseña
    if password:
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        if not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")
        if not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número.")

    # 5. Validación de coincidencia de contraseñas
    if password and confirm_password and password != confirm_password:
        errors.append("Las contraseñas no coinciden.")

    # Si hay errores, se vuelve a mostrar el formulario con los mensajes y valores previos
    if errors:
        return render(request, 'accounts/register.html', {
            'errors': errors,
            'prev_username': username,
            'prev_email': email
        })

    # Si todas las validaciones pasan, se guarda el nuevo usuario en memoria
    USERS.append({
        'username': username,
        'email': email,
        'password': password
    })

    # Redirección a login informando éxito en el registro
    return redirect('/login/?registrado=1')


def login_view(request):
    """
    Vista de autenticación de usuarios y control de intentos fallidos.
    
    Dado GET: Muestra el formulario de inicio de sesión.
    Dado POST:
      - Si el usuario está bloqueado: muestra mensaje de bloqueo y detiene el flujo.
      - Si las credenciales fallan: incrementa intentos. Al 3er fallo bloquea la cuenta.
      - Si las credenciales coinciden y no está bloqueado: reinicia intentos y crea sesión.
    """
    # Si viene con parámetro de registro exitoso, preparamos mensaje informativo
    mensaje_exito = None
    if request.GET.get('registrado') == '1':
        mensaje_exito = "¡Usuario registrado con éxito! Ya puedes iniciar sesión."

    if request.method == 'GET':
        return render(request, 'accounts/login.html', {
            'mensaje_exito': mensaje_exito
        })

    # Procesamiento del formulario POST
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    # Validar campos vacíos básicos
    if not username or not password:
        return render(request, 'accounts/login.html', {
            'error_login': "Por favor ingresa usuario y contraseña.",
            'prev_username': username
        })

    # Verificar si el usuario ya se encuentra bloqueado en LOGIN_ATTEMPTS
    estado_usuario = LOGIN_ATTEMPTS.get(username, {'intentos': 0, 'bloqueado': False})

    if estado_usuario.get('bloqueado'):
        return render(request, 'accounts/login.html', {
            'error_login': "Clave bloqueada. Ha superado el máximo de intentos permitidos.",
            'bloqueado': True,
            'prev_username': username
        })

    # Buscar usuario y validar credenciales contra USERS
    usuario_encontrado = None
    for u in USERS:
        if u['username'] == username and u['password'] == password:
            usuario_encontrado = u
            break

    if usuario_encontrado:
        # Credenciales correctas:
        # 1. Reiniciar contador de intentos fallidos
        LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}

        # 2. Guardar el usuario en la sesión de Django (signed_cookies)
        request.session['username'] = usuario_encontrado['username']

        # 3. Redirigir a la pantalla de bienvenida
        return redirect('/bienvenida/')
    else:
        # Credenciales incorrectas: registrar e incrementar intento fallido
        if username not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[username] = {'intentos': 0, 'bloqueado': False}

        LOGIN_ATTEMPTS[username]['intentos'] += 1
        intentos = LOGIN_ATTEMPTS[username]['intentos']

        # Evaluar si se alcanzó el límite de 3 intentos
        if intentos >= 3:
            LOGIN_ATTEMPTS[username]['bloqueado'] = True
            mensaje_error = "Clave bloqueada. Ha superado el máximo de intentos permitidos."
            bloqueado = True
        else:
            mensaje_error = f"Usuario o contraseña incorrectos. Intento {intentos} de 3."
            bloqueado = False

        return render(request, 'accounts/login.html', {
            'error_login': mensaje_error,
            'bloqueado': bloqueado,
            'prev_username': username
        })


def welcome_view(request):
    """
    Vista protegida de bienvenida post-login.
    
    Dado que existe 'username' en request.session: muestra saludo personalizado.
    Dado que no hay sesión activa: redirige inmediatamente a /login/.
    """
    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    return render(request, 'accounts/welcome.html', {
        'username': username
    })


def logout_view(request):
    """
    Vista para cerrar la sesión del usuario y redirigir al login.
    """
    # request.session.flush() elimina la cookie y los datos de la sesión actual
    request.session.flush()
    return redirect('/login/')
